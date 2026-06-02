from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import AuthResponse
from app.schemas.user import UserCreate, UserOut
from app.utils.exceptions import ConflictError, UnauthorizedError


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, payload: UserCreate) -> AuthResponse:
        if self.repo.get_by_email(payload.email):
            raise ConflictError("An account with this email already exists")

        user = User(
            name=payload.name.strip(),
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
        )
        user = self.repo.create(user)
        return self._build_auth_response(user)

    def login(self, email: str, password: str) -> AuthResponse:
        user = self.repo.get_by_email(email.lower())
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Incorrect email or password")
        return self._build_auth_response(user)

    def _build_auth_response(self, user: User) -> AuthResponse:
        token = create_access_token(subject=user.id)
        return AuthResponse(access_token=token, user=UserOut.model_validate(user))
