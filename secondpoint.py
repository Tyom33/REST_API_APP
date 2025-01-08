from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql+psycopg2://library_user:password123@localhost/library_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

class Book(Base):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String)
    publisher = Column(String)
    topic = Column(String)
    identifier = Column(String)

class Reader(Base):
    __tablename__ = "reader"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    passport_number = Column(String)
    is_active = Column(Boolean, default=True)

class Issue(Base):
    __tablename__ = "issue"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("book.id"))
    reader_id = Column(Integer, ForeignKey("reader.id"))
    issue_date = Column(Date, nullable=False)
    return_date = Column(Date)
    actual_return_date = Column(Date)

    book = relationship("Book")
    reader = relationship("Reader")

Base.metadata.create_all(bind=engine)

class BookCreate(BaseModel):
    title: str
    author: str = None
    publisher: str = None
    topic: str = None
    identifier: str = None

class BookRead(BaseModel):
    id: int
    title: str
    author: str
    publisher: str
    topic: str
    identifier: str

    class Config:
        orm_mode = True

@app.post("/books/", response_model=BookRead)
def create_book(book: BookCreate):
    db = SessionLocal()
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    db.close()
    return db_book

@app.get("/books/{book_id}", response_model=BookRead)
def read_book(book_id: int):
    db = SessionLocal()
    db_book = db.query(Book).filter(Book.id == book_id).first()
    db.close()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.put("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookCreate):
    db = SessionLocal()
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        db.close()
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book.dict().items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    db.close()
    return db_book

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    db = SessionLocal()
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        db.close()
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()
    db.close()
    return {"message": "Book deleted successfully"}
