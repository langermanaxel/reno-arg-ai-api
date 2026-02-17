from passlib.context import CryptContext

# Configuramos el algoritmo de encriptación (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Convierte texto plano en un hash seguro."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la clave ingresada coincide con el hash guardado."""
    return pwd_context.verify(plain_password, hashed_password)