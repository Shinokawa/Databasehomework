import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, g, current_app
from . import db 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_default_fallback_secret_key_if_not_set')

db.init_app(app)

@app.cli.command('init-db')
def init_db_command():
    """清除现有数据并创建新表。"""
    try:
        with app.app_context():
            db.init_db_tables()
        click.echo('数据库已初始化。')
    except Exception as e:
        click.echo(f'数据库初始化失败: {e}')

def get_int_or_none(value_str):
    """尝试将字符串转换为整数，如果字符串为空或无效则返回 None。"""
    if value_str and value_str.strip():
        try:
            return int(value_str)
        except ValueError:
            return None
    return None

@app.route('/')
def index():
    """应用首页。"""
    return render_template('index.html')

@app.route('/books')
def list_books():
    """显示所有图书列表，支持搜索。"""
    search_term = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = "SELECT * FROM books"
    count_query = "SELECT COUNT(*) FROM books"
    args = []
    conditions = []

    if search_term:
        conditions.append("(title ILIKE %s OR author ILIKE %s OR isbn = %s)")
        args.extend([f'%{search_term}%', f'%{search_term}%', search_term])

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        count_query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY title LIMIT %s OFFSET %s"
    offset = (page - 1) * per_page
    args_paginated = args + [per_page, offset]

    try:
        books = db.query_db(query, args_paginated)
        total_books_row = db.query_db(count_query, args, one=True)
        total_books = total_books_row[0] if total_books_row else 0
        total_pages = (total_books + per_page - 1) // per_page
    except psycopg2.Error as e:
        flash(f'查询图书时发生错误: {e}', 'danger')
        books = []
        total_pages = 0
        page = 1

    return render_template('books/list.html',
                           books=books,
                           search_term=search_term,
                           current_page=page,
                           total_pages=total_pages)

@app.route('/books/new', methods=['GET', 'POST'])
def add_book():
    """添加新图书。"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publisher = request.form.get('publisher', '').strip() or None
        publication_year_str = request.form.get('publication_year', '').strip()
        category = request.form.get('category', '').strip() or None
        total_stock_str = request.form.get('total_stock', '0').strip()

        publication_year = get_int_or_none(publication_year_str)
        total_stock = get_int_or_none(total_stock_str) or 0
        available_stock = total_stock

        if not title or not author or not isbn:
            flash('书名、作者和 ISBN 为必填项。', 'danger')
        elif total_stock < 0:
            flash('总库存不能为负数。', 'danger')
        else:
            sql = """
                INSERT INTO books (title, author, isbn, publisher, publication_year, category, total_stock, available_stock)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING book_id;
            """
            try:
                db.query_db(sql, (title, author, isbn, publisher, publication_year, category, total_stock, available_stock), commit=True)
                flash('图书添加成功!', 'success')
                return redirect(url_for('list_books'))
            except psycopg2.IntegrityError as e:
                db.get_db().rollback()
                current_app.logger.error(f"添加图书失败 (ISBN冲突或约束违反): {e}")
                if 'books_isbn_key' in str(e).lower():
                    flash(f'添加失败: ISBN ({isbn}) 已存在。', 'danger')
                elif 'chk_available_stock' in str(e).lower():
                     flash('添加失败: 可用库存不能大于总库存或小于0。', 'danger')
                else:
                    flash(f'添加失败: 数据库约束冲突。 {e}', 'danger')
            except psycopg2.Error as e:
                db.get_db().rollback()
                current_app.logger.error(f"添加图书时发生数据库错误: {e}")
                flash(f'添加图书时发生错误: {e}', 'danger')
            except Exception as e:
                db.get_db().rollback()
                current_app.logger.error(f"添加图书时发生未知错误: {e}")
                flash(f'添加图书时发生未知错误: {e}', 'danger')

    return render_template('books/form.html', action_text='添加', book=None, form_action=url_for('add_book'))

@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    """编辑现有图书信息。"""
    book = db.query_db('SELECT * FROM books WHERE book_id = %s', [book_id], one=True)
    if not book:
        flash('未找到该图书。', 'warning')
        return redirect(url_for('list_books'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publisher = request.form.get('publisher', '').strip() or None
        publication_year_str = request.form.get('publication_year', '').strip()
        category = request.form.get('category', '').strip() or None
        total_stock_str = request.form.get('total_stock', '0').strip()
        available_stock_str = request.form.get('available_stock', '0').strip()

        publication_year = get_int_or_none(publication_year_str)
        total_stock = get_int_or_none(total_stock_str)
        available_stock = get_int_or_none(available_stock_str)

        if not title or not author or not isbn:
            flash('书名、作者和 ISBN 为必填项。', 'danger')
        elif total_stock is None or total_stock < 0:
            flash('总库存必须是一个非负整数。', 'danger')
        elif available_stock is None or available_stock < 0:
            flash('可借阅库存必须是一个非负整数。', 'danger')
        elif available_stock > total_stock:
            flash('可借阅库存不能大于总库存。', 'danger')
        else:
            sql = """
                UPDATE books SET title=%s, author=%s, isbn=%s, publisher=%s,
                               publication_year=%s, category=%s, total_stock=%s, available_stock=%s
                WHERE book_id=%s;
            """
            try:
                db.query_db(sql, (title, author, isbn, publisher, publication_year, category, total_stock, available_stock, book_id), commit=True)
                flash('图书信息更新成功!', 'success')
                return redirect(url_for('list_books'))
            except psycopg2.IntegrityError as e:
                db.get_db().rollback()
                current_app.logger.error(f"更新图书失败 (ISBN冲突或约束违反): {e}")
                if 'books_isbn_key' in str(e).lower():
                    flash(f'更新失败: ISBN ({isbn}) 与其他图书重复。', 'danger')
                elif 'chk_available_stock' in str(e).lower():
                     flash('更新失败: 可用库存不能大于总库存或小于0。', 'danger')
                else:
                    flash(f'更新失败: 数据库约束冲突。 {e}', 'danger')
            except psycopg2.Error as e:
                db.get_db().rollback()
                current_app.logger.error(f"更新图书时发生数据库错误: {e}")
                flash(f'更新图书时发生错误: {e}', 'danger')
            except Exception as e:
                db.get_db().rollback()
                current_app.logger.error(f"更新图书时发生未知错误: {e}")
                flash(f'更新图书时发生未知错误: {e}', 'danger')
        current_values = dict(request.form)
        current_values['book_id'] = book_id
        return render_template('books/form.html', action_text='更新', book=current_values, form_action=url_for('edit_book', book_id=book_id))

    return render_template('books/form.html', action_text='更新', book=book, form_action=url_for('edit_book', book_id=book_id))


@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    """删除图书。"""
    active_loans = db.query_db("SELECT 1 FROM loans WHERE book_id = %s AND return_date IS NULL LIMIT 1", [book_id], one=True)
    if active_loans:
        flash('无法删除该图书，尚有未归还的借阅记录。请先处理这些借阅。', 'danger')
    else:
        try:
            deleted_rows = db.query_db('DELETE FROM books WHERE book_id = %s', [book_id], commit=True)
            if deleted_rows > 0:
                flash('图书删除成功!', 'success')
            else:
                flash('未找到要删除的图书或已被删除。', 'warning')
        except psycopg2.IntegrityError as e:
            db.get_db().rollback()
            flash(f'删除图书失败: 数据库完整性约束冲突。 {e}', 'danger')
        except psycopg2.Error as e:
            db.get_db().rollback()
            flash(f'删除图书失败: {e}', 'danger')
        except Exception as e:
            db.get_db().rollback()
            flash(f'删除图书时发生未知错误: {e}', 'danger')
    return redirect(url_for('list_books'))

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """返回指定图书的详细信息（JSON 格式）。"""
    try:
        book = db.query_db("SELECT * FROM books WHERE book_id = %s", [book_id], one=True)
        if not book:
            return {"error": "Book not found"}, 404
        book_json = {
            "book_id": book["book_id"],
            "title": book["title"],
            "author": book["author"],
            "isbn": book["isbn"],
            "publisher": book["publisher"],
            "publication_year": book["publication_year"],
            "category": book["category"],
            "total_stock": book["total_stock"],
            "available_stock": book["available_stock"]
        }
        return book_json, 200
    except psycopg2.Error as e:
        current_app.logger.error(f"查询图书详情失败: {e}")
        return {"error": "Database error"}, 500

@app.route('/readers')
def list_readers():
    """显示所有读者列表。"""
    try:
        readers = db.query_db("SELECT * FROM readers ORDER BY name")
    except psycopg2.Error as e:
        flash(f'查询读者列表失败: {e}', 'danger')
        readers = []
    return render_template('readers/list.html', readers=readers)

@app.route('/readers/new', methods=['GET', 'POST'])
def add_reader():
    """添加新读者。"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        reader_number = request.form.get('reader_number', '').strip()
        contact = request.form.get('contact', '').strip() or None

        if not name or not reader_number:
            flash('姓名和读者编号为必填项。', 'danger')
        else:
            sql = "INSERT INTO readers (name, reader_number, contact) VALUES (%s, %s, %s) RETURNING reader_id;"
            try:
                db.query_db(sql, (name, reader_number, contact), commit=True)
                flash('读者添加成功!', 'success')
                return redirect(url_for('list_readers'))
            except psycopg2.IntegrityError as e:
                db.get_db().rollback()
                if 'readers_reader_number_key' in str(e).lower():
                    flash(f'添加失败: 读者编号 ({reader_number}) 已存在。', 'danger')
                else:
                    flash(f'添加失败: 数据库约束冲突。 {e}', 'danger')
            except psycopg2.Error as e:
                db.get_db().rollback()
                flash(f'添加读者时发生错误: {e}', 'danger')
        return render_template('readers/form.html', action_text='添加', reader=request.form, form_action=url_for('add_reader'))
    return render_template('readers/form.html', action_text='添加', reader=None, form_action=url_for('add_reader'))


@app.route('/readers/edit/<int:reader_id>', methods=['GET', 'POST'])
def edit_reader(reader_id):
    """编辑读者信息。"""
    reader = db.query_db("SELECT * FROM readers WHERE reader_id = %s", [reader_id], one=True)
    if not reader:
        flash('未找到该读者。', 'warning')
        return redirect(url_for('list_readers'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        reader_number = request.form.get('reader_number', '').strip()
        contact = request.form.get('contact', '').strip() or None

        if not name or not reader_number:
            flash('姓名和读者编号为必填项。', 'danger')
        else:
            sql = "UPDATE readers SET name=%s, reader_number=%s, contact=%s WHERE reader_id=%s;"
            try:
                db.query_db(sql, (name, reader_number, contact, reader_id), commit=True)
                flash('读者信息更新成功!', 'success')
                return redirect(url_for('list_readers'))
            except psycopg2.IntegrityError as e:
                db.get_db().rollback()
                if 'readers_reader_number_key' in str(e).lower():
                    flash(f'更新失败: 读者编号 ({reader_number}) 与其他读者重复。', 'danger')
                else:
                    flash(f'更新失败: 数据库约束冲突。 {e}', 'danger')
            except psycopg2.Error as e:
                db.get_db().rollback()
                flash(f'更新读者信息时发生错误: {e}', 'danger')
        current_values = dict(request.form)
        current_values['reader_id'] = reader_id
        return render_template('readers/form.html', action_text='更新', reader=current_values, form_action=url_for('edit_reader', reader_id=reader_id))

    return render_template('readers/form.html', action_text='更新', reader=reader, form_action=url_for('edit_reader', reader_id=reader_id))

@app.route('/readers/delete/<int:reader_id>', methods=['POST'])
def delete_reader(reader_id):
    """删除读者。"""
    active_loans = db.query_db("SELECT 1 FROM loans WHERE reader_id = %s AND return_date IS NULL LIMIT 1", [reader_id], one=True)
    if active_loans:
        flash('无法删除该读者，该读者尚有未归还的图书。', 'danger')
    else:
        try:
            deleted_rows = db.query_db('DELETE FROM readers WHERE reader_id = %s', [reader_id], commit=True)
            if deleted_rows > 0:
                flash('读者删除成功!', 'success')
            else:
                flash('未找到要删除的读者或已被删除。', 'warning')
        except psycopg2.Error as e:
            db.get_db().rollback()
            flash(f'删除读者失败: {e}', 'danger')
    return redirect(url_for('list_readers'))


@app.route('/loans/borrow', methods=['GET', 'POST'])
def borrow_book():
    """处理借书请求。"""
    if request.method == 'POST':
        book_id_str = request.form.get('book_id')
        reader_id_str = request.form.get('reader_id')
        due_date_str = request.form.get('due_date')

        book_id = get_int_or_none(book_id_str)
        reader_id = get_int_or_none(reader_id_str)

        if not book_id or not reader_id or not due_date_str:
            flash('图书、读者和应归还日期均为必填项。', 'danger')
        else:
            conn = db.get_db()
            cur = conn.cursor()
            try:
                cur.execute("SELECT available_stock FROM books WHERE book_id = %s FOR UPDATE;", (book_id,))
                book_stock_info = cur.fetchone()

                if book_stock_info and book_stock_info[0] > 0:
                    cur.execute("""
                        INSERT INTO loans (book_id, reader_id, due_date, loan_date)
                        VALUES (%s, %s, %s, CURRENT_DATE);
                    """, (book_id, reader_id, due_date_str))
                    conn.commit()
                    flash('借书成功!', 'success')
                    return redirect(url_for('list_active_loans'))
                elif book_stock_info and book_stock_info[0] <= 0:
                    conn.rollback()
                    flash('借书失败：该图书库存不足。', 'danger')
                else:
                    conn.rollback()
                    flash('借书失败：未找到该图书或图书信息有误。', 'danger')

            except psycopg2.Error as e:
                conn.rollback()
                if "chk_available_stock" in str(e).lower():
                    flash('借书失败：操作后库存将为负，请检查图书状态。', 'danger')
                else:
                    flash(f'借书操作失败: {e}', 'danger')
                current_app.logger.error(f"借书失败: {e}")
            except Exception as e:
                conn.rollback()
                flash(f'借书操作时发生未知错误: {e}', 'danger')
                current_app.logger.error(f"借书未知错误: {e}")
            finally:
                if cur:
                    cur.close()

    try:
        books_for_loan = db.query_db("SELECT book_id, title, author, available_stock FROM books WHERE available_stock > 0 ORDER BY title")
        readers_list = db.query_db("SELECT reader_id, name, reader_number FROM readers ORDER BY name")
    except psycopg2.Error as e:
        flash(f'加载借书表单数据失败: {e}', 'danger')
        books_for_loan = []
        readers_list = []

    return render_template('loans/borrow_form.html', books=books_for_loan, readers=readers_list)


@app.route('/loans/return/<int:loan_id>', methods=['POST'])
def return_book(loan_id):
    """处理还书请求。"""
    conn = db.get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT book_id FROM loans WHERE loan_id = %s AND return_date IS NULL FOR UPDATE;", (loan_id,))
        loan_info = cur.fetchone()

        if not loan_info:
            conn.rollback()
            flash('无效的借阅记录或图书已归还。', 'warning')
            return redirect(url_for('list_active_loans'))

        cur.execute("UPDATE loans SET return_date = CURRENT_DATE WHERE loan_id = %s;", (loan_id,))
        
        conn.commit()
        flash('还书成功!', 'success')
    except psycopg2.Error as e:
        conn.rollback()  
        if "chk_available_stock" in str(e).lower():
            flash('还书失败：操作后库存状态异常，请检查图书总库存。', 'danger')
        else:
            flash(f'还书操作失败: {e}', 'danger')
        current_app.logger.error(f"还书失败: {e}")
    except Exception as e:
        conn.rollback()
        flash(f'还书操作时发生未知错误: {e}', 'danger')
        current_app.logger.error(f"还书未知错误: {e}")
    finally:
        if cur:
            cur.close()
    return redirect(url_for('list_active_loans'))


@app.route('/loans/active')
def list_active_loans():
    """显示当前所有未归还的借阅记录。"""
    try:
        active_loans = db.query_db("SELECT * FROM view_activeloans ORDER BY due_date;")
    except psycopg2.Error as e:
        flash(f'查询当前借阅记录失败: {e}', 'danger')
        active_loans = []
    return render_template('loans/active_loans.html', loans=active_loans)


@app.route('/loans/overdue')
def list_overdue_loans():
    """显示所有已逾期未归还的借阅记录。"""
    try:
        overdue_loans = db.query_db("SELECT * FROM view_overdueloans ORDER BY due_date;")
    except psycopg2.Error as e:
        flash(f'查询逾期记录失败: {e}', 'danger')
        overdue_loans = []
    return render_template('loans/overdue_loans.html', loans=overdue_loans)

@app.route('/search/reader_loans/<int:reader_id>')
def reader_loan_history(reader_id):
    """查询某个读者的所有借阅记录 (包括已归还和未归还)。"""
    try:
        reader = db.query_db("SELECT * FROM readers WHERE reader_id = %s", [reader_id], one=True)
        if not reader:
            flash('未找到该读者。', 'warning')
            return redirect(url_for('list_readers'))

        sql = """
            SELECT l.loan_id, b.title AS book_title, b.isbn,
                   l.loan_date, l.due_date, l.return_date
            FROM loans l
            JOIN books b ON l.book_id = b.book_id
            WHERE l.reader_id = %s
            ORDER BY l.loan_date DESC;
        """
        loans = db.query_db(sql, [reader_id])
    except psycopg2.Error as e:
        flash(f'查询读者借阅历史失败: {e}', 'danger')
        loans = []
        if 'reader' not in locals():
             reader = None


    return render_template('loans/history.html',
                           loans=loans,
                           reader=reader,
                           history_type='reader')


@app.route('/search/book_loans/<int:book_id>')
def book_loan_history(book_id):
    """查询某本图书的所有被借阅记录。"""
    try:
        book = db.query_db("SELECT * FROM books WHERE book_id = %s", [book_id], one=True)
        if not book:
            flash('未找到该图书。', 'warning')
            return redirect(url_for('list_books'))

        sql = """
            SELECT l.loan_id, r.name AS reader_name, r.reader_number,
                   l.loan_date, l.due_date, l.return_date
            FROM loans l
            JOIN readers r ON l.reader_id = r.reader_id
            WHERE l.book_id = %s
            ORDER BY l.loan_date DESC;
        """
        loans = db.query_db(sql, [book_id])
    except psycopg2.Error as e:
        flash(f'查询图书借阅历史失败: {e}', 'danger')
        loans = []
        if 'book' not in locals():
            book = None

    return render_template('loans/history.html',
                           loans=loans,
                           book=book,
                           history_type='book')


if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_ENV') == 'development')
try:
    import click
except ImportError:
    pass
