import enum

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    Time,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PetStatus(enum.Enum):
    lost = "lost"
    found = "found"
    returned = "returned"
    closed = "closed"


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="pets")

    type = Column(String(50), nullable=False)
    breed = Column(String(100), nullable=True)
    name = Column(String(255), nullable=True)
    color = Column(String(100), nullable=False)
    sex = Column(String(10), nullable=False)
    age = Column(String(50), nullable=True)
    chip_number = Column(String(100), nullable=True)
    brand_number = Column(String(100), nullable=True)

    found_date = Column(Date, nullable=False)
    found_time = Column(Time, nullable=False)
    address = Column(String(255), nullable=False)

    description = Column(Text, nullable=False)

    photo_url = Column(String(500), nullable=True)

    status = Column(Enum(PetStatus, name="pet_status"), nullable=False, default=PetStatus.lost)
    embedding = Column(ARRAY(Float).with_variant(JSON, "sqlite"), nullable=True)
    attachments = relationship(
        "PetAttachment",
        back_populates="pet",
        cascade="all, delete-orphan",
    )


class PetAttachment(Base):
    __tablename__ = "pet_attachments"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    storage_key = Column(String(255), nullable=False, unique=True, index=True)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    is_image = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    pet = relationship("Pet", back_populates="attachments")
