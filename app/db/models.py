from sqlalchemy import String, BigInteger, DateTime, Boolean, func, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from enum import Enum as PyEnum


class ModelName(str, PyEnum):
    FAST = "yolo26n_fast"
    ACCURATE = "yolo26l_accurate"


class UserInfo(Base):
    __tablename__ = "user_info"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    history: Mapped[list["History"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user_info.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    model_used: Mapped[str] = mapped_column(String(50), nullable=False)
    results_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["UserInfo"] = relationship(back_populates="history")