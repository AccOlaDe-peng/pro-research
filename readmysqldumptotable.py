import re
import argparse

# 解析 MySQL dump 文件中的数据库和表结构
def parse_mysqldump(file_path):
    databases = {}
    current_db = None
    current_table = None
    in_create_table = False
    table_structure = []
    table_data = {}

    # 正则表达式匹配 CREATE DATABASE 和 CREATE TABLE 语句
    db_pattern = re.compile(r'CREATE DATABASE /\*!\d+ IF NOT EXISTS\*/ `(\w+)`')
    table_pattern = re.compile(r'CREATE TABLE `(\w+)`')
    column_pattern = re.compile(r'^\s*`(\w+)` (\w+.*?),?$')
    insert_pattern = re.compile(r'INSERT INTO `(\w+)` VALUES (.+);')

    # 指定文件编码为 'utf-8'
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 匹配 CREATE DATABASE 语句
            db_match = db_pattern.search(line)
            if db_match:
                current_db = db_match.group(1)
                databases[current_db] = {"tables": {}, "data": {}}
                continue

            # 匹配 CREATE TABLE 语句
            table_match = table_pattern.search(line)
            if table_match:
                current_table = table_match.group(1)
                in_create_table = True
                table_structure = []
                continue

            # 结束 CREATE TABLE 语句块
            if in_create_table and line.startswith(')'):
                in_create_table = False
                if current_db and current_table:
                    databases[current_db]["tables"][current_table] = table_structure
                current_table = None
                table_structure = []
                continue

            # 匹配表中的列定义
            if in_create_table:
                column_match = column_pattern.search(line)
                if column_match:
                    column_name = column_match.group(1)
                    column_type = column_match.group(2)
                    table_structure.append((column_name, column_type))

            # 匹配 INSERT INTO 语句并提取数据
            insert_match = insert_pattern.search(line)
            if insert_match:
                table_name = insert_match.group(1)
                values = insert_match.group(2)
                # 将插入的值处理为列表
                values = re.findall(r'\((.*?)\)', values)
                values = [tuple(v.split(',')) for v in values]  # 将值拆分为列表
                if current_db and table_name:
                    if table_name not in table_data:
                        table_data[table_name] = []
                    table_data[table_name].extend(values)
                    databases[current_db]["data"][table_name] = table_data[table_name]

    return databases

# 打印数据库、表结构和表中的数据
def print_db_structure(databases):
    for db_name, content in databases.items():
        print(f"Database: {db_name}")
        tables = content["tables"]
        data = content["data"]
        for table_name, columns in tables.items():
            print(f"  Table: {table_name}")
            for column in columns:
                print(f"    Column: {column[0]}, Type: {column[1]}")
            if table_name in data:
                print(f"  Data for table: {table_name}")
                for row in data[table_name]:
                    print(f"    Row: {row}")

if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Parse MySQL dump file and extract database and table structures.")
    parser.add_argument("dump_file", help="Path to the MySQL dump file")
    args = parser.parse_args()

    # 解析传入的 MySQL dump 文件
    dump_file = args.dump_file

    # 解析 dump 文件
    db_structure = parse_mysqldump(dump_file)

    # 打印数据库和表结构
    print_db_structure(db_structure)
