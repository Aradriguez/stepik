from sqlalchemy import Boolean, Integer, String, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from stepik.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    comment: Mapped[str | None] = mapped_column(nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now)
    grade: Mapped[int] = mapped_column(Integer, CheckConstraint("grade BETWEEN 1 AND 5"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)



