from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from app.models import Employee, EmployeeUpdate, EmployeeResponse, MessageResponse, DepartmentAvgSalary
from app.database import get_collection, connect_to_mongo, close_connection
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import os

# Create FastAPI app
app = FastAPI(
    title="Employee Management API",
    description="A REST API for managing employees with MongoDB",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        connect_to_mongo()
        print("🚀 Employee Management API started successfully!")
    except Exception as e:
        print(f"❌ Startup failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    close_connection()
    print("👋 Employee Management API shutdown")

@app.get("/")
def root():
    """API health check"""
    return {
        "message": "Employee Management API is running!",
        "docs": "/docs",
        "endpoints": {
            "create": "POST /employees",
            "get": "GET /employees/{employee_id}",
            "update": "PUT /employees/{employee_id}",
            "delete": "DELETE /employees/{employee_id}",
            "list": "GET /employees",
            "by_department": "GET /employees?department=Engineering",
            "avg_salary": "GET /employees/avg-salary",
            "search_skill": "GET /employees/search?skill=Python"
        }
    }

# 1. CREATE EMPLOYEE
@app.post("/employees", response_model=MessageResponse, status_code=201)
def create_employee(employee: Employee):
    """
    Create a new employee record
    
    - **employee_id**: Unique identifier (e.g., E123)
    - **name**: Employee full name
    - **department**: Department name (e.g., Engineering, HR)
    - **salary**: Employee salary (positive number)
    - **joining_date**: Date in YYYY-MM-DD format
    - **skills**: List of skills (e.g., ["Python", "MongoDB"])
    """
    try:
        collection = get_collection()
        
        # Convert employee to model_dump and handle date
        employee_dict = employee.model_dump()
        employee_dict["joining_date"] = employee_dict["joining_date"].isoformat()
        
        print(f"📝 Creating employee: {employee.employee_id}")
        
        # Insert into MongoDB
        result = collection.insert_one(employee_dict)
        
        if result.inserted_id:
            return MessageResponse(message=f"Employee {employee.employee_id} created successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to create employee")
            
    except DuplicateKeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Employee ID '{employee.employee_id}' already exists"
        )
    except Exception as e:
        print(f"❌ Error creating employee: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 6. AVERAGE SALARY BY DEPARTMENT
@app.get("/employees/avg-salary", response_model=List[DepartmentAvgSalary])
def get_average_salary_by_department():
    """
    Get average salary by department using MongoDB aggregation
    
    Returns list of departments with their average salaries
    """
    try:
        collection = get_collection()
        
        print("📊 Calculating average salary by department")
        
        # MongoDB aggregation pipeline
        pipeline = [
            {
                "$group": {
                    "_id": "$department",
                    "avg_salary": {"$avg": "$salary"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "department": "$_id",
                    "avg_salary": {"$round": ["$avg_salary", 2]}
                }
            },
            {
                "$sort": {"department": 1}
            }
        ]
        
        # Execute aggregation
        result = list(collection.aggregate(pipeline))
        
        print(f"📈 Found salary data for {len(result)} departments")
        return [DepartmentAvgSalary(**item) for item in result]
        
    except Exception as e:
        print(f"❌ Error calculating average salary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 7. SEARCH EMPLOYEES BY SKILL
@app.get("/employees/search", response_model=List[str])
def search_employees_by_skill(skill: str = Query(..., description="Skill to search for")):
    """
    Search employees who have the specified skill
    
    Returns employees with the given skill in their skills array
    """
    try:
        collection = get_collection()
        
        print(f"🔎 Searching employees with skill: {skill}")
        
        # MongoDB query to find skill in array
        query = {"skills": {"$in": [skill]}}
        
        # Find and sort by name
        cursor = collection.find(query).sort("name", 1)
        # employees = list(cursor)
        
        # cursor = collection.find(query, {"name": 1, "_id": 0}).sort("name", 1)
        docs = list(cursor)

        # Extract the name from each document
        names = [doc["name"] for doc in docs]
        
        
        
        print(f"🎯 Found {len(names)} employees with skill '{skill}'")
        return names
        
    except Exception as e:
        print(f"❌ Error searching employees: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# 2. GET EMPLOYEE BY ID
@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str):
    """
    Fetch employee details by employee_id
    
    Returns 404 if employee not foundx
    """
    try:
        collection = get_collection()
        
        print(f"🔍 Looking for employee: {employee_id}")
        
        # Find employee in MongoDB
        employee = collection.find_one({"employee_id": employee_id})
        
        if not employee:
            raise HTTPException(
                status_code=404,
                detail=f"Employee with ID '{employee_id}' not found"
            )
        
        # Remove MongoDB _id field and convert date
        employee.pop("_id", None)
        if isinstance(employee["joining_date"], str):
            employee["joining_date"] = datetime.fromisoformat(employee["joining_date"]).date()
        
        return EmployeeResponse(**employee)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting employee: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 3. UPDATE EMPLOYEE
@app.put("/employees/{employee_id}", response_model=MessageResponse)
def update_employee(employee_id: str, employee_update: EmployeeUpdate):
    """
    Update employee details (partial updates allowed)
    
    Only provided fields will be updated
    """
    try:
        collection = get_collection()
        
        # Check if employee exists
        existing = collection.find_one({"employee_id": employee_id})
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Employee with ID '{employee_id}' not found"
            )
        
        # Prepare update data (only non-None fields)
        update_data = {}
        for field, value in employee_update.model_dump().items():
            if value is not None:
                if field == "joining_date":
                    update_data[field] = value.isoformat()
                else:
                    update_data[field] = value
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields provided for update")
        
        print(f"✏️ Updating employee {employee_id} with: {update_data}")
        
        # Update in MongoDB
        result = collection.update_one(
            {"employee_id": employee_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return MessageResponse(message=f"Employee {employee_id} updated successfully")
        else:
            return MessageResponse(message="No changes made")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating employee: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 4. DELETE EMPLOYEE
@app.delete("/employees/{employee_id}", response_model=MessageResponse)
def delete_employee(employee_id: str):
    """
    Delete employee record
    
    Returns success/failure message
    """
    try:
        collection = get_collection()
        
        print(f"🗑️ Deleting employee: {employee_id}")
        
        # Delete from MongoDB
        result = collection.delete_one({"employee_id": employee_id})
        
        if result.deleted_count > 0:
            return MessageResponse(message=f"Employee {employee_id} deleted successfully")
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Employee with ID '{employee_id}' not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting employee: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# 5. LIST EMPLOYEES BY DEPARTMENT
@app.get("/employees", response_model=List[EmployeeResponse])
def list_employees(
    department: Optional[str] = Query(None, description="Filter by department"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    List employees with optional department filter and pagination
    
    Results sorted by joining_date (newest first)
    """
    try:
        collection = get_collection()
        
        # Build query
        query = {}
        if department:
            query["department"] = department
            print(f"📋 Listing employees in department: {department}")
        else:
            print("📋 Listing all employees")
        
        # Calculate skip for pagination
        skip = (page - 1) * limit
        
        cursor = collection.find(query).skip(skip).limit(limit)
        employees = list(cursor)

        # Sort by parsing ISO date, then convert to DD/MM/YYYY
        for emp in employees:
            if isinstance(emp["joining_date"], str):               
                emp["joining_date"] = datetime.fromisoformat(emp["joining_date"]).date()
                
        employees_sorted = sorted(
        employees,
        key=lambda emp: emp["joining_date"],
        reverse=False
        )

        return employees_sorted
        
    except Exception as e:
        print(f"❌ Error listing employees: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
