"""SQLAlchemy models for picscreenr."""

from sqlalchemy import Column, Integer, String, Float, LargeBinary, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Image(Base):
    __tablename__ = "images"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    caption = Column(String)
    tags = Column(String)
    persons = relationship("PersonImage", back_populates="image")

class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    face_embedding = Column(LargeBinary)
    feature_vector = Column(LargeBinary)
    images = relationship("PersonImage", back_populates="person")

class PersonImage(Base):
    __tablename__ = "person_images"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"))
    image_id = Column(Integer, ForeignKey("images.id"))
    confidence = Column(Float)

    person = relationship("Person", back_populates="images")
    image = relationship("Image", back_populates="persons")
