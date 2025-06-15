from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    def __init__(self, email: str, password: str, first_name: str, last_name: str):
        self.email = email
        self.password = self.get_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin  # Nuevo campo

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.password)