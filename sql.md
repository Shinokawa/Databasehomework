```sql
DROP TRIGGER IF EXISTS trg_cascade_update_sno ON S;
DROP FUNCTION IF EXISTS fn_cascade_update_sno();
DROP TRIGGER IF EXISTS trg_limit_student_count ON S;
DROP FUNCTION IF EXISTS fn_limit_student_count();
DROP TRIGGER IF EXISTS trg_log_grade_update ON SP;
DROP FUNCTION IF EXISTS fn_log_grade_update();
DROP VIEW IF EXISTS V_Female_Student_Projects;
DROP VIEW IF EXISTS V_Student_Grade_Summary;
DROP TABLE IF EXISTS SC_log;
DROP TABLE IF EXISTS SP;
DROP TABLE IF EXISTS P;
DROP TABLE IF EXISTS S;
DROP TABLE IF EXISTS T;
```

### 一、建表和插入数据

**1. 建立四个基本表 (CREATE TABLE for PostgreSQL)**

```sql
CREATE TABLE T (
    Tno CHAR(3) PRIMARY KEY,         
    Tname CHAR(50) NOT NULL,      
    Tsex CHAR(1) NOT NULL CHECK (Tsex IN ('男', '女')), 
    Tdept CHAR(10) NOT NULL       
);

CREATE TABLE S (
    Sno CHAR(5) PRIMARY KEY,         
    Sname CHAR(50) NOT NULL,      
    Ssex CHAR(1) NOT NULL CHECK (Ssex IN ('男', '女')), 
    Sage INT NOT NULL CHECK (Sage > 0 AND Sage < 100), 
    Sdept CHAR(10) NOT NULL       
);

CREATE TABLE P (
    Pno CHAR(1) PRIMARY KEY,         
    Pname CHAR(100) NOT NULL,     
    Tno CHAR(3) NOT NULL,            
    FOREIGN KEY (Tno) REFERENCES T(Tno)
        ON DELETE RESTRICT           
        ON UPDATE CASCADE            
);

CREATE TABLE SP (
    Sno CHAR(5) NOT NULL,            
    Pno CHAR(1) NOT NULL,            
    Grade INT CHECK (Grade >= 0 AND Grade <= 100), 
    PRIMARY KEY (Sno, Pno),          
    FOREIGN KEY (Sno) REFERENCES S(Sno)
        ON DELETE CASCADE,           
    FOREIGN KEY (Pno) REFERENCES P(Pno)
        ON DELETE CASCADE            
);
```

**2. 用INSERT插入数据 (已修正T表数据)**

```sql
INSERT INTO T (Tno, Tname, Tsex, Tdept) VALUES
('101', '梁任甫', '男', 'CS'),
('102', '陈鹤寿', '男', 'CS'),
('103', '王静安', '男', 'MA'),
('104', '赵宜仲', '女', 'IS');

INSERT INTO S (Sno, Sname, Ssex, Sage, Sdept) VALUES
('23121', '韩刚', '男', 20, 'CS'),
('23122', '刘心语', '女', 19, 'CS'),
('23123', '苏恬', '女', 19, 'CS'),
('23124', '潘佳慧', '女', 19, 'CS'),
('23125', '邓辉', '男', 20, 'CS'),
('23126', '肖馨玥', '女', 19, 'CS'),
('23127', '薛志超', '男', 20, 'CS'),
('23128', '迪丽', '女', 19, 'CS'),
('23201', '罗钧一', '男', 20, 'MA'),
('23202', '王浩然', '男', 18, 'MA'),
('23203', '马杰', '男', 20, 'MA'),
('23204', '蔡静雯', '女', 18, 'MA'),
('23205', '刘雪彤', '女', 20, 'MA'),
('23206', '丁一', '女', 18, 'MA'),
('23321', '张立', '男', 19, 'IS'),
('23322', '杨娜', '女', 19, 'IS');

INSERT INTO P (Pno, Pname, Tno) VALUES
('1', '数据库设计项目', '101'),
('2', '无人机飞行设计项目', '103'),
('3', '校园网络规划项目', '102'),
('4', '操作系统设计项目', '101'),
('5', '视觉处理项目', '102'),
('6', '大模型构建项目', '104');

INSERT INTO SP (Sno, Pno, Grade) VALUES
('23122', '3', 80),
('23122', '2', 90),
('23121', '3', 88),
('23122', '5', 68),
('23123', '1', 92),
('23124', '2', 85),
('23125', '5', 94),
('23126', '3', 88),
('23201', '1', 92),
('23202', '1', 92),
('23202', '6', 77),
('23203', '2', 79),
('23204', '4', 85),
('23122', '6', 90),
('23205', '3', 99),
('23206', '5', 58),
('23321', '1', 55),
('23321', '6', 81),
('23322', '6', 89),
('23322', '2', 75),
('23128', '4', 81),
('23127', '4', 89),
('23122', '1', 75),
('23122', '4', 80);
```

### 二、查询

```sql
SELECT Sno, Grade
FROM SP
WHERE Pno = '3';

SELECT T.Tname
FROM T
JOIN P ON T.Tno = P.Tno
WHERE P.Pname = '无人机飞行设计项目';

SELECT Sname, Sdept
FROM S
WHERE Sno NOT IN (SELECT Sno FROM SP WHERE Pno = '2');

SELECT S.Sname
FROM S
JOIN SP ON S.Sno = SP.Sno
GROUP BY S.Sno, S.Sname
HAVING COUNT(DISTINCT SP.Pno) = (SELECT COUNT(*) FROM P);

SELECT Sno
FROM SP
GROUP BY Sno
HAVING COUNT(Pno) = 1;

SELECT Sno, AVG(Grade) AS AverageGrade
FROM SP
GROUP BY Sno
HAVING MIN(Grade) >= 60
ORDER BY AverageGrade DESC;

WITH RankedGrades AS (
    SELECT
        Sno,
        Grade,
        DENSE_RANK() OVER (ORDER BY Grade DESC) as rnk
    FROM SP
    WHERE Pno = '1'
)
SELECT S.Sname
FROM RankedGrades rg
JOIN S ON rg.Sno = S.Sno
WHERE rg.rnk = 2;
```

### 三、数据修改、删除与视图

```sql
UPDATE SP
SET Grade = FLOOR(Grade * 0.95)
WHERE Pno = '4';

BEGIN;

DELETE FROM SP
WHERE Pno = '5';

DELETE FROM P
WHERE Pno = '5';

ROLLBACK;

CREATE OR REPLACE VIEW V_Female_Student_Projects AS
SELECT S.Sno, S.Sname, P.Pname AS ProjectName, SP.Grade
FROM S
JOIN SP ON S.Sno = SP.Sno
JOIN P ON SP.Pno = P.Pno
WHERE S.Ssex = '女';

SELECT Sno, Sname
FROM V_Female_Student_Projects
GROUP BY Sno, Sname
HAVING AVG(Grade) > 80;

CREATE OR REPLACE VIEW V_Student_Grade_Summary AS
SELECT
    Sno,
    COUNT(Pno) AS ProjectCount,
    AVG(Grade) AS AverageGrade
FROM SP
GROUP BY Sno;

GRANT ALL PRIVILEGES ON TABLE SP TO Root3;
GRANT SELECT ON TABLE S TO Root3;
GRANT SELECT ON TABLE P TO Root3;
GRANT SELECT ON TABLE T TO Root3;
```

### 四、触发器 (PostgreSQL)

**1. 级联更新学号触发器**

```sql
CREATE OR REPLACE FUNCTION fn_cascade_update_sno()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.Sno IS DISTINCT FROM NEW.Sno THEN
        UPDATE SP
        SET Sno = NEW.Sno
        WHERE Sno = OLD.Sno;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cascade_update_sno
AFTER UPDATE OF Sno ON S
FOR EACH ROW
EXECUTE FUNCTION fn_cascade_update_sno();
```

**2. 限制学生数量触发器**

```sql
CREATE OR REPLACE FUNCTION fn_limit_student_count()
RETURNS TRIGGER AS $$
DECLARE
    student_count INT;
BEGIN
    SELECT COUNT(*) INTO student_count FROM S;
    IF student_count >= 18 THEN
        RAISE EXCEPTION '无法插入：学生人数已达上限 (18人)';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_limit_student_count
BEFORE INSERT ON S
FOR EACH ROW
EXECUTE FUNCTION fn_limit_student_count();
```

**3. 记录成绩修改日志触发器**

```sql
CREATE TABLE SC_log (
    LogID SERIAL PRIMARY KEY,
    Sno CHAR(5) NOT NULL,
    Pno CHAR(1) NOT NULL,
    OldGrade INT,
    NewGrade INT,
    ChangeTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION fn_log_grade_update()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.Grade IS DISTINCT FROM NEW.Grade THEN
        INSERT INTO SC_log (Sno, Pno, OldGrade, NewGrade, ChangeTime)
        VALUES (OLD.Sno, OLD.Pno, OLD.Grade, NEW.Grade, CURRENT_TIMESTAMP);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_grade_update
AFTER UPDATE OF Grade ON SP
FOR EACH ROW
EXECUTE FUNCTION fn_log_grade_update();
```

### 清理工作：撤销建立的基本表和视图

```sql
DROP TRIGGER IF EXISTS trg_cascade_update_sno ON S;
DROP FUNCTION IF EXISTS fn_cascade_update_sno();
DROP TRIGGER IF EXISTS trg_limit_student_count ON S;
DROP FUNCTION IF EXISTS fn_limit_student_count();
DROP TRIGGER IF EXISTS trg_log_grade_update ON SP;
DROP FUNCTION IF EXISTS fn_log_grade_update();

DROP VIEW IF EXISTS V_Female_Student_Projects;
DROP VIEW IF EXISTS V_Student_Grade_Summary;

DROP TABLE IF EXISTS SC_log;

DROP TABLE IF EXISTS SP;
DROP TABLE IF EXISTS P;
DROP TABLE IF EXISTS S;
DROP TABLE IF EXISTS T;
```
再次感谢您的指正，这使得方案更加完善和准确！