```

**重要说明和后续步骤：**


3.  **创建模板文件夹和文件：**
    *   根据你的项目结构，创建 `templates` 文件夹以及其中规划的子文件夹 (`books`, `readers`, `loans`) 和 HTML 文件 (`base.html`, `index.html`, `books/list.html`, `books/form.html`, `readers/list.html`, `readers/form.html`, `loans/borrow_form.html`, `loans/active_loans.html`, `loans/overdue_loans.html`, `loans/history.html` 等)。
    *   你需要根据 `render_template` 调用中传递的变量来填充这些 HTML 文件的具体内容。

4.  **初始化数据库：**
    *   打开终端，导航到 `Databasehomework` 目录。
    *   设置 Flask 应用环境变量 (如果还没有通过 `.env` 或其他方式设置):
        ```bash
        export FLASK_APP=personal_library.app
        export FLASK_ENV=development
        ```
    *   运行数据库初始化命令：
        ```bash
        flask init-db
        ```
        如果 `click` 未正确导入或 `init-db` 命令未注册，此步骤可能会失败。确保 `click` 已安装，并且 `app.py` 中的 `init_db_command` 函数正确。

5.  **运行应用：**
    *   使用以下命令运行 Flask 应用：
        ```bash
        flask run
        ```
    *   或者，如果 `if __name__ == '__main__':` 中的 `app.run()` 被执行 (例如直接 `python personal_library/app.py`)。推荐使用 `flask run`。

6.  **错误处理和日志：**
    *   代码中加入了一些基本的错误处理和日志记录 (`current_app.logger.error`)。在生产环境中，你可能需要更完善的日志配置。

7.  **事务处理：**
    *   `borrow_book` 和 `return_book` 函数中使用了显式的事务控制 (`conn.commit()`, `conn.rollback()`) 和行级锁 (`FOR UPDATE`) 来处理并发。

8.  **安全性：**
    *   **CSRF保护**：对于生产应用，应添加 CSRF 保护 (例如使用 Flask-WTF)。
    *   **输入验证**：虽然进行了一些基本验证，但更复杂的验证（如日期格式、ISBN 格式等）可以使用库（如 WTForms）来增强。
    *   **SQL注入**：通过使用参数化查询 (`db.query_db` 中的 `args`)，可以防止 SQL 注入。

这个 `app.py` 文件提供了你设计方案中大部分核心功能的实现骨架。你需要创建相应的 HTML 模板来完成用户界面。# filepath: /Users/sakiko/Desktop/Databasehomework/personal_library/app.py
