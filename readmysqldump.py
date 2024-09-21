# import re
# import argparse

# # MySQL 系统数据库的列表
# SYSTEM_DATABASES = ['information_schema', 'mysql', 'performance_schema', 'sys']

# # 解析 MySQL dump 文件中的数据库和表结构
# def parse_mysqldump(file_path):
#     databases = {}
#     users = {}
#     current_db = None
#     current_table = None
#     in_create_table = False
#     table_structure = []

#     # 正则表达式匹配 CREATE DATABASE 和 CREATE TABLE 语句
#     db_pattern = re.compile(r'CREATE DATABASE /\*!\d+ IF NOT EXISTS\*/ `(\w+)`')
#     table_pattern = re.compile(r'CREATE TABLE `(\w+)`')
#     column_pattern = re.compile(r'^\s*`(\w+)` (\w+.*?),?$')

#     # 匹配 GRANT 语句的正则表达式
#     grant_pattern = re.compile(r'GRANT (.+) ON (.+) TO \'(\w+)\'@\'([^\']+)\' IDENTIFIED BY PASSWORD \'([^\']+)\';')

#     with open(file_path, 'r', encoding="utf-8") as file:
#         for line in file:
#             # 匹配 CREATE DATABASE 语句
#             db_match = db_pattern.search(line)
#             if db_match:
#                 current_db = db_match.group(1)
#                 # 跳过系统数据库
#                 if current_db not in SYSTEM_DATABASES:
#                     databases[current_db] = {}
#                 continue

#             # 匹配 CREATE TABLE 语句
#             if current_db and current_db not in SYSTEM_DATABASES:
#                 table_match = table_pattern.search(line)
#                 if table_match:
#                     current_table = table_match.group(1)
#                     in_create_table = True
#                     table_structure = []
#                     continue

#             # 结束 CREATE TABLE 语句块
#             if in_create_table and line.startswith(')'):
#                 in_create_table = False
#                 if current_db and current_table:
#                     databases[current_db][current_table] = table_structure
#                 current_table = None
#                 table_structure = []
#                 continue

#             # 匹配表中的列定义
#             if in_create_table:
#                 column_match = column_pattern.search(line)
#                 if column_match:
#                     column_name = column_match.group(1)
#                     column_type = column_match.group(2)
#                     table_structure.append((column_name, column_type))


#             # 匹配 GRANT 语句并提取用户信息
#             grant_match = grant_pattern.search(line)
#             if grant_match:
#                 privileges = grant_match.group(1)
#                 scope = grant_match.group(2)
#                 username = grant_match.group(3)
#                 hostname = grant_match.group(4)
#                 password = grant_match.group(5)
#                 users[username] = {
#                     "hostname": hostname,
#                     "privileges": privileges,
#                     "scope": scope,
#                     "password": password
#                 }

#     return databases, users

# # 打印数据库和表结构
# def print_db_structure(databases, users):
#     for db_name, tables in databases.items():
#         print(f"Database: {db_name}")
#         for table_name, columns in tables.items():
#             print(f"  Table: {table_name}")
#             for column in columns:
#                 print(f"    Column: {column[0]}, Type: {column[1]}")
        
#     # 打印用户信息
#     print("\nMySQL Users:")
#     for username, info in users.items():
#         print(f"  User: {username}")
#         print(f"    Hostname: {info['hostname']}")
#         print(f"    Privileges: {info['privileges']}")
#         print(f"    Scope: {info['scope']}")
#         print(f"    Password: {info['password']}")
        

# if __name__ == "__main__":
#     # 使用 argparse 解析命令行参数
#     parser = argparse.ArgumentParser(description="Parse MySQL dump file and extract database and table structures, excluding system databases.")
#     parser.add_argument("dump_file", help="Path to the MySQL dump file")
#     args = parser.parse_args()

#     # 解析传入的 MySQL dump 文件
#     dump_file = args.dump_file

#     # 解析 dump 文件
#     db_structure, user_info = parse_mysqldump(dump_file)
#     print("user_info", user_info)
#     # 打印数据库和表结构
#     print_db_structure(db_structure, user_info)


import re
import argparse

# 解析 MySQL dump 文件中的数据库和表结构，并提取特定范围的数据
def parse_mysqldump(file_path, db_name, table_name, start_row, end_row):
    databases = {}
    current_db = None
    current_table = None
    table_data = []
    in_create_table = False
    table_structure = []

    # 正则表达式匹配 CREATE DATABASE、CREATE TABLE 和 INSERT INTO 语句
    db_pattern = re.compile(r'CREATE DATABASE /\*!\d+ IF NOT EXISTS\*/ `(\w+)`')
    table_pattern = re.compile(r'CREATE TABLE `(\w+)`')
    column_pattern = re.compile(r'^\s*`(\w+)` (\w+.*?),?$')
    insert_pattern = re.compile(r'INSERT INTO `(\w+)` VALUES (.+);')
    insert_start_pattern = re.compile(r'INSERT INTO `(\w+)` VALUES')
    insert_end_pattern = re.compile(r';')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 匹配 CREATE DATABASE 语句
            db_match = db_pattern.search(line)
            if db_match:
                current_db = db_match.group(1)
                databases[current_db] = {}
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
                    databases[current_db][current_table] = table_structure
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

            # 处理 INSERT INTO 语句
            insert_start_match = insert_start_pattern.search(line)
            if insert_start_match and current_db == db_name and insert_start_match.group(1) == table_name:
                in_insert_statement = True
                insert_values = line[line.index('VALUES') + len('VALUES'):].strip()
                continue

            # 如果在 INSERT INTO 语句中，拼接多行
            if in_insert_statement:
                if insert_end_pattern.search(line):
                    insert_values += " " + line[:line.index(';')].strip()  # 结束语句
                    in_insert_statement = False
                    # 提取插入的值
                    values = re.findall(r'\((.*?)\)', insert_values)
                    values = [tuple(v.split(',')) for v in values]  # 将值拆分为列表
                    table_data.extend(values)
                else:
                    insert_values += " " + line.strip()  # 继续拼接

            # # 匹配 INSERT INTO 语句并提取数据
            # insert_match = insert_pattern.search(line)
            # if insert_match:
            #     current_insert_table = insert_match.group(1)
            #     print("current_insert_table", current_insert_table)
            #     if current_db == db_name and current_insert_table == table_name:
            #         # 提取插入的值
            #         values = insert_match.group(2)
            #         values = re.findall(r'\((.*?)\)', values)
            #         values = [tuple(v.split(',')) for v in values]  # 将值拆分为列表

            #         # 仅提取第 start_row 到第 end_row 行数据
            #         if start_row <= len(table_data) + len(values) <= end_row:
            #             table_data.extend(values)

    print("database", databases)
    # 仅返回请求的表数据的指定行
    return table_data[start_row - 1:end_row]

# 打印表中的特定范围的数据
def print_table_data(data):
    for row in data:
        print(f"    Row: {row}")

if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Parse MySQL dump file and extract table data within a range.")
    parser.add_argument("dump_file", help="Path to the MySQL dump file")
    parser.add_argument("database", help="Database name")
    parser.add_argument("table", help="Table name")
    parser.add_argument("x", type=int, help="Start row (x)")
    parser.add_argument("y", type=int, help="End row (y)")
    args = parser.parse_args()

    # 解析传入的 MySQL dump 文件和指定参数
    dump_file = args.dump_file
    db_name = args.database
    table_name = args.table
    start_row = args.x
    end_row = args.y

    # 解析 dump 文件并提取指定范围的数据
    table_data = parse_mysqldump(dump_file, db_name, table_name, start_row, end_row)

    # 打印表中的数据
    print(f"Data from table '{table_name}' (rows {start_row} to {end_row}):")
    print_table_data(table_data)
