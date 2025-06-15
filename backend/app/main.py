from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_db_connection
from models import User
from schemas import UserCreate, UserResponse
import mysql.connector
import os
import logging
from pathlib import Path
from typing import List 

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

SECRET_KEY = os.getenv("SECRET_KEY") #"tu_super_secreto_aqui"  # Deberías usar una variable de entorno en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

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

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Obtener usuario de la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT email, first_name, last_name, is_admin FROM users WHERE email = %s",
            (email,)
        )
        user_data = cursor.fetchone()
        if user_data is None:
            raise credentials_exception
        
        return User(
            email=user_data['email'],
            password="",  # No necesitamos la contraseña aquí
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_admin=user_data['is_admin']
        )
    except JWTError:
        raise credentials_exception
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user


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
            "INSERT INTO users (email, password, first_name, last_name, is_admin) VALUES (%s, %s, %s, %s, %s)",
            (db_user.email, db_user.password, db_user.first_name, db_user.last_name, False)
        )
        connection.commit()
        log_main(user.email, True, "user_registered", request.client.host)

        return UserResponse(
            email=db_user.email,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            is_admin=False
        )
        
    except mysql.connector.Error as err:
        log_main(user.email, False, "db_error", request.client.host)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/login/")
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        connection = get_db_connection()
        if connection is None:
            log_main(form_data.username, False, "db_connection_failed", request.client.host)
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT email, password, first_name, last_name, is_admin FROM users WHERE email = %s",
            (form_data.username,)
        )
        user_data = cursor.fetchone()
        
        if not user_data:
            log_main(form_data.username, False, "login_failed", request.client.host)
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        user = User(
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_admin=user_data.get('is_admin', False) #user_data['is_admin']
        )
        
        if not user.verify_password(form_data.password):
            log_main(form_data.username, False, "login_failed", request.client.host)
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        access_token = create_access_token(
            data={"sub": user.email, "is_admin": user.is_admin}
        )
        
        log_main(form_data.username, True, "login_success", request.client.host)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "is_admin": user.is_admin
        }
        
    except mysql.connector.Error as err:
        log_main(form_data.username, False, "db_error", request.client.host)
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
        cursor.execute("SELECT email, first_name, last_name, is_admin FROM users WHERE email = %s", (email,))
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

@app.get("/admin/users/", response_model=List[UserResponse])
async def list_all_users(
    request: Request,
    current_user: User = Depends(get_current_admin)
):
    try:
        connection = get_db_connection()
        if connection is None:
            log_main(current_user.email, False, "db_connection_failed", request.client.host)
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT email, first_name, last_name, is_admin FROM users")
        users = cursor.fetchall()
        
        log_main(current_user.email, True, "admin_list_users", request.client.host)
        return users
        
    except mysql.connector.Error as err:
        log_main(current_user.email, False, "db_error", request.client.host)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()