import json
import os
import re
from logs import *
from utils.jcoptions import *
from flask import Flask, request
from flask_cors import *


app = Flask(__name__)

url_sort = []

jcOption = []

# logger = MyLogger(log_file="log\\crawler.log", log_level=logging.DEBUG)


@app.route('/search', methods=['POST'])
@cross_origin()
def search():
    """参数传递"""
    key_words = []
    if request.form.get("key_words") != '':
        key_words = request.form.get("key_words").split(' ')
        key_words = list(filter(lambda x: len(x.strip()) != 0, key_words))
    print(key_words)
    start_year = 2018
    if request.form.get("start_year") != '':
        start_year = int(request.form.get("start_year"))
    print(start_year)
    final_year = 2023
    if request.form.get("final_year") != '':
        final_year = int(request.form.get("final_year"))
    print(final_year)
    # volumes of journals
    vols = 10
    if request.form.get("vols") != '':
        vols = int(request.form.get("vols"))
    print(vols)

    cj_list = []
    if request.form.get("cj_list") != '':
        cj_list = group_list(request.form.get("cj_list").split(','), 3)
    print(cj_list)

    match_pattern = '1'
    if request.form.get("match_pattern") != '':
        match_pattern = str(request.form.get("match_pattern"))
    print(match_pattern)


    result_ = []
    for paths in cj_list:
        print("hhh")
        if '会' in paths[1]:
            for y in range(final_year, start_year - 1, -1):
                # 加载json文件
                try:
                    prefix = paths[2] + "_" + str(y)
                    target_file_name = ''
                    folder_path = "../retrieval_root/" + paths[0] + "/" + paths[1] + '/' + paths[2]
                    files = os.listdir(folder_path)
                    # 遍历文件列表，查找匹配的文件
                    for file in files:
                        if prefix in file:
                            target_file_name = file
                            print(target_file_name)
                            break
                    else:
                        print("未找到匹配的文件 "+prefix)
                        continue
                    ndp = target_file_name.replace(".json", "").split("_")
                    with open(folder_path + "/" + target_file_name, "r") as f:
                        papers = json.load(f)
                        # print(papers)
                        # 会议
                        for p in papers:
                            # 新增属性
                            p['jcname'] = p['journal']
                            p['year_or_volume'] = p['datePublished']
                            p['publisher_or_year'] = ndp[2]
                            # 重构属性
                            p['authors'] = ", ".join([author["name"] for author in p["authors"]])
                            if start_year <= int(p['year_or_volume']) <= final_year:
                                save = False
                                if match_pattern == '1':
                                    for word in key_words:
                                        if word.lower() in p["title"].lower():
                                            save = True
                                            break
                                    if save:
                                        p['id'] = len(result_)
                                        result_.append(p)
                                elif match_pattern == '2':
                                    for word in key_words:
                                        if match_word(p["title"].lower(), word.lower()):
                                            save = True
                                            break
                                    if save:
                                        p['id'] = len(result_)
                                        result_.append(p)
                                elif match_pattern == '3':
                                    count = 0
                                    for word in key_words:
                                        if word.lower() in p["title"].lower():
                                            count += 1
                                    if count == len(key_words):
                                        p['id'] = len(result_)
                                        result_.append(p)
                                elif match_pattern == '4':
                                    count = 0
                                    for word in key_words:
                                        if match_word(p["title"].lower(), word.lower()):
                                            count += 1
                                    if count == len(key_words):
                                        p['id'] = len(result_)
                                        result_.append(p)
                except BaseException as e:
                    print(e)
                    continue
        else:
            # 期刊
            folder_path = "new_paper_collect/" + paths[0] + "/" + paths[1] + '/' + paths[2].lower()  # 替换为你要扫描的文件夹路径

            max_number = float('-inf')  # 初始化最大数字为负无穷大

            # 遍历文件夹中的文件
            for file_name in os.listdir(folder_path):
                # 使用正则表达式提取文件名中的数字部分
                match = re.search(r'\d+', file_name)
                if match:
                    number = int(match.group())  # 提取到的数字部分转换为整数
                    max_number = max(max_number, number)

            latest_vol = max_number
            print('latest_vol: ' + str(latest_vol))
            for volume in range(latest_vol, latest_vol - vols, -1):
                print(volume)
                try:
                    with open(
                            "new_paper_collect/" + paths[0] + "/" + paths[1] + '/' + paths[2].lower() + '/' + paths[
                                2].lower() + str(volume) + ".json", "r") as f:
                        papers = json.load(f)
                        # print(papers)
                        # 期刊
                        for p in papers:
                            p['conference_or_article'] = p['journal']
                            p['authors'] = ", ".join([author["name"] for author in p["authors"]])
                            p['year_or_volume'] = p['volume']
                            del p['volume']
                            del p['journal']
                            if latest_vol - int(p['year_or_volume']) <= vols:
                                save = False
                                if match_pattern == '1':
                                    for word in key_words:
                                        if word.lower() in p["title"].lower():
                                            save = True
                                            break
                                    if save:
                                        p['id'] = len(result_)
                                        result_.append(p)
                                elif match_pattern == '2':
                                    for word in key_words:
                                        if match_word(p["title"].lower(), word.lower()):
                                            save = True
                                            break
                                    if save:
                                        p['id'] = len(result_)
                                        result_.append(p)
                                elif match_pattern == '3':
                                    count = 0
                                    for word in key_words:
                                        if word.lower() in p["title"].lower():
                                            count += 1
                                    if count == len(key_words):
                                        p['id'] = len(result_)
                                        result_.append(p)

                                elif match_pattern == '4':
                                    count = 0
                                    for word in key_words:
                                        if match_word(p["title"].lower(), word.lower()):
                                            count += 1
                                    if count == len(key_words):
                                        p['id'] = len(result_)
                                        result_.append(p)
                except BaseException as e:
                    print(e)
                    continue
    for item in result_:
        print(item)
    return result_


def group_list(lst, size):
    # 使用切片操作将列表分组
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def match_word(string, word):
    # 构造正则表达式，匹配一个单词，忽略标点符号和大小写
    pattern = rf'(?i)\b{re.escape(word)}\b'
    # 使用正则表达式查找匹配项
    match = re.search(pattern, string)
    if match:
        return True  # 匹配成功
    else:
        return False  # 匹配失败


@app.route('/jcoptions', methods=['GET'])
@cross_origin()
def getJCOptions():
    return jcOption


if __name__ == '__main__':
    jcOption = getcjOption()
    print(jcOption)
    # 启动时构建root树，并保存到全局变量，前端界面创建时，向服务器索要
    app.run(host="172.31.225.109", port=5001, debug=False)
