"""Modelo de usuarios."""

from sqlalchemy import Column, String, Boolean, CheckConstraint
from app.models.core import Base, UUIDMixin, TimestampMixin

class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "usuarios"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False, index=True)
    
    __table_args__ = (
        CheckConstraint('length(username) >= 3', name='check_username_min_length'),
        CheckConstraint('email ~* \'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$\'', 
                       name='check_email_format'),
    )
