"""Security utilities for SMF Social v2."""
from cryptography.fernet import Fernet
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, ENCRYPTION_KEY

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token encryption
def get_fernet():
    """Get Fernet cipher instance."""
    # Ensure key is 32 bytes (Fernet requirement)
    key = ENCRYPTION_KEY[:32].encode()
    # Pad or truncate to exactly 32 bytes
    key = key.ljust(32, b'=')[:32]
    # Fernet requires URL-safe base64 encoded key
    import base64
    key = base64.urlsafe_b64encode(key)
    return Fernet(key)

def encrypt_token(plain_text: str) -> str:
    """Encrypt OAuth token for database storage."""
    f = get_fernet()
    return f.encrypt(plain_text.encode()).decode()

def decrypt_token(cipher_text: str) -> str:
    """Decrypt OAuth token from database."""
    f = get_fernet()
    return f.decrypt(cipher_text.encode()).decode()

def hash_password(password: str) -> str:
    """Hash password for database storage."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
