import pytest
from personal_library.app import app
from personal_library.db import get_db

@pytest.fixture(autouse=True)
def clear_database():
    """
    在每个测试前清空数据库，确保测试环境干净。
    """
    with app.app_context():  # 显式设置应用上下文
        db = get_db()
        with db.cursor() as cur:
            cur.execute("TRUNCATE TABLE loans, books, readers RESTART IDENTITY CASCADE;")
        db.commit()