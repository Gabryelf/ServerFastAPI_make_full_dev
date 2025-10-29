from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    from .crud import get_user_by_email
    print(f"🔐 Authenticating user: {email}")

    user = get_user_by_email(db, email)
    if not user:
        print(f"❌ User not found: {email}")
        return False

    print(f"✅ User found: {user.email}, checking password...")
    password_valid = verify_password(password, user.hashed_password)

    if not password_valid:
        print(f"❌ Invalid password for user: {email}")
        return False

    print(f"✅ Authentication successful for user: {email}")
    return user


def create_access_token(user):
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta

    to_encode = {"sub": str(user.id), "email": user.email, "role": user.role}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    print(f"🔑 Created access token for user: {user.email}, role: {user.role}")
    return {"access_token": encoded_jwt, "token_type": "bearer"}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    from .crud import get_user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print(f"🔍 Validating token...")
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
        email: str = payload.get("email")
        role: str = payload.get("role")

        print(f"📋 Token payload - user_id: {user_id}, email: {email}, role: {role}")

        if user_id is None:
            raise credentials_exception

        user = get_user(db, user_id=user_id)
        if user is None:
            print(f"❌ User not found in database: {user_id}")
            raise credentials_exception

        print(f"✅ User validated: {user.email}")
        return user

    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception
