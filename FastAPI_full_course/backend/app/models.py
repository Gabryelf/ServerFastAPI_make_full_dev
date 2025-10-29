from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from .config import settings

# For MySQL compatibility, we'll use JSON instead of ARRAY
if settings.DATABASE_TYPE == 'mysql':
    from sqlalchemy import JSON


    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        email = Column(String(255), unique=True, index=True)
        hashed_password = Column(String(255))
        full_name = Column(String(255))
        role = Column(String(50), default="user")  # guest, user, admin

        products = relationship("Product", back_populates="owner")


    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(255), index=True)
        description = Column(Text)
        owner_id = Column(Integer, ForeignKey("users.id"))
        # For MySQL, store as JSON
        image_paths = Column(JSON, default=[])
        video_paths = Column(JSON, default=[])

        owner = relationship("User", back_populates="products")

else:
    from sqlalchemy.dialects.postgresql import ARRAY


    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        email = Column(String(255), unique=True, index=True)
        hashed_password = Column(String(255))
        full_name = Column(String(255))
        role = Column(String(50), default="user")  # guest, user, admin

        products = relationship("Product", back_populates="owner")


    class Product(Base):
        __tablename__ = "products"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String(255), index=True)
        description = Column(Text)
        owner_id = Column(Integer, ForeignKey("users.id"))
        # For PostgreSQL, use native ARRAY
        image_paths = Column(ARRAY(String), default=[])
        video_paths = Column(ARRAY(String), default=[])

        owner = relationship("User", back_populates="products")