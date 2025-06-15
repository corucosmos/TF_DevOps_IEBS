from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection
from models import User
from schemas import UserCreate, UserResponse
import mysql.connector
import os
import logging
from pathlib import Path 

app = FastAPI()
current_directory = Path(__file__).parent

LOG_DIR = current_directory / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # Formato del log
file_handler = logging.FileHandler(LOG_DIR / "main.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Configuración CORS para permitir acceso desde cualquier frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_main(email: str, success: bool, action: str, ip: str = None):
    status = "SUCCESS" if success else "FAILED"
    message = f"{action} - Email: {email} - Status: {status}"
    if ip:
        message += f" - IP: {ip}"
    logger.info(message)

@app.post("/register/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, request: Request):
    db_user = User(user.email, user.password, user.first_name, user.last_name)

    try:
        connection = get_db_connection()
        if connection is None:
            log_main(user.email, False, "db_connection_failed", request.client.host)
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor()
        
        # Verificar si el usuario ya existe
        cursor.execute("SELECT email FROM users WHERE email = %s", (db_user.email,))
        if cursor.fetchone():
            log_main(user.email, False, "email_already_registered", request.client.host)
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Insertar nuevo usuario
        cursor.execute(
            "INSERT INTO users (email, password, first_name, last_name) VALUES (%s, %s, %s, %s)",
            (db_user.email, db_user.password, db_user.first_name, db_user.last_name)
        )
        connection.commit()
        log_main(user.email, True, "user_registered", request.client.host)

        return UserResponse(
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name
        )
        
    except mysql.connector.Error as err:
        log_main(user.email, False, "db_error", request.client.host)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")



    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.get("/users/{email}", response_model=UserResponse)
async def get_user(email: str, request: Request):
    try:
        connection = get_db_connection()
        if connection is None:
            log_main(email, False, "db_connection_failed", request.client.host)
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT email, first_name, last_name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            log_main(email, False, "user_not_found", request.client.host)
            raise HTTPException(status_code=404, detail="User not found")
        else:
            log_main(email, True, "user_search", request.client.host)

        return user
        
    except mysql.connector.Error as err:
        log_main(email, False, "db_error", request.client.host)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()