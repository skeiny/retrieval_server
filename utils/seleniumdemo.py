from selenium import webdriver
import time
from bs4 import BeautifulSoup

# 启动浏览器模拟
driver = webdriver.Chrome()

# 访问目标网站
url = "https://dblp.uni-trier.de/db/conf/ppopp/index.html"  # 替换为目标网站的URL
driver.get(url)

# 等待一定时间，例如等待5秒
time.sleep(10)

# 获取页面源代码
page_source = driver.page_source

# 关闭浏览器
driver.quit()

# 使用Beautiful Soup解析页面
cBsObj = BeautifulSoup(page_source, 'lxml')
bsUls = cBsObj.body.find("div", {"id": "main"}).findAll("ul", {"class": "publ-list"})
        # bsLis = [item.find("li", {"class": "entry editor toc"}) for item in bsUls]
bsLis = [li for ul in bsUls for li in ul.findAll("li", {"class": "entry editor toc"})]
bsCites = [item.find("cite", {"class": "data tts-content"}) for item in bsLis]
tasks = [{"publisher": item.find("span", {"itemprop": "publisher"}).get_text().replace("/", "&"),
          "datePublished": item.find("span", {"itemprop": "datePublished"}).get_text(),
          "toc-link": item.find("a", {"class": "toc-link"}).get("href")} for item in bsCites]
print(tasks)
