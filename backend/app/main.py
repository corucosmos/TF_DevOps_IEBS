from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection
from models import User
from schemas import UserCreate, UserResponse
import mysql.connector

app = FastAPI()

# Configuración CORS para permitir acceso desde cualquier frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    db_user = User(user.email, user.password, user.first_name, user.last_name)
    
    try:
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT email FROM users WHERE email = %s", (db_user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Insertar nuevo usuario
        cursor.execute(
            "INSERT INTO users (email, password, first_name, last_name) VALUES (%s, %s, %s, %s)",
            (db_user.email, db_user.password, db_user.first_name, db_user.last_name)
        )
        connection.commit()
        
        return UserResponse(
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name
        )
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/users/{email}", response_model=UserResponse)
async def get_user(email: str):
    try:
        connection = get_db_connection()
        if connection is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT email, first_name, last_name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return user
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()