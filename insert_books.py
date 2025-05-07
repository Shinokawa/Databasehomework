import os
import psycopg2
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中获取 DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

# SQL 脚本
clear_sql = """
TRUNCATE TABLE loans, books, readers RESTART IDENTITY CASCADE;
"""

books = [
    {"title": "Python编程从入门到实践", "author": "Eric Matthes", "isbn": "9787115428028", "publisher": "人民邮电出版社", "publication_year": 2016, "category": "编程", "total_stock": 10, "available_stock": 10},
    {"title": "三体", "author": "刘慈欣", "isbn": "9787536692930", "publisher": "重庆出版社", "publication_year": 2008, "category": "科幻", "total_stock": 5, "available_stock": 5},
    {"title": "数据库系统概念", "author": "Abraham Silberschatz", "isbn": "9787111671735", "publisher": "机械工业出版社", "publication_year": 2020, "category": "计算机", "total_stock": 8, "available_stock": 8},
    {"title": "深入理解计算机系统", "author": "Randal E. Bryant", "isbn": "9787111544930", "publisher": "机械工业出版社", "publication_year": 2015, "category": "计算机", "total_stock": 6, "available_stock": 6},
    {"title": "算法导论", "author": "Thomas H. Cormen", "isbn": "9787111187779", "publisher": "机械工业出版社", "publication_year": 2013, "category": "计算机", "total_stock": 7, "available_stock": 7},
    {"title": "Java核心技术", "author": "Cay S. Horstmann", "isbn": "9787111624946", "publisher": "机械工业出版社", "publication_year": 2019, "category": "编程", "total_stock": 10, "available_stock": 10},
    {"title": "C程序设计语言", "author": "Brian W. Kernighan", "isbn": "9787111128062", "publisher": "机械工业出版社", "publication_year": 1988, "category": "编程", "total_stock": 5, "available_stock": 5},
    {"title": "人工智能：一种现代方法", "author": "Stuart Russell", "isbn": "9787111128063", "publisher": "机械工业出版社", "publication_year": 2020, "category": "人工智能", "total_stock": 6, "available_stock": 6},
    {"title": "机器学习", "author": "周志华", "isbn": "9787111128064", "publisher": "清华大学出版社", "publication_year": 2016, "category": "人工智能", "total_stock": 8, "available_stock": 8},
    {"title": "深度学习", "author": "Ian Goodfellow", "isbn": "9787111128065", "publisher": "人民邮电出版社", "publication_year": 2017, "category": "人工智能", "total_stock": 7, "available_stock": 7},
    {"title": "操作系统概念", "author": "Abraham Silberschatz", "isbn": "9787111128066", "publisher": "机械工业出版社", "publication_year": 2018, "category": "计算机", "total_stock": 9, "available_stock": 9},
    {"title": "计算机网络", "author": "Andrew S. Tanenbaum", "isbn": "9787111128067", "publisher": "清华大学出版社", "publication_year": 2019, "category": "计算机", "total_stock": 10, "available_stock": 10},
    {"title": "编译原理", "author": "Alfred V. Aho", "isbn": "9787111128068", "publisher": "机械工业出版社", "publication_year": 2007, "category": "计算机", "total_stock": 6, "available_stock": 6},
    {"title": "数据结构与算法分析", "author": "Mark Allen Weiss", "isbn": "9787111128069", "publisher": "机械工业出版社", "publication_year": 2013, "category": "计算机", "total_stock": 8, "available_stock": 8},
    {"title": "计算机组成与设计", "author": "David A. Patterson", "isbn": "9787111128070", "publisher": "机械工业出版社", "publication_year": 2014, "category": "计算机", "total_stock": 7, "available_stock": 7},
    {"title": "现代操作系统", "author": "Andrew S. Tanenbaum", "isbn": "9787111128071", "publisher": "清华大学出版社", "publication_year": 2015, "category": "计算机", "total_stock": 9, "available_stock": 9},
    {"title": "Python数据科学手册", "author": "Jake VanderPlas", "isbn": "9787111128072", "publisher": "人民邮电出版社", "publication_year": 2017, "category": "数据科学", "total_stock": 10, "available_stock": 10},
    {"title": "统计学习方法", "author": "李航", "isbn": "9787111128073", "publisher": "清华大学出版社", "publication_year": 2012, "category": "人工智能", "total_stock": 8, "available_stock": 8},
    {"title": "数据挖掘导论", "author": "Pang-Ning Tan", "isbn": "9787111128074", "publisher": "机械工业出版社", "publication_year": 2018, "category": "数据科学", "total_stock": 7, "available_stock": 7},
    {"title": "大数据时代", "author": "Viktor Mayer-Schönberger", "isbn": "9787111128075", "publisher": "浙江人民出版社", "publication_year": 2013, "category": "数据科学", "total_stock": 6, "available_stock": 6}
]

readers = [
    {"name": "张三", "reader_number": "R001", "contact": "123456789"},
    {"name": "李四", "reader_number": "R002", "contact": "987654321"},
    {"name": "王五", "reader_number": "R003", "contact": "456789123"},
    {"name": "赵六", "reader_number": "R004", "contact": "789123456"},
    {"name": "孙七", "reader_number": "R005", "contact": "321654987"}
]

loans = [
    {"book_id": 1, "reader_id": 1, "due_date": "2023-12-31"},
    {"book_id": 2, "reader_id": 2, "due_date": "2023-12-31"},
    {"book_id": 3, "reader_id": 3, "due_date": "2023-12-31"},
    {"book_id": 4, "reader_id": 4, "due_date": "2023-12-31"},
    {"book_id": 5, "reader_id": 5, "due_date": "2023-12-31"}
]

# 插入数据的 SQL 语句
insert_book_sql = """
INSERT INTO books (title, author, isbn, publisher, publication_year, category, total_stock, available_stock)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
"""

insert_reader_sql = """
INSERT INTO readers (name, reader_number, contact)
VALUES (%s, %s, %s);
"""

insert_loan_sql = """
INSERT INTO loans (book_id, reader_id, due_date, loan_date)
VALUES (%s, %s, %s, CURRENT_DATE);
"""

def clear_and_insert_data():
    try:
        # 连接到数据库
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # 清空数据库
        cur.execute(clear_sql)

        # 插入书籍数据
        for book in books:
            cur.execute(insert_book_sql, (
                book["title"],
                book["author"],
                book["isbn"],
                book["publisher"],
                book["publication_year"],
                book["category"],
                book["total_stock"],
                book["total_stock"]  # 初始时，available_stock 等于 total_stock
            ))

        # 插入读者数据
        for reader in readers:
            cur.execute(insert_reader_sql, (
                reader["name"],
                reader["reader_number"],
                reader["contact"]
            ))

        # 插入借阅记录
        for loan in loans:
            cur.execute(insert_loan_sql, (
                loan["book_id"],
                loan["reader_id"],
                loan["due_date"]
            ))

        # 更新每本书的 available_stock
        cur.execute("""
            UPDATE books
            SET available_stock = total_stock - (
                SELECT COUNT(*)
                FROM loans
                WHERE books.book_id = loans.book_id AND loans.return_date IS NULL
            );
        """)

        # 提交事务
        conn.commit()
        print("数据已成功插入！")

    except psycopg2.Error as e:
        print(f"插入数据时发生错误: {e}")
        if conn:
            conn.rollback()
    finally:
        # 关闭数据库连接
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    clear_and_insert_data()