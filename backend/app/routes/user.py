from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.services.auth import create_access_token, get_password_hash, verify_password, verify_token
from app.database.connection import get_db_connection
from datetime import timedelta

router = APIRouter(prefix="/api/v1/user", tags=["user"])

bearer_scheme = HTTPBearer()


# Models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    email: str


@router.post("/signup")
async def signup(user: UserRegister):
    """
    Register a new user

    Example:
    POST /api/v1/user/signup
    {
        "username": "john",
        "email": "john@example.com",
        "password": "secure123"
    }
    """
    if not user.username or len(user.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters"
        )

    if not user.password or len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (user.username, user.email)
    ).fetchone()
    if existing:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    hashed_password = get_password_hash(user.password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (user.username, user.email, hashed_password)
    )
    conn.commit()
    conn.close()

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=7)
    )

    return {
        "message": "User created successfully",
        "username": user.username,
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/login")
async def login(user: UserLogin):
    """
    Login user

    Example:
    POST /api/v1/user/login
    {
        "username": "john",
        "password": "secure123"
    }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    stored_user = cursor.execute(
        "SELECT username, password_hash FROM users WHERE username = ?",
        (user.username,)
    ).fetchone()
    conn.close()

    if not stored_user or not verify_password(user.password, stored_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


@router.get("/profile", response_model=UserResponse)
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Get current user profile.
    Send the JWT token in the header: Authorization: Bearer <token>
    """
    payload = verify_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT username, email FROM users WHERE username = ?",
        (payload["sub"],)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"username": row["username"], "email": row["email"]}
