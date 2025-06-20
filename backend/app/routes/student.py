from fastapi import APIRouter, HTTPException, status, UploadFile, File
import tempfile
import shutil
from app.routes.summarizer import summarize_file
from app.models.student_model import StudentCreate, StudentOut, StudentUpdate
from app.database import get_connection
import psycopg2
import psycopg2.errors
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from fastapi import Body
from app.utils.password import hash_password
from fastapi import Depends
from app.dependency import get_current_user, require_admin



router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/secure", dependencies=[Depends(get_current_user)])
def secure_route():
    return {"message": "You are authorized!"}

# Response model
class StudentCreateResponse(BaseModel):
    message: str
    student_id: int

@router.get("/me", response_model=StudentOut)
def get_my_profile(user: dict = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM students WHERE email = %s;", (user['sub'],))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    finally:
        cursor.close()
        conn.close()

@router.post("/summarizer", dependencies=[Depends(get_current_user)])
async def summarize_document(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        summary = summarize_file(tmp_path)
        return {"summary": summary}
    except Exception as e:
        return {"error": str(e)}

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=StudentCreateResponse, dependencies=[Depends(require_admin)])
def create_student(student: StudentCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        insert_query = """
        INSERT INTO students (name, email, password, phone, role, branch)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING student_id;
        """
        cursor.execute(insert_query, (
            student.name,
            student.email,
            hash_password(student.password),  
            student.phone,
            student.role,
            student.branch
        ))
        student_id = cursor.fetchone()["student_id"]
        conn.commit()

        return {"message": "Student created successfully", "student_id": student_id}

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Email already exists.")

    except Exception as e:
        conn.rollback()
        print("Error while inserting student:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))

    finally:
        cursor.close()
        conn.close()

#@router.get('/', response_model=list[StudentOut])
@router.get('/',dependencies=[Depends(require_admin)])
def get_all_students():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT * FROM students WHERE role = 'student';")
        records = cursor.fetchall()
        return records 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        conn.close()


@router.get('/{student_id}', response_model=StudentOut, dependencies=[Depends(require_admin)])
def get_by_student_id(student_id: int):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        query = "select * from students where student_id = %s;"
        cursor.execute(query,(student_id,))
        student = cursor.fetchone()

        if not student:
            raise HTTPException(status_code=404, detail='Student not found !')
        
        return student
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cursor.close()
        conn.close()


@router.delete("/{student_id}", status_code=200, dependencies=[Depends(require_admin)])
def delete_student(student_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # First check if the student exists
        cursor.execute("SELECT * FROM students WHERE student_id = %s;", (student_id,))
        student = cursor.fetchone()

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # Proceed to delete
        cursor.execute("DELETE FROM students WHERE student_id = %s;", (student_id,))
        conn.commit()

        return {"message": f"Student with ID {student_id} deleted successfully."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

@router.put("/{student_id}", status_code=200, dependencies=[Depends(require_admin)])
def update_student(student_id: int, student: StudentUpdate = Body(...)):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if student exists
        cursor.execute("SELECT * FROM students WHERE student_id = %s;", (student_id,))
        existing = cursor.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Student not found")

        # Update only the provided fields
        update_fields = []
        update_values = []

        if student.name:
            update_fields.append("name = %s")
            update_values.append(student.name)
        if student.password:
            update_fields.append("password = %s")
            update_values.append(student.password)
        if student.email:
            update_fields.append("email = %s")
            update_values.append(student.email)
        if student.phone:
            update_fields.append("phone = %s")
            update_values.append(student.phone)
        if student.branch:
            update_fields.append("branch = %s")
            update_values.append(student.branch)


        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        update_query = f"UPDATE students SET {', '.join(update_fields)} WHERE student_id = %s;"
        update_values.append(student_id)

        cursor.execute(update_query, tuple(update_values))
        conn.commit()

        return {"message": f"Student ID {student_id} updated successfully."}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

