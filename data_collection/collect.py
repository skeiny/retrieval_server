import json
import os
import random
import re
import time
from urllib.request import urlopen
from selenium import webdriver
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
        bsCites = [item.find("cite", {"class": "input tts-content"}) for item in bsLis]
        tasks = [{"publisher": item.find("span", {"itemprop": "publisher"}).get_text().replace("/", "&"),
                  "datePublished": item.find("span", {"itemprop": "datePublished"}).get_text(),
                  "toc-link": item.find("a", {"class": "toc-link"}).get("href")} for item in bsCites]
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
    wait_time = random.uniform(1, 3)
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
    # 写入文件
    with open(jsonPath, "w") as f:
        json.dump(papers, f, indent=4)
    # 读出来看看
    with open(jsonPath, "r") as f:
        new_list = json.load(f)
        for item in new_list:
            print(item)


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
                params = re.sub(r'[^,\d-]', '', bsH2.get_text()).split(",")
                if len(params) >= 1:
                    task["volume"] = params[0]
                    if len(params) >= 2:
                        task["datePublished"] = params[-1]
            except Exception as e:
                logger.error("Get volume and datePublished error. " + task[
                    "toc-link"] + " " + officialName + "Details: " + e.__str__())
            jsonPath = folder + '/' + officialName + "_" + task["volume"] + "_" + task["datePublished"] + ".json"
        else:
            jsonPath = folder + "/" + officialName + "_" + task["datePublished"] + "_" + task["publisher"] + ".json"

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
                    paper_url = \
                        item.find("nav", {"class": "publ"}).find("ul").findAll("li", {"class": "drop-down"})[0].find(
                            "div",
                            {
                                "class": "head"}).a[
                            "href"]
                    paper["title"] = item.cite.find("span", {"class": "title"}).get_text()
                    paper["authors"] = authors
                    if "journal".__eq__(str(ttype)):
                        paper["journal"] = officialName
                        paper["volume"] = task["volume"]
                    else:
                        paper["conference"] = officialName
                    paper["datePublished"] = task["datePublished"]
                    paper["doi"] = paper_url
                    papers.append(paper)
        except BaseException as e:
            logger.error("Failed to Parse NoneType. " + jsonPath + " - " + officialName + " ""Details: " + e.__str__())
            continue
        saveJSON(papers, jsonPath)
        logger.info("Success. " + jsonPath)
        papers.clear()
        with open('../logs/success.txt', 'a', encoding="utf-8") as file:
            file.write(task["toc-link"] + '\n')
