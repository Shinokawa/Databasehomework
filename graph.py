from graphviz import Digraph

# 创建一个有向图，尽管很多连接是无方向的，但 Graphviz 主要处理有向边
# rankdir='TB' for Top-to-Bottom, 'LR' for Left-to-Right
dot = Digraph(comment='图书馆ER图 - Chen表示法', format='png',
              graph_attr={
                  'rankdir': 'TB',
                  'splines': 'polyline', # 'ortho' or 'polyline' often better for Chen
                  'nodesep': '0.8',
                  'ranksep': '1.2',
                  'fontname': 'SimSun' # 全局字体
              })
dot.attr(label='图书馆借阅系统 ER 图 (Chen 表示法)', labelloc='t', fontsize='20')

# --- 定义样式 ---
entity_style = {'shape': 'rectangle', 'style': 'filled', 'fillcolor': 'lightblue', 'fontname': 'SimSun'}
attribute_style = {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgoldenrodyellow', 'fontname': 'SimSun', 'fontsize':'10'}
pk_attribute_style = {'shape': 'ellipse', 'style': 'filled', 'fillcolor': 'lightgoldenrodyellow', 'fontname': 'SimSun', 'fontsize':'10'} # PK Will use HTML for underline
relationship_style = {'shape': 'diamond', 'style': 'filled', 'fillcolor': 'lightpink', 'fontname': 'SimSun', 'fixedsize':'true', 'width':'2.5', 'height':'1.5'}
line_style = {'dir': 'none', 'fontsize': '10', 'fontname': 'SimSun'} # Chen的线通常无箭头


# --- 实体节点 ---
dot.node('E_Reader', '读者\n(Reader)', **entity_style)
dot.node('E_Book', '书籍\n(Book)', **entity_style)
dot.node('E_Loan', '借阅记录\n(Loan)', **entity_style) # Loan 作为实体

# --- 关系节点 ---
# 关系: 读者 "进行" 借阅记录
dot.node('R_ReaderLoan', '进行借阅', **relationship_style)
# 关系: 书籍 "涉及" 借阅记录
dot.node('R_BookLoan', '涉及书籍', **relationship_style)


# --- 属性节点 和 连接线 (属性 -> 实体) ---

# 读者属性
dot.node('A_Reader_ID', '<<U>reader_id</U>>', **pk_attribute_style)
dot.node('A_Reader_Name', 'name\n(姓名)', **attribute_style)
dot.node('A_Reader_Number', 'reader_number\n(读者编号, 唯一)', **attribute_style)
dot.node('A_Reader_Contact', 'contact\n(联系方式)', **attribute_style)
dot.edge('A_Reader_ID', 'E_Reader', **line_style)
dot.edge('A_Reader_Name', 'E_Reader', **line_style)
dot.edge('A_Reader_Number', 'E_Reader', **line_style)
dot.edge('A_Reader_Contact', 'E_Reader', **line_style)

# 书籍属性
dot.node('A_Book_ID', '<<U>book_id</U>>', **pk_attribute_style)
dot.node('A_Book_Title', 'title\n(书名)', **attribute_style)
dot.node('A_Book_Author', 'author\n(作者)', **attribute_style)
dot.node('A_Book_ISBN', 'isbn\n(ISBN, 唯一)', **attribute_style)
dot.node('A_Book_Publisher', 'publisher\n(出版社)', **attribute_style)
dot.node('A_Book_PubYear', 'publication_year\n(出版年份)', **attribute_style)
dot.node('A_Book_Category', 'category\n(分类)', **attribute_style)
dot.node('A_Book_TotalStock', 'total_stock\n(总库存)', **attribute_style)
dot.node('A_Book_AvailStock', 'available_stock\n(可用库存)', **attribute_style)
dot.edge('A_Book_ID', 'E_Book', **line_style)
dot.edge('A_Book_Title', 'E_Book', **line_style)
dot.edge('A_Book_Author', 'E_Book', **line_style)
dot.edge('A_Book_ISBN', 'E_Book', **line_style)
dot.edge('A_Book_Publisher', 'E_Book', **line_style)
dot.edge('A_Book_PubYear', 'E_Book', **line_style)
dot.edge('A_Book_Category', 'E_Book', **line_style)
dot.edge('A_Book_TotalStock', 'E_Book', **line_style)
dot.edge('A_Book_AvailStock', 'E_Book', **line_style)

# 借阅记录属性 (注意：在Chen图中，外键reader_id, book_id 不作为Loan的直接属性，而是通过关系体现)
dot.node('A_Loan_ID', '<<U>loan_id</U>>', **pk_attribute_style)
dot.node('A_Loan_Date', 'loan_date\n(借阅日期)', **attribute_style)
dot.node('A_Loan_DueDate', 'due_date\n(应还日期)', **attribute_style)
dot.node('A_Loan_ReturnDate', 'return_date\n(实际归还日期)', **attribute_style)
dot.edge('A_Loan_ID', 'E_Loan', **line_style)
dot.edge('A_Loan_Date', 'E_Loan', **line_style) # 或者如果认为这些是关系R_ReaderLoan的属性，则连到菱形上
dot.edge('A_Loan_DueDate', 'E_Loan', **line_style)
dot.edge('A_Loan_ReturnDate', 'E_Loan', **line_style)


# --- 连接实体到关系，并标注基数 ---
# 读者 (1) -- 进行借阅 -- (N) 借阅记录
dot.edge('E_Reader', 'R_ReaderLoan', label='1', **line_style)
dot.edge('R_ReaderLoan', 'E_Loan', label='N', **line_style)

# 书籍 (1) -- 涉及书籍 -- (N) 借阅记录
dot.edge('E_Book', 'R_BookLoan', label='1', **line_style)
dot.edge('R_BookLoan', 'E_Loan', label='N', **line_style)


# --- 渲染 ---
try:
    filename = 'library_chen_er_diagram'
    dot.render(filename, view=True, cleanup=True)
    print(f"Chen ER图已生成: {filename}.png")
except Exception as e:
    print(f"生成Chen ER图失败: {e}")
    print("请确保 Graphviz 已正确安装并已添加到系统 PATH。")
    print("如果使用中文，请确保字体文件存在或尝试使用英文字体（如 Arial Unicode MS）。")