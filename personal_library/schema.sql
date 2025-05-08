DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS readers CASCADE;

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


CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_category ON books(category);

CREATE INDEX idx_readers_name ON readers(name);

CREATE INDEX idx_loans_book_id ON loans(book_id);
CREATE INDEX idx_loans_reader_id ON loans(reader_id);
CREATE INDEX idx_loans_due_date ON loans(due_date);
CREATE INDEX idx_loans_return_date ON loans(return_date);

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

CREATE OR REPLACE FUNCTION fn_decrement_stock_on_borrow()
RETURNS TRIGGER AS $$
BEGIN

    IF NEW.return_date IS NULL THEN
        UPDATE books
        SET available_stock = available_stock - 1
        WHERE book_id = NEW.book_id;

    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_decrement_stock_on_borrow
AFTER INSERT ON loans
FOR EACH ROW
EXECUTE FUNCTION fn_decrement_stock_on_borrow();

CREATE OR REPLACE FUNCTION fn_update_stock_on_loan_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.return_date IS NULL AND NEW.return_date IS NOT NULL THEN
        UPDATE books
        SET available_stock = available_stock + 1
        WHERE book_id = NEW.book_id; 
    ELSIF OLD.return_date IS NOT NULL AND NEW.return_date IS NULL THEN
        UPDATE books
        SET available_stock = available_stock - 1
        WHERE book_id = NEW.book_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_stock_on_loan_change
AFTER UPDATE OF return_date ON loans 
FOR EACH ROW
EXECUTE FUNCTION fn_update_stock_on_loan_change();

CREATE OR REPLACE FUNCTION fn_increment_stock_on_loan_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.return_date IS NULL THEN
        UPDATE books
        SET available_stock = available_stock + 1
        WHERE book_id = OLD.book_id;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_stock_on_loan_delete
AFTER DELETE ON loans
FOR EACH ROW
EXECUTE FUNCTION fn_increment_stock_on_loan_delete();
