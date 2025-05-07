import psycopg2
import psycopg2.extras  # 用于字典游标
import os
from flask import g, current_app  # g 是 Flask提供的请求绑定数据对象, current_app 用于获取应用配置

# 从环境变量获取DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    """
    获取数据库连接。
    如果当前请求上下文中不存在连接，则创建一个新的连接并存储它。
    """
    if 'db' not in g:
        if not DATABASE_URL:
            # 如果 DATABASE_URL 未设置，则记录错误并引发运行时错误
            current_app.logger.error("DATABASE_URL 未设置。请在 .env 文件或环境变量中配置。")
            raise RuntimeError("DATABASE_URL 未设置。应用无法连接到数据库。")
        try:
            g.db = psycopg2.connect(DATABASE_URL)
        except psycopg2.OperationalError as e:
            current_app.logger.error(f"无法连接到数据库: {e}")
            raise RuntimeError(f"无法连接到数据库: {e}")
    return g.db

def close_db(e=None):
    """
    关闭数据库连接。
    从请求上下文中移除连接并关闭它。
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """
    在 Flask 应用实例上注册数据库关闭函数。
    这样在应用上下文销毁时，会自动关闭数据库连接。
    """
    app.teardown_appcontext(close_db)  # 注册应用上下文结束时调用的函数

def query_db(query, args=(), one=False, commit=False):
    """
    执行数据库查询。
    :param query: SQL 查询语句。
    :param args: 查询参数 (元组)。
    :param one: 如果为 True，则只返回第一行结果。
    :param commit: 如果为 True，则在执行后提交事务 (用于 INSERT, UPDATE, DELETE)。
    :return: 查询结果 (字典或字典列表) 或影响的行数 (如果 commit=True)。
    """
    db = get_db()
    # 使用 DictCursor 使查询结果返回字典形式，方便通过列名访问
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute(query, args)
        if commit:  # 对于 INSERT, UPDATE, DELETE 操作
            db.commit()
            return cur.rowcount  # 返回影响的行数
        rv = cur.fetchall()
    except psycopg2.Error as e:
        db.rollback()  # 如果发生错误，回滚事务
        # 使用 current_app.logger 记录错误
        current_app.logger.error(f"数据库错误: {e}\n查询: {query}\n参数: {args}")
        raise  # 重新抛出异常，由调用者处理
    finally:
        cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_sql_file(filename):
    """
    执行一个 SQL 文件中的所有语句。
    :param filename: SQL 文件的路径。
    """
    db = get_db()
    cur = db.cursor()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            cur.execute(sql_script)
        db.commit()  # 成功执行后提交事务
        current_app.logger.info(f"成功执行 SQL 文件: {filename}")
    except psycopg2.Error as e:
        db.rollback()  # 执行SQL文件出错时回滚
        current_app.logger.error(f"执行 SQL 文件 {filename} 时出错: {e}")
        raise  # 重新抛出异常
    except FileNotFoundError:
        current_app.logger.error(f"SQL 文件未找到: {filename}")
        raise  # 文件未找到，重新抛出异常
    finally:
        cur.close()

def init_db_tables():
    """
    初始化数据库表结构。
    这将执行位于 personal_library/schema.sql 文件中的SQL语句。
    确保此函数在应用上下文中被调用，以便 get_db() 和 current_app.logger 正常工作。
    """
    # 构建 schema.sql 文件的绝对路径
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    try:
        current_app.logger.info(f"尝试从以下位置初始化数据库表: {schema_path}")
        execute_sql_file(schema_path)
        current_app.logger.info("数据库表从 schema.sql 成功初始化。")
    except Exception as e:
        current_app.logger.error(f"使用 schema.sql 初始化数据库表失败: {e}")
        raise