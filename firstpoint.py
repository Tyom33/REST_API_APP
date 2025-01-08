import psycopg2
from psycopg2 import sql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Конфигурация базы данных
DB_NAME = "postgres"
DB_USER = "user5447"
DB_PASSWORD = "KcgcUFgxx5KxC"
DB_HOST = "83.149.198.142"
DB_PORT = "5432"

NEW_DB_NAME = "library_db"
NEW_USER = "library_user"
NEW_PASSWORD = "password123"

app = FastAPI()

class Book(BaseModel):
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    topic: Optional[str] = None
    identifier: Optional[str] = None

class Reader(BaseModel):
    full_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    passport_number: Optional[str] = None
    is_active: Optional[bool] = True

def create_database_and_user():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(NEW_DB_NAME)))
        cursor.execute(
            sql.SQL("CREATE USER {} WITH PASSWORD %s;").format(sql.Identifier(NEW_USER)),
            [NEW_PASSWORD]
        )
        cursor.execute(
            sql.SQL("ALTER DATABASE {} OWNER TO {};").format(
                sql.Identifier(NEW_DB_NAME),
                sql.Identifier(NEW_USER)
            )
        )

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка: {e}")

def create_tables():
    try:
        conn = psycopg2.connect(
            dbname=NEW_DB_NAME,
            user=NEW_USER,
            password=NEW_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE book (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255),
                publisher VARCHAR(255),
                topic VARCHAR(255),
                identifier VARCHAR(100)
            );
        """)

        cursor.execute("""
            CREATE TABLE reader (
                id SERIAL PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                address TEXT,
                phone VARCHAR(20),
                passport_number VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE
            );
        """)

        cursor.execute("""
            CREATE TABLE issue (
                id SERIAL PRIMARY KEY,
                book_id INT REFERENCES book(id),
                reader_id INT REFERENCES reader(id),
                issue_date DATE NOT NULL,
                return_date DATE,
                actual_return_date DATE
            );
        """)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка: {e}")

@app.on_event("startup")
def startup_db():
    create_database_and_user()
    create_tables()

@app.get("/books/", response_model=List[Book])
def get_books():
    try:
        conn = psycopg2.connect(
            dbname=NEW_DB_NAME,
            user=NEW_USER,
            password=NEW_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT title, author, publisher, topic, identifier FROM book;")
        books = cursor.fetchall()
        conn.close()
        return [
            Book(title=book[0], author=book[1], publisher=book[2], topic=book[3], identifier=book[4])
            for book in books
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {e}")

@app.post("/books/", response_model=Book)
def add_book(book: Book):
    try:
        conn = psycopg2.connect(
            dbname=NEW_DB_NAME,
            user=NEW_USER,
            password=NEW_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO book (title, author, publisher, topic, identifier)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """,
            (book.title, book.author, book.publisher, book.topic, book.identifier)
        )
        book_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return {**book.dict(), "id": book_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {e}")

@app.post("/readers/", response_model=Reader)
def add_reader(reader: Reader):
    try:
        conn = psycopg2.connect(
            dbname=NEW_DB_NAME,
            user=NEW_USER,
            password=NEW_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reader (full_name, address, phone, passport_number, is_active)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """,
            (reader.full_name, reader.address, reader.phone, reader.passport_number, reader.is_active)
        )
        reader_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return {**reader.dict(), "id": reader_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {e}")

if __name__ == "__main__":
    create_database_and_user()
    create_tables()
