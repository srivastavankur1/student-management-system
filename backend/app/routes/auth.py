from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_connection
from app.utils.password import verify_password
from app.utils.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm= Depends()):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE email = %s;", (form_data.username,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()

    if not student or not verify_password(form_data.password, student['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": student["email"], "role": student["role"]})
    return {"access_token": access_token, "token_type": "bearer"}