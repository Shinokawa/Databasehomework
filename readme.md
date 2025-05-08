# 个人图书管理系统

本项目是一个数据库课程的大作业。一个基于 Flask 和 PostgreSQL 的个人图书管理系统。它允许用户管理图书、读者信息以及图书的借阅和归还。

## 主要功能

### 图书管理
- **添加图书**: 添加新图书，包括书名、作者、ISBN（唯一）、出版社、出版年份、分类、总库存。可借阅库存默认为总库存 ([`personal_library.app.add_book`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **编辑图书**: 修改已存在的图书信息。确保可借阅库存不大于总库存，且两者均不能为负数 ([`personal_library.app.edit_book`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **删除图书**: 删除图书。如果图书当前有未归还的借阅记录，则不允许删除 ([`personal_library.app.delete_book`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **查询与浏览图书**: 浏览所有图书列表，支持分页和按书名、作者或 ISBN 搜索 ([`personal_library.app.list_books`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **查看图书详情**: 查看单本图书的完整详细信息 ([`personal_library.app.get_book`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。

### 读者管理
- **添加读者**: 添加新的读者信息，包括姓名、读者编号（唯一）、联系方式 ([`personal_library.app.add_reader`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **编辑读者**: 修改已存在的读者信息 ([`personal_library.app.edit_reader`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **删除读者**: 删除读者。如果读者当前有未归还的图书，则不允许删除 ([`personal_library.app.delete_reader`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **查询与浏览读者**: 浏览所有读者的列表 ([`personal_library.app.list_readers`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。

### 借阅管理
- **借书**: 为指定读者借阅指定的图书，需选择图书、读者并指定应归还日期。成功后，图书的“可借阅库存”会自动减1 ([`personal_library.app.borrow_book`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **还书**: 记录指定借阅记录的归还操作。成功后，图书的“可借阅库存”会自动加1 ([`personal_library.app.return_book`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **查询当前借阅**: 查看所有当前未归还的借阅记录列表 ([`personal_library.app.list_active_loans`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **查询逾期借阅**: 查看所有已到期但尚未归还的借阅记录列表 ([`personal_library.app.list_overdue_loans`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。

### 综合查询
- **查询读者借阅历史**: 根据读者查询其所有的借阅历史记录 ([`personal_library.app.reader_loan_history`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。
- **查询图书借阅历史**: 根据图书查询其所有的被借阅历史记录 ([`personal_library.app.book_loan_history`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py))。

## 技术栈
- **后端**: Python, Flask
- **数据库**: PostgreSQL
- **前端**: HTML, CSS, Bootstrap, JavaScript (Select2)
- **测试**: Pytest

## 项目结构概览
```
.
├── .env                  # 环境变量配置
├── graph.py              # 用于生成ER图的脚本 (可能)
├── insert_books.py       # 插入示例数据的脚本
├── library_er_diagram_curved_beautified.png # ER图
├── README.MD             # 本文件
├── requirements.txt      # Python依赖
├── personal_library/     # Flask应用模块
│   ├── app.py            # Flask应用主文件，包含路由和视图函数
│   ├── db.py             # 数据库连接和操作辅助函数
│   ├── schema.sql        # 数据库表结构定义
│   ├── static/           # 静态文件 (CSS, JS, 图片等)
│   └── templates/        # HTML模板
│       ├── base.html
│       ├── index.html
│       ├── books/
│       ├── readers/
│       └── loans/
├── tests/                # 测试代码
│   ├── conftest.py       # Pytest配置文件
│   └── test_app.py       # 应用测试用例
└── doc/                  # 文档目录 (包含LaTeX设计文档等)
    └── doc.tex           # 项目设计文档
```

## 安装与设置

1.  **克隆仓库**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **创建并激活虚拟环境**
    ```bash
    python -m venv venv
    # Windows
    # venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

4.  **配置数据库**
    - 确保你有一个正在运行的 PostgreSQL 实例。
    - 创建数据库，例如 `personal_library_db`。
    - 创建数据库用户，例如 `library_admin` 并授予相应权限。

5.  **配置环境变量**
    复制项目根目录下的 `.env` 文件（如果不存在，请创建一个），并根据你的环境修改以下变量：
    ```env
    # .env
    DATABASE_URL="postgresql://library_admin:your_password@localhost:5432/personal_library_db"
    FLASK_APP="personal_library.app"
    FLASK_ENV="development" # 设置为 "production" 用于生产环境
    SECRET_KEY="a_very_secret_random_string_for_flask_sessions" # 请修改为一个强随机字符串
    ```
    请参考你工作区中的现有 [`.env`](/.env) 文件进行配置。

## 数据库初始化

配置好数据库连接后，运行以下命令来创建数据库表结构（定义于 [`personal_library/schema.sql`](/Users/sakiko/Desktop/Databasehomework/personal_library/schema.sql)）：
```bash
flask init-db
```
这将调用 [`personal_library.app.init_db_command`](/Users/sakiko/Desktop/Databasehomework/personal_library/app.py) 函数。

## 插入示例数据 (可选)

项目包含一个脚本 [`insert_books.py`](/Users/sakiko/Desktop/Databasehomework/insert_books.py) 用于向数据库中插入一些示例图书数据。在初始化数据库表之后，你可以运行此脚本：
```bash
python insert_books.py
```
**注意**: 此脚本会首先清空 `loans`, `books`, `readers` 表中的数据。

## 运行应用

```bash
flask run
```
应用默认会在 `http://127.0.0.1:5000/` 上运行。

## 运行测试

项目使用 Pytest 进行测试。测试用例位于 `tests/` 目录下，例如 [`tests/test_app.py`](/Users/sakiko/Desktop/Databasehomework/tests/test_app.py)。
在项目根目录下运行：
```bash
pytest
```
测试配置见 [`tests/conftest.py`](/Users/sakiko/Desktop/Databasehomework/tests/conftest.py)，它会在每个测试前清空数据库。


