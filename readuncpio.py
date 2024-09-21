import tarfile
import argparse
import subprocess
import os
import tempfile

def convert_cpio_to_tar(cpio_file, tar_file):
    # 使用 cpio 命令将 .cpio 文件转换为 .tar 文件
    try:
        command = f"cpio -it < {cpio_file} | tar -cvf {tar_file} -T -"
        subprocess.run(command, shell=True, check=True)
        print(f"成功将 {cpio_file} 转换为 {tar_file}.")
    except subprocess.CalledProcessError as e:
        print(f"转换失败: {e}")
        raise

def process_tar_file(tar_file, file_index, start_byte, end_byte):
    # 处理 tar 文件中的指定内容
    with tarfile.open(tar_file, 'r') as tar:
        members = tar.getmembers()

        # 检查文件索引是否有效
        if file_index >= len(members):
            print(f"文件索引 {file_index} 超出范围。tar 文件中只有 {len(members)} 个文件。")
        else:
            member = members[file_index]

            if member.isfile():  # 检查是否是文件（跳过目录）
                print(f"正在读取文件: {member.name}")
                
                # 读取文件内容
                file_obj = tar.extractfile(member)
                
                if file_obj:  # 确保文件对象不为空
                    content = file_obj.read()

                    # 读取文件指定字节范围内容
                    byte_excerpt = content[start_byte:end_byte]
                    
                    # 输出读取的内容（以十六进制形式打印）
                    print(f"文件 {member.name} 第 {start_byte} 到第 {end_byte} 个字节内容:")
                    print(byte_excerpt.hex())
            else:
                print(f"索引 {file_index} 对应的条目不是文件。")

def main():
    # 定义命令行参数
    parser = argparse.ArgumentParser(description="处理 .cpio 文件并读取其中指定的 tar 文件内容")
    parser.add_argument('cpio_file', help=".cpio 文件路径")
    parser.add_argument('file_index', type=int, help="要读取的文件在 tar 中的索引 (从 0 开始)")
    parser.add_argument('start_byte', type=int, help="读取的起始字节位置 (Y)")
    parser.add_argument('end_byte', type=int, help="读取的结束字节位置 (Z)")

    args = parser.parse_args()

    # 创建临时 .tar 文件
    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as temp_tar_file:
        tar_file = temp_tar_file.name

    try:
        # 将 .cpio 文件转换为 .tar 文件
        print(args.cpio_file, tar_file)
        convert_cpio_to_tar(args.cpio_file, tar_file)

        # 处理转换后的 .tar 文件
        process_tar_file(tar_file, args.file_index, args.start_byte, args.end_byte)

    finally:
        # 删除临时生成的 .tar 文件
        os.remove(tar_file)

if __name__ == "__main__":
    main()
