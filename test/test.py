
if __name__ == "__main__":
    # 打开文件以读取
    with open("./jclist.csv", "r", encoding="utf-8") as file:
        # 逐行读取文件内容
        for line in file:
            # 去掉行末尾的换行符
            line = line.strip()

            # 如果行不为空
            if line:
                print(line)
                # 使用逗号分割行
                parts = line.split(",")
                # 如果行被成功分割成了5部分（category, link, name, 领域, CCF等级）
                if len(parts) == 5:
                    category = parts[0].strip()
                    link = parts[1].strip()
                    name = parts[2].strip()
                    field = parts[3].strip()
                    ccf_level = parts[4].strip()

                    # 打印每一部分的内容
                    # print(f"Category: {category}")
                    # print(f"Link: {link}")
                    # print(f"Name: {name}")
                    # print(f"领域: {field}")
                    # print(f"CCF等级: {ccf_level}")
                    # print("\n")  # 打印空行以分隔不同的记录
