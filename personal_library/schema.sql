-- Drop tables if they exist (order matters due to foreign keys)
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS readers;

-- Create tables
CREATE TABLE readers (
    reader_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    reader_number VARCHAR(50) UNIQUE NOT NULL,
    contact VARCHAR(100)
);

CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    publisher VARCHAR(100),
    publication_year INTEGER,
    category VARCHAR(50),
    total_stock INTEGER NOT NULL DEFAULT 0,
    available_stock INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT chk_available_stock CHECK (available_stock >= 0 AND available_stock <= total_stock)
);

CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(book_id) ON DELETE RESTRICT,
    reader_id INTEGER NOT NULL REFERENCES readers(reader_id) ON DELETE RESTRICT,
    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL
);

-- Create indexes
-- Primary key indexes are created automatically
-- Unique constraint on books.isbn and readers.reader_number also creates an index automatically

CREATE INDEX idx_books_title ON books(title);
-- For PostgreSQL, if you need efficient fuzzy search and have pg_trgm extension:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX idx_books_title_trgm ON books USING gin (title gin_trgm_ops);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_category ON books(category);

CREATE INDEX idx_readers_name ON readers(name);

CREATE INDEX idx_loans_book_id ON loans(book_id);
CREATE INDEX idx_loans_reader_id ON loans(reader_id);
CREATE INDEX idx_loans_due_date ON loans(due_date);
CREATE INDEX idx_loans_return_date ON loans(return_date);

-- (Optional) Create Views
CREATE OR REPLACE VIEW view_activeloans AS
SELECT
    L.loan_id,
    R.name AS reader_name,
    R.reader_number,
    B.title AS book_title,
    B.isbn,
    L.loan_date,
    L.due_date
FROM loans L
JOIN books B ON L.book_id = B.book_id
JOIN readers R ON L.reader_id = R.reader_id
WHERE L.return_date IS NULL;

CREATE OR REPLACE VIEW view_overdueloans AS
SELECT
    L.loan_id,
    R.name AS reader_name,
    R.reader_number,
    R.contact AS reader_contact,
    B.title AS book_title,
    B.isbn,
    L.loan_date,
    L.due_date
FROM loans L
JOIN books B ON L.book_id = B.book_id
JOIN readers R ON L.reader_id = R.reader_id
WHERE L.return_date IS NULL AND L.due_date < CURRENT_DATE;

-- (Optional) Insert some initial data
/*
INSERT INTO readers (name, reader_number, contact) VALUES
('张三', 'R001', '13800138000'),
('李四', 'R002', '13900139000');

INSERT INTO books (title, author, isbn, publisher, publication_year, category, total_stock, available_stock) VALUES
('Python编程从入门到实践', 'Eric Matthes', '9787115428028', '人民邮电出版社', 2016, '编程', 5, 5),
('三体', '刘慈欣', '9787536692930', '重庆出版社', 2008, '科幻', 3, 3),
('数据库系统概念', 'Abraham Silberschatz', '9787111671735', '机械工业出版社', 2020, '计算机', 2, 1);

-- Example loan (assuming book_id 3 and reader_id 1 exist)
-- INSERT INTO loans (book_id, reader_id, loan_date, due_date) VALUES (3, 1, '2025-04-01', '2025-05-01');
*/