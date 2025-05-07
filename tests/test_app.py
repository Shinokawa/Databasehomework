import pytest
from personal_library.app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- 首页测试 ---
def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert "欢迎来到个人图书管理系统".encode() in response.data

# --- 图书管理测试 ---
def test_add_book(client):
    response = client.post('/books/new', data={
        'title': '测试书籍1',
        'author': '测试作者1',
        'isbn': 'unique_isbn_1',
        'publisher': '测试出版社1',
        'publication_year': '2023',
        'category': '测试分类1',
        'total_stock': '5'
    })
    assert response.status_code == 302  # 重定向到图书列表页面

def test_add_book_duplicate_isbn(client):
    # 添加重复 ISBN 的书籍
    client.post('/books/new', data={
        'title': '测试书籍1',
        'author': '测试作者1',
        'isbn': 'unique_isbn_2',
        'publisher': '测试出版社1',
        'publication_year': '2023',
        'category': '测试分类1',
        'total_stock': '5'
    })
    response = client.post('/books/new', data={
        'title': '测试书籍2',
        'author': '测试作者2',
        'isbn': 'unique_isbn_2',  # 重复的 ISBN
        'publisher': '测试出版社2',
        'publication_year': '2023',
        'category': '测试分类2',
        'total_stock': '5'
    })
    assert response.status_code == 200
    assert b"ISBN" in response.data  # 检查是否提示 ISBN 冲突

def test_edit_book(client):
    # 添加一本书
    client.post('/books/new', data={
        'title': '测试书籍',
        'author': '测试作者',
        'isbn': 'unique_isbn_3',
        'publisher': '测试出版社',
        'publication_year': '2023',
        'category': '测试分类',
        'total_stock': '5'
    })
    # 编辑这本书
    response = client.post('/books/edit/1', data={
        'title': '修改后的书籍',
        'author': '修改后的作者',
        'isbn': 'unique_isbn_3',
        'publisher': '修改后的出版社',
        'publication_year': '2024',
        'category': '修改后的分类',
        'total_stock': '10',
        'available_stock': '10'
    })
    assert response.status_code == 302  # 重定向到图书列表页面

# --- 借阅管理测试 ---
def test_borrow_book(client):
    # 添加一本书和一个读者
    client.post('/books/new', data={
        'title': '测试书籍',
        'author': '测试作者',
        'isbn': 'unique_isbn_4',
        'publisher': '测试出版社',
        'publication_year': '2023',
        'category': '测试分类',
        'total_stock': '5'
    })
    client.post('/readers/new', data={
        'name': '测试读者',
        'reader_number': 'unique_reader_1',
        'contact': '123456789'
    })
    # 借书
    response = client.post('/loans/borrow', data={
        'book_id': '1',
        'reader_id': '1',
        'due_date': '2023-12-31'
    })
    assert response.status_code == 302  # 重定向到当前借阅记录页面

    # 检查库存是否减少
    book_response = client.get('/books/1')
    book_data = json.loads(book_response.data)  # 解析 JSON 数据
    assert book_data["available_stock"] == 4  # 检查 available_stock 的值

def test_return_book(client):
    # 借书
    client.post('/loans/borrow', data={
        'book_id': '1',
        'reader_id': '1',
        'due_date': '2023-12-31'
    })
    # 还书
    response = client.post('/loans/return/1')
    assert response.status_code == 302  # 重定向到当前借阅记录页面

# --- 综合查询测试 ---
def test_reader_loan_history(client):
    # 添加读者和借阅记录
    client.post('/readers/new', data={
        'name': '测试读者',
        'reader_number': 'unique_reader_2',
        'contact': '123456789'
    })
    client.post('/books/new', data={
        'title': '测试书籍',
        'author': '测试作者',
        'isbn': 'unique_isbn_5',
        'publisher': '测试出版社',
        'publication_year': '2023',
        'category': '测试分类',
        'total_stock': '5'
    })
    client.post('/loans/borrow', data={
        'book_id': '1',
        'reader_id': '1',
        'due_date': '2023-12-31'
    })
    # 测试借阅历史
    response = client.get('/search/reader_loans/1')
    assert response.status_code == 200
    assert '<h2>借阅历史</h2>' in response.data.decode("utf-8")  # 检查标题是否正确
    assert '测试书籍' in response.data.decode("utf-8")  # 检查借阅记录是否正确显示

def test_book_loan_history(client):
    # 添加图书和借阅记录
    client.post('/books/new', data={
        'title': '测试书籍',
        'author': '测试作者',
        'isbn': 'unique_isbn_6',
        'publisher': '测试出版社',
        'publication_year': '2023',
        'category': '测试分类',
        'total_stock': '5'
    })
    client.post('/readers/new', data={
        'name': '测试读者',
        'reader_number': 'unique_reader_3',
        'contact': '123456789'
    })
    client.post('/loans/borrow', data={
        'book_id': '1',
        'reader_id': '1',
        'due_date': '2023-12-31'
    })
    # 测试借阅历史
    response = client.get('/search/book_loans/1')
    assert response.status_code == 200
    assert '<h2>借阅历史</h2>' in response.data.decode("utf-8")  # 检查标题是否正确
    assert '测试读者' in response.data.decode("utf-8")  # 检查借阅记录是否正确显示

