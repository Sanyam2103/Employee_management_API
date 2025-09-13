from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Employee(BaseModel):
    """Employee model for creating new employees"""
    employee_id: str
    name: str
    department: str
    salary: float
    joining_date: date
    skills: List[str]
    
    class Config:
        # Example for API documentation
        schema_extra = {
            "example": {
                "employee_id": "E123",
                "name": "John Doe",
                "department": "Engineering",
                "salary": 75000,
                "joining_date": "2023-01-15",
                "skills": ["Python", "MongoDB", "APIs"]
            }
        }

class EmployeeUpdate(BaseModel):
    """Model for updating employee - all fields optional"""
    name: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = None
    joining_date: Optional[date] = None
    skills: Optional[List[str]] = None

class EmployeeResponse(BaseModel):
    """Model for employee responses"""
    employee_id: str
    name: str
    department: str
    salary: float
    joining_date: date
    skills: List[str]

class MessageResponse(BaseModel):
    """Standard response model"""
    message: str

class DepartmentAvgSalary(BaseModel):
    """Model for department average salary"""
    department: str
    avg_salary: float
