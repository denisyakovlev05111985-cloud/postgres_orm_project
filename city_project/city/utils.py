from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from .models import User as SAUser
from .database import SessionLocal

User = get_user_model()

def get_or_create_sa_user(django_user) -> SAUser:
    with SessionLocal() as db:
        sa_user = db.query(SAUser).filter(SAUser.username == django_user.username).first()
        if sa_user is None:
            sa_user = SAUser(
                username=django_user.username,
                email=django_user.email,
                password_hash="",
            )
            db.add(sa_user)
            db.commit()
            db.refresh(sa_user)
        return sa_user

def calculate_ban_until(duration: str) -> Optional[datetime]:
    now = datetime.utcnow()
    if duration == "day":
        return now + timedelta(days=1)
    elif duration == "week":
        return now + timedelta(weeks=1)
    elif duration == "month":
        return now + timedelta(days=30)
    elif duration == "forever":
        return None
    return None

def is_admin(user) -> bool:
    with SessionLocal() as db:
        sa_user = db.query(SAUser).filter(SAUser.username == user.username).first()
        if not sa_user:
            return False
        return sa_user.is_admin and not sa_user.is_currently_banned
