from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional, Literal
from datetime import datetime

class StudentCreate(BaseModel):
    role: Annotated[Literal['Admin','student'], Field(..., description='role of the user')]
    name: Annotated[str, Field(..., description='Name of the student')]
    email: Annotated[EmailStr, Field(..., description='Email of the student')]
    password: Annotated[str, Field(..., description='Password for the student')] 
    phone: Annotated[str, Field(..., description='Phone number of the student')]
    branch: Annotated[Literal['Btech', 'BCA', 'BBA'], Field(..., description='Branch in which student study')]

    

class StudentOut(BaseModel):
    student_id: Annotated[int, Field(..., description='ID of the student')]
    role: Annotated[Literal['Admin','student'], Field(..., description='role of the user')]
    name: Annotated[str, Field(..., description='Name of the student')]
    email: Annotated[EmailStr, Field(..., description='Email of the student')]
    phone: Annotated[str, Field(..., description='Phone number of the student')]
    branch: Annotated[Literal['Btech', 'BCA', 'BBA'], Field(..., description='branch in which student study')]
    created_at: Annotated[datetime, Field(..., description='Date when student was created')]

    class Config:
        orm_mode = True

    # class StudentUpdate(BaseModel):
    # name: Optional[Annotated[str, Field(description="Updated Name of student")]] 
#     email: Optional[Annotated[EmailStr, Field(description="Updated Email of the student")]]
#     password: Optional[Annotated[str, Field(description="Updated Password of student")]]
#     phone: Optional[Annotated[str, Field(description="Updated Phone number of student")]]

class StudentUpdate(BaseModel):
    role: Optional[Literal['Admin','Student']]= None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    branch: Optional[Literal['Btech', 'BCA', 'BBA']] = None