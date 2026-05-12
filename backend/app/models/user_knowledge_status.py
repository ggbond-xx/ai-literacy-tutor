from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.mysql import Base


class UserKnowledgeStatus(Base):
    __tablename__ = "user_knowledge_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    concept_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    update_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
