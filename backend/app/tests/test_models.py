import pytest
from app.models import User

def test_password_hashing():
    """Verifica que el hashing de contraseñas funcione correctamente"""
    # 1. Crear usuario con contraseña en texto plano
    test_user = User(
        email="test@example.com",
        password="secret",  # Contraseña sin hashear
        first_name="Test",
        last_name="User"
    )
    
    # 2. Verificaciones
    assert test_user.password != "secret", "La contraseña no fue hasheada"
    assert test_user.password.startswith("$2b$"), "El hash no es BCrypt"
    assert test_user.verify_password("secret") is True, "Verificación correcta falló"
    assert test_user.verify_password("wrongpass") is False, "Verificación incorrecta pasó"

def test_user_creation(sample_user):  # Usa el fixture
    assert sample_user.email == "fixture@example.com"
    assert isinstance(sample_user.password, str)

def test_password_hashing_edge_cases():
    # Contraseña vacía
    user = User(email="empty@test.com", password="", first_name="Empty", last_name="Pass")
    assert user.verify_password("") is True
    
    # Contraseña muy larga
    long_pass = "a" * 1000
    user = User(email="long@test.com", password=long_pass, first_name="Long", last_name="Pass")
    assert user.verify_password(long_pass) is True