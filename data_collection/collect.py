import json
import os
import random
import re
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup

# logger
from utils.log import *

logger = MyLogger(log_file="../logs/run.log", log_level=logging.DEBUG)


def getJournal(j_url, officialName, area, rank):
    jBsObj = getBsObj(j_url)
    if jBsObj is None:
        logger.error("Get homepage error. " + j_url + " " + officialName)
        return
    try:
        bsMain = jBsObj.body.find("div", {"id": "main"})
        bsUl = bsMain.find("ul", recursive=False)
        bsLis = bsUl.findAll("li")
        bsAs = [a for li in bsLis for a in li.findAll('a')]
        tasks = [{"volume": "None",
                  "datePublished": "None",
                  "toc-link": item.get("href")} for item in bsAs]
    except Exception as e:
        logger.error("Failed to create tasks. " + j_url + " " + officialName + " " + e.__str__())
        return

    # 文件夹
    folder = "../output/retrieval_root/" + area + "/" + rank + "/" + officialName
    try:
        os.makedirs(folder, exist_ok=True)
    except FileExistsError:
        print("Folder already exists.")
    except Exception as e:
        logger.error("Failed to create folder. " + j_url + " " + officialName + " " + e.__str__())
        return

    # 已完成前期准备，开始爬取
    runTasks("journal", tasks, folder, officialName, j_url)


def getConference(c_url, officialName, area, rank):
    cBsObj = getBsObj(c_url)
    if cBsObj is None:
        logger.error("Get homepage error. " + c_url + " " + officialName)
        return
    try:
        bsUls = cBsObj.body.find("div", {"id": "main"}).findAll("ul", {"class": "publ-list"})
        # bsLis = [item.find("li", {"class": "entry editor toc"}) for item in bsUls]
        bsLis = [li for ul in bsUls for li in ul.findAll("li", {"class": "entry editor toc"})]
        bsCites = [item.find("cite", {"class": "data tts-content"}) for item in bsLis]
        tasks = []
        for cite in bsCites:
            task_ = {"publisher": "None", "datePublished": "None", "toc-link": "None"}
            publisher = cite.find("span", {"itemprop": "publisher"})
            datePublished = cite.find("span", {"itemprop": "datePublished"})
            toc_link = cite.find("a", {"class": "toc-link"})
            if publisher is not None:
                task_["publisher"] = publisher.get_text()
            if datePublished is not None:
                task_["datePublished"] = datePublished.get_text()
            if toc_link is not None:
                task_["toc-link"] = toc_link.get("href")
            tasks.append(task_)
        # print(tasks)
    except Exception as e:
        logger.error("Failed to create tasks. " + c_url + " " + officialName + " Details: " + e.__str__())
        return

    folder = "../output/retrieval_root/" + area + "/" + rank + "/" + officialName
    try:
        os.makedirs(folder, exist_ok=True)
    except FileExistsError:
        print("Folder already exists.")
    except Exception as e:
        logger.error("Failed to create folder. " + c_url + " " + officialName + " Details: " + e.__str__())
        return
    # 已完成前期准备，开始爬取
    runTasks("conference", tasks, folder, officialName, c_url)


def getBsObj(url):
    if url is None:
        logger.info("Url is None")
        return None
    wait_time = random.uniform(0.1, 0.5)
    print("sleep time: "+str(wait_time))
    time.sleep(wait_time)
    try:
        print("getting: " + url)
        html = urlopen(url)
    except BaseException as e:
        logger.info("Could not get url: " + url + " Details: " + e.__str__())
        return None
    try:
        bsObj = BeautifulSoup(html, features="lxml")
    except Exception as e:
        logger.info("Could not get bsObj: " + url + " Details: " + e.__str__())
        return None
    return bsObj


def saveJSON(papers, jsonPath):
    old_len = 0
    add_len = len(papers)
    new_data = []
    if os.path.exists(jsonPath):
        with open(jsonPath, "r") as f:
            print("Combing data...")
            new_data = json.load(f)
            #print(new_data)
            old_len = len(new_data)
    new_data.extend(papers)
    #print(new_data)
    # 使用字典来去除重复项
    doi_set = set()
    unique_list = []
    for p in new_data:
        doi = p["doi"]
        if "None".__eq__(doi) or doi not in doi_set:
            unique_list.append(p)
            doi_set.add(doi)
    new_len = len(unique_list)
    with open(jsonPath, "w") as f:
        json.dump(unique_list, f, indent=4)
    # print(jsonPath + ": old_len="+str(old_len)+", add_len="+str(add_len)+", new_len="+str(new_len))
    logger.info(jsonPath + ": old_len="+str(old_len)+", add_len="+str(add_len)+", new_len="+str(new_len))


def runTasks(ttype, tasks, folder, officialName, url):
    # 加载success文件, 过滤掉搜索过的任务
    try:
        with open("../logs/success.txt", 'r') as file:
            success_urls = set(line.strip() for line in file)
    except FileNotFoundError:
        logger.info("Could not find success_urls.txt")

    # 开始做任务
    for task in tasks:
        # 成功搜索过, 跳过任务
        if task["toc-link"] in success_urls:
            print(task["toc-link"] + " already success.")
            continue

        bsObj = None
        papers = []
        # 期刊需要获取刊号和年份
        if "journal".__eq__(str(ttype)):
            bsObj = getBsObj(task["toc-link"])
            if bsObj is None:
                logger.error("Get volume page error. " + task["toc-link"] + " " + officialName)
                continue
            try:
                bsMain = bsObj.body.find("div", {"id": "main"})
                bsHeader = bsMain.find("header", {"class": "h2"}, recursive=False)
                bsH2 = bsHeader.find("h2")
                if bsH2 is not None:
                    params = re.sub(r'[^,\d-]', '', bsH2.get_text()).split(",")
                    if len(params) >= 1:
                        task["volume"] = params[0].replace("/", "&")
                        if len(params) >= 2:
                            task["datePublished"] = params[-1].replace("/", "&")
            except Exception as e:
                logger.error("Get volume and datePublished error. " + task[
                    "toc-link"] + " " + officialName + "Details: " + e.__str__())
            jsonPath = folder + '/' + officialName + "_" + task["volume"] + ".json"
        else:
            jsonPath = folder + "/" + officialName + "_" + task["datePublished"] + ".json"

        print("Crawling " + jsonPath)

        url4bs = task["toc-link"]
        # 如果不是期刊，那对象还没被获取过
        if not "journal".__eq__(str(ttype)):
            bsObj = getBsObj(url4bs)
        if bsObj is None:
            logger.error("Failed to get url: " + url + " Details: " + officialName)
            continue
        try:
            bsThemeList = bsObj.body.find("div", {"id": "main"}).findAll("ul", {"class": "publ-list"})
            for theme in bsThemeList:
                if "journal".__eq__(str(ttype)):
                    bsItemList = theme.findAll("li", {"class": "entry article"})
                else:
                    bsItemList = theme.findAll("li", {"class": "entry inproceedings"})
                for item in bsItemList:
                    # 构建单个paper的json对象
                    paper = {}
                    authors = []
                    temp = item.cite.findAll("span", {"itemprop": "author"})
                    for aa in temp:
                        authors.append({'url': aa.a["href"], 'name': aa.a.span.get_text()})
                    bsLis = item.find("nav", {"class": "publ"}).find("ul").findAll("li", {"class": "drop-down"})
                    bsHead = bsLis[0].find("div", {"class": "head"})
                    if bsHead.find("a") is None:
                        # print("paper_url = None")
                        paper_url = "None"
                    else:
                        paper_url = bsHead.a["href"]
                        # print(paper_url)
                    paper["title"] = item.cite.find("span", {"class": "title"}).get_text()
                    paper["authors"] = authors

                    if "journal".__eq__(str(ttype)):
                        paper["journal"] = officialName
                        paper["volume"] = task["volume"]
                    else:
                        paper["conference"] = officialName
                        paper["publisher"] = task["publisher"]
                    bsDatePublished = item.cite.find("meta", {"itemprop": "datePublished"})
                    if bsDatePublished is None or bsDatePublished.find("content") is None:
                        paper["datePublished"] = "None"
                    else:
                        paper["datePublished"] = bsDatePublished["content"]
                    paper["doi"] = paper_url
                    papers.append(paper)
        except Exception as e:
            logger.error("Failed to Parse NoneType. " + jsonPath + " - " + officialName + " ""Details: " + e.__str__())
            continue
        saveJSON(papers, jsonPath)
        # logger.info("Success. " + jsonPath)
        papers.clear()
        with open('../logs/success.txt', 'a', encoding="utf-8") as file:
            file.write(task["toc-link"] + '\n')
