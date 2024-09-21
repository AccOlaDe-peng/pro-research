import tarfile
import argparse

# 定义命令行参数
parser = argparse.ArgumentParser(description="读取 tar 文件中指定文件的部分内容")
parser.add_argument('tar_file', help="tar 文件路径")
parser.add_argument('file_index', type=int, help="要读取的文件在 tar 中的索引 (从 0 开始)")
parser.add_argument('start_byte', type=int, help="读取的起始字节位置 (Y)")
parser.add_argument('end_byte', type=int, help="读取的结束字节位置 (Z)")

args = parser.parse_args()

# 打开 tar 文件
with tarfile.open(args.tar_file, 'r') as tar:
    members = tar.getmembers()

    # 检查文件索引是否有效
    if args.file_index >= len(members):
        print(f"文件索引 {args.file_index} 超出范围。tar 文件中只有 {len(members)} 个文件。")
    else:
        member = members[args.file_index]

        if member.isfile():  # 检查是否是文件（跳过目录）
            print(f"正在读取文件: {member.name}")
            
            # 读取文件内容
            file_obj = tar.extractfile(member)
            
            if file_obj:  # 确保文件对象不为空
                content = file_obj.read()

                # 读取文件指定字节范围内容
                byte_excerpt = content[args.start_byte:args.end_byte]
                
                # 输出读取的内容（以十六进制形式打印）
                print(f"文件 {member.name} 第 {args.start_byte} 到第 {args.end_byte} 个字节内容:")
                print(byte_excerpt)
        else:
            print(f"索引 {args.file_index} 对应的条目不是文件。")