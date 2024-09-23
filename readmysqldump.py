import re
import argparse

# 解析 MySQL dump 文件中的数据库和表结构，并提取特定范围的数据
def parse_mysqldump(file_path, target_db, target_table, start_row, end_row, field_types):
    table_data = []
    table_structure = []
    char_fields_indices = []  # 保存指定类型字段的索引
    current_db = None
    current_table = None
    in_create_table = False
    in_insert_statement = False
    insert_values = ""

    # 精确匹配的正则表达式
    use_db_pattern = re.compile(r'USE `(\w+)`;')
    table_pattern = re.compile(r'CREATE TABLE `(\w+)`', re.IGNORECASE)
    column_pattern = re.compile(r'^\s*`(\w+)` (\w+.*?),?$', re.IGNORECASE)
    insert_start_pattern = re.compile(r'INSERT INTO `(\w+)` VALUES', re.IGNORECASE)
    insert_end_pattern = re.compile(r';')

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 匹配 USE DATABASE 语句来识别当前数据库
            use_db_match = use_db_pattern.search(line)
            if use_db_match:
                current_db = use_db_match.group(1)
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

                # 确保只计算指定数据库和表的字段结构
                if current_db == target_db and current_table == target_table:
                    # 找到指定类型字段的索引
                    for i, (column_name, column_type) in enumerate(table_structure):
                        if any(field_type in column_type.lower() for field_type in field_types):
                            char_fields_indices.append(i)

                current_table = None
                continue

            # 匹配表中的列定义，仅在处理指定表时提取列定义
            if in_create_table:
                column_match = column_pattern.search(line)
                if column_match:
                    column_name = column_match.group(1)
                    column_type = column_match.group(2)
                    table_structure.append((column_name, column_type))

            # 处理 INSERT INTO 语句，精确匹配指定的数据库和表
            insert_start_match = insert_start_pattern.search(line)
            if insert_start_match and current_db == target_db and insert_start_match.group(1) == target_table:
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

                    # 仅提取指定类型字段的数据
                    for row in values:
                        filtered_row = [row[i] for i in char_fields_indices]  # 只提取指定索引的字段
                        table_data.append(filtered_row)
                else:
                    insert_values += " " + line.strip()  # 继续拼接

    # 返回请求的表数据的指定行
    return table_data[start_row - 1:end_row]

# 打印表中的特定范围的数据
def print_table_data(data):
    print("Table Data:")
    for row in data:
        print(row)

if __name__ == "__main__":
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="Parse MySQL dump file and extract table data within a range.")
    parser.add_argument("dump_file", help="Path to the MySQL dump file")
    parser.add_argument("database", help="Database name")
    parser.add_argument("table", help="Table name")
    parser.add_argument("x", type=int, help="Start row (x)")
    parser.add_argument("y", type=int, help="End row (y)")
    parser.add_argument("--types", default="char,varchar,text", help="Comma-separated list of field types to extract (default: char,varchar,text)")
    args = parser.parse_args()

    # 解析传入的 MySQL dump 文件和指定参数
    dump_file = args.dump_file
    db_name = args.database
    table_name = args.table
    start_row = args.x
    end_row = args.y
    field_types = args.types.split(',')

    # 解析 dump 文件并提取指定范围的数据
    table_data = parse_mysqldump(dump_file, db_name, table_name, start_row, end_row, field_types)

    # 打印表中的数据作为列表展示
    print(f"Data from table '{table_name}' (rows {start_row} to {end_row}) for field types {field_types}:")
    print_table_data(table_data)
