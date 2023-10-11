import os
import shutil

# 根路径 r1 和 r2
r1 = '../raw'
r2 = '../retrieval_root'


# 要搜索的文件夹路径
folder_to_search = '../retrieval_root'

# 目标文件夹名称
target_folder_name = 'Fuc'

# 定义一个函数，用于递归地搜索文件夹并返回相对路径
def search_folder_with_relative_path(folder_path, target_folder_name, current_path=''):
    for root, dirs, files in os.walk(folder_path):
        if target_folder_name in dirs:
            relative_path = os.path.relpath(os.path.join(root, target_folder_name), folder_path)
            return relative_path  # 返回找到的目标文件夹的相对路径
    return None  # 没找到目标文件夹，返回None

# 定义函数，递归复制文件夹内的文件
def copy_files(src_dir, dst_dir):
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)

        if os.path.isdir(src_item):
            # 如果是子文件夹，递归复制
            copy_files(src_item, dst_item)
        else:
            # 如果是文件，复制到目标文件夹
            shutil.copy2(src_item, dst_item)
            print(f"复制文件 {src_item} 到 {dst_item}")


# 遍历r1的每个不含子文件夹的文件夹
for root, dirs, files in os.walk(r1):
    for dir in dirs:

        src_dir = os.path.join(root, dir)

        dst_dir = os.path.join(r2, search_folder_with_relative_path(r2, dir))

        # 创建目标文件夹（如果不存在）
        os.makedirs(dst_dir, exist_ok=True)

        # 复制文件夹内的文件
        copy_files(src_dir, dst_dir)

print("复制完成")
