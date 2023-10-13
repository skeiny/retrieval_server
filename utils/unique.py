my_list = [
    {'doi': '10.1001/jama.2021.1234', 'title': 'Example Title 3'},
    {'doi': '10.1002/jnr.24809', 'title': 'Example Title 2'},
    {'doi': '10.1001/jama.2021.1234', 'title': 'Example Title2'}
]

# 使用字典来去除重复项
doi_set = set()
unique_list = []

for item in my_list:
    doi = item['doi']
    if doi not in doi_set:
        unique_list.append(item)
        doi_set.add(doi)

# 打印去除重复项后的列表
for item in unique_list:
    print(item)