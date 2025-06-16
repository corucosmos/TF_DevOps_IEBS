import pytest
from app.models import User

@pytest.fixture
def sample_user():
    return User(
        email="fixture@example.com",
        password="test123",
        first_name="Fixture",
        last_name="User"
    )