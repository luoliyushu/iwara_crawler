#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整脚本：将所有 Selenium JSON 接口调用更新为“访问 API → 等待 JSON 渲染 → 提取并解析 JSON”的方式，
其他功能保持一致，并附有详细中文注释。
"""

import os
import sys
import json
import time
import random
import string
import shutil
import datetime
from urllib.parse import urlencode

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 自定义下载逻辑：需自行实现 download_file(url, filename, dir_username, headers, ...)
from mymodule import download_file

# 用户批量配置：username/file_prefix/download_index/profile_name/query
USER_INFO = [
    # {"user_name": "Forget Skyrim.", "profile_name": "forgetskyrim", "file_prefix": "Forget Skyrim", "download_index": ""},
    # {"user_name": "S10", "profile_name": "s10", "download_index": "", "file_prefix": ""},
    # {"user_name": "二两牛肉面JD", "profile_name": "user178752", "download_index": "", "file_prefix": ""},
    # {"user_name": "孤寡老音", "profile_name": "user1141804", "download_index": "", "file_prefix": ""},
    # {"user_name": "Cerodiers", "profile_name": "sanka", "file_prefix": "sanka", "download_index": ""},
    # {"user_name": "破砕姫", "profile_name": "user21650", "download_index": "", "file_prefix": ""},
    # {"user_name": "ViciNeko", "profile_name": "vicineko", "download_index": "", "file_prefix": ""},
    # {"user_name": "Juswe", "profile_name": "juswe", "download_index": "", "file_prefix": ""},
    # {"user_name": "kisaki", "profile_name": "user1263963", "download_index": "", "file_prefix": ""},
    # {"user_name": "Insect LOVE", "profile_name": "user1572781", "download_index": "", "file_prefix": ""},
    # {"user_name": "ADLER", "profile_name": "user2124413", "download_index": "", "file_prefix": ""},
    # {"user_name": "user15566", "profile_name": "user15566", "file_prefix": "sb5", "download_index": "32:"},
    # {"user_name": "mitsuboshiL", "profile_name": "mitsuboshil", "download_index": "2:", "file_prefix": ""},
    # {"user_name": "fengyunmomo", "profile_name": "fengyunmomo", "download_index": "", "file_prefix": ""},
    # {"user_name": "txwy", "profile_name": "txwy", "download_index": "", "file_prefix": ""},
    # {"user_name": "Arx_MMD", "profile_name": "arxmmd", "download_index": "", "file_prefix": ""},
    # {"user_name": "akomni", "profile_name": "akomni", "download_index": "44:", "file_prefix": ""},
    # {"user_name": "千种咲夜子", "profile_name": "user1866311", "download_index": "", "file_prefix": ""},
    # {"user_name": "xiangweitudou", "profile_name": "user1936430", "download_index": "", "file_prefix": ""},
    # {"user_name": "PastaPaprika", "profile_name": "pastapaprika", "download_index": "", "file_prefix": ""},
    # {"user_name": "10yue", "profile_name": "10yue", "download_index": "", "file_prefix": ""},
    # {"user_name": "ダンリック", "profile_name": "user8160", "download_index": "", "file_prefix": ""},
    # {"user_name": "lovely416", "profile_name": "zehk416", "download_index": "", "file_prefix": ""},
    # {"user_name": "在下神奈有何贵干", "profile_name": "user1851714", "download_index": "", "file_prefix": ""},
    # {"user_name": "kemkem", "profile_name": "kemkem", "download_index": "", "file_prefix": ""},
    # {"user_name": "ReHaku", "profile_name": "rehaku", "download_index": "", "file_prefix": ""},
    # {"user_name": "iskanime", "profile_name": "iskanime", "download_index": "", "file_prefix": ""},
    # {"user_name": "tuiwannian", "profile_name": "user221116", "download_index": "700:", "file_prefix": ""},
    # {"user_name": "煜喵", "profile_name": "user1107866", "download_index": "60:", "file_prefix": ""},
    # {"user_name": "盐焗鸡", "profile_name": "598456851", "download_index": "", "file_prefix": ""},
    # {"user_name": "RuaaaD", "profile_name": "ruaaad", "download_index": "", "file_prefix": "好想摸鱼"},
    {"user_name": "LikeHugeB", "profile_name": "user3207206", "download_index": "", "file_prefix": ""},
    # {"user_name": "天平キツネ", "profile_name": "extrafoxes", "download_index": "", "file_prefix": ""},
    # {"user_name": "Cloudsea Castle", "profile_name": "cloudseacastle", "download_index": "", "file_prefix": ""},
    # # # -----------------------------------------------------------
    # # # 整活（时间停止、催眠、绅士之手）
    # {"user_name": "QNR", "profile_name": "qnr", "download_index": "30:", "file_prefix": ""},
    # {"user_name": "Unlimited EcchiMMD Works", "profile_name": "11556621", "download_index": "", "file_prefix": ""},
    # {"user_name": "yokujitsu@ヨクジツ", "profile_name": "yokujitsu", "download_index": "", "file_prefix": ""},
    # {"user_name": "noneferoero", "profile_name": "noneferoero", "download_index": "", "file_prefix": ""},
    # {"user_name": "yafrmmd", "profile_name": "yafrmmd", "download_index": "", "file_prefix": ""},
    # {"user_name": "sodeno19", "profile_name": "sodeno19", "download_index": "", "file_prefix": ""},
    # {"user_name": "Garnet2020", "profile_name": "garnet2020", "download_index": "", "file_prefix": ""},
    # {"user_name": "xiaodidi09", "profile_name": "xiaodidi09", "download_index": "", "file_prefix": ""},
    # {"user_name": "mox", "profile_name": "mox", "download_index": "", "file_prefix": ""},
    # {"user_name": "Arisananades", "profile_name": "Arisananades", "download_index": "", "file_prefix": ""},
    # {"user_name": "kuronekorin", "profile_name": "kuronekorin", "download_index": "", "file_prefix": ""},
    # {"user_name": "curvylonix", "profile_name": "curvylonix", "download_index": "", "file_prefix": ""},
    {"user_name": "sola", "profile_name": "user2501342", "download_index": "", "file_prefix": ""},
    # # -----------------------------------------------------------
    # # 淫词艳曲
    {"user_name": "琉璃狐", "profile_name": "user724850", "download_index": "", "file_prefix": ""},
    {"user_name": "YZLZ", "profile_name": "yzlzhhzwty", "download_index": "", "file_prefix": ""},
    {"user_name": "粉红色猫猫头", "profile_name": "user205029", "download_index": "", "file_prefix": ""},
    {"user_name": "整夜下雪", "profile_name": "user340036", "download_index": "", "file_prefix": ""},
    # # -----------------------------------------------------------
    {"user_name": "水水..", "profile_name": "user937858", "file_prefix": "水水..a", "download_index": "305:"},
    {"user_name": "qishi", "profile_name": "qishi", "download_index": "264:", "file_prefix": ""},
    {"user_name": "LTDEND", "profile_name": "ltdend", "download_index": "236:", "file_prefix": ""},
    # # -----------------------------------------------------------
    # # R18的很少
    {"user_name": "骑着牛儿追织女", "profile_name": "user1528210", "download_index": "", "file_prefix": ""},
    # # -----------------------------------------------------------
    # # # 搜索，使用|代表or搜索模式
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "ハンド", "query": "ハンド|gentleman hand"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "標識", "query": "標識|ero sign|sign strip|hentai sign"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "時間停止", "query": "時間 停止|time stop|时间 停止|时停|時停"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "紳士枠", "query": "枠|透視|框|透视"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "DATEN_ROUTE", "query": "DATEN"},
]

# 全局常量
DATE_LIMIT = 0    # 天数限制：0 表示不限制，>0 表示只下载近 N 天的视频
PROXIES = {}      # 如需代理，填入 HTTP/HTTPS 配置
IWARA_HOME = "https://www.iwara.tv/"
IWARA_API  = "https://api.iwara.tv/"
ERROR_LOG  = os.path.join(os.path.dirname(__file__), 'error_list.txt')
TIMEOUT_SEC = 40

# ------------------------------------------------------------------------------
def get_token():
    """
    获取本地 token：
      1. 如果不存在 token.json，则启动带 UA 的浏览器到登录页，人工扫码或自动登录后
         从 localStorage 读取 token 并保存到 token.json
      2. 已存在则直接读取 token.json
    返回：user_agent, token
    """
    if not os.path.exists("token.json"):
        ua = UserAgent().random
        opts = webdriver.ChromeOptions()
        opts.add_argument(f"--user-agent={ua}")
        if "http" in PROXIES:
            opts.add_argument(f"--proxy-server={PROXIES['http'].replace('http://','')}")
        driver = webdriver.Chrome(service=ChromeService("./chromedriver.exe"), options=opts)
        driver.get(IWARA_HOME + "login")
        # 等待 localStorage 存入 token
        while True:
            token = driver.execute_script("return window.localStorage.getItem('token');")
            if token:
                break
            time.sleep(1 + random.random() * 2)
        driver.quit()
        # 写入 token.json
        with open("token.json", "w", encoding="utf-8") as f:
            json.dump({"user_agent": ua, "token": token}, f, indent=2)
    else:
        cfg = json.load(open("token.json", encoding="utf-8"))
        ua    = cfg["user_agent"]
        token = cfg["token"]
    return ua, token

# ------------------------------------------------------------------------------
def init_selenium_session(user_agent: str):
    """
    初始化 Selenium ChromeDriver 用于 API 请求
      - headless 模式，设置语言和 UA
      - 隐藏 AutomationControlled 特征，注入 stealth 脚本
      - 导航到 IWARA_HOME，注入 token 到 localStorage
    返回：已登录注入 token 的 driver
    """
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--lang=zh")
    opts.add_argument(f"--user-agent={user_agent}")
    if "http" in PROXIES:
        opts.add_argument(f"--proxy-server={PROXIES['http'].replace('http://','')}")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=ChromeService("./chromedriver.exe"), options=opts)

    # region 隐藏爬虫特征：在每个新文档里注入 stealth.min.js
    with open('./stealth.min.js', 'r', encoding='utf-8') as f:
        stealth_js = f.read()
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": stealth_js
    })
    # endregion

    # 导航到主站，保持同源上下文
    driver.get(IWARA_HOME)
    # 注入 token 和 ecchi 标记到 localStorage
    token = json.load(open("token.json", encoding="utf-8"))["token"]
    driver.execute_script(f"window.localStorage.setItem('token','{token}');")
    driver.execute_script("window.localStorage.setItem('ecchi','1');")

    return driver

# ------------------------------------------------------------------------------
def selenium_api_get_json(driver, url: str, params: dict = None, headers: dict = None):
    """
    用 Selenium 访问 API 并获取 JSON，分三步：
      1. 访问 API：使用 CDP 设置额外请求头后，driver.get(full_url)
      2. 等待 JSON 渲染：等待 <body> 出现花括号文本
      3. 提取并解析 JSON：取出 body.text 并 json.loads
    返回：Python 原生对象（dict/list）
    """
    # 如果当前不在 iwara.tv 同源上下文，先导航到主站
    if not (driver.current_url.startswith(IWARA_HOME) or
            driver.current_url.startswith(IWARA_API)):
        driver.get(IWARA_HOME)

    # 构造完整 URL（拼接查询参数）
    full_url = url
    if params:
        qs = urlencode(params)
        full_url = f"{url}?{qs}"

    # 1. 访问 API：先启用 Network 并注入请求头
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
    driver.get(full_url)

    # 2. 等待 JSON 渲染：body.text 以 { 开头即视为完成
    try:
        WebDriverWait(driver, TIMEOUT_SEC).until(
            lambda d: d.find_element(By.TAG_NAME, "body").text.strip().startswith("{")
        )
    except TimeoutException:
        raise RuntimeError(f"JSON 渲染超时: {full_url}")

    # 3. 提取并解析 JSON
    raw = driver.find_element(By.TAG_NAME, "body").text
    try:
        result = json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"JSON 解析失败: {e}\nRaw Text: {raw[:200]}...")
    return result

# ------------------------------------------------------------------------------
def download_file_with_progress(url, filename, dir_username):
    """
    Selenium + 本地下载目录方式下载视频文件
    """
    root = os.path.join(os.path.dirname(__file__), "tmp_dir")
    rand = "".join(random.choices(string.ascii_lowercase, k=8))
    tmp = os.path.join(root, rand)
    os.makedirs(tmp, exist_ok=True)

    opts = webdriver.ChromeOptions()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--lang=zh")
    opts.add_experimental_option("prefs", {
        "download.default_directory": tmp,
    })
    if "http" in PROXIES:
        opts.add_argument(f"--proxy-server={PROXIES['http'].replace('http://','')}")
    ua, token = get_token()
    opts.add_argument(f"--user-agent={ua}")
    opts.add_argument("--headless=new")

    with webdriver.Chrome(service=ChromeService("./chromedriver.exe"), options=opts) as dl_drv:
        # 注入 token

        # region 隐藏爬虫特征：在每个新文档里注入 stealth.min.js
        with open('./stealth.min.js', 'r', encoding='utf-8') as f:
            stealth_js = f.read()
        dl_drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": stealth_js
        })
        # endregion
        
        dl_drv.get(IWARA_HOME)
        dl_drv.execute_script(f"window.localStorage.setItem('token','{token}');")
        dl_drv.execute_script("window.localStorage.setItem('ecchi','1');")
        # 跳转到视频页面，等待下载按钮
        dl_drv.get(url)
        try:
            btn = WebDriverWait(dl_drv, TIMEOUT_SEC).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".downloadButton"))
            )
        except TimeoutException:
            print("下载按钮超时")
            return False

        parent = btn.find_element(By.XPATH, "./../..")
        links = parent.find_elements(By.CSS_SELECTOR, ".dropdown__content li a")
        target = None
        for a in links:
            txt = a.get_attribute("innerHTML")
            if txt in ("Source", "540"):
                target = a.get_attribute("href")
                break
        if not target:
            print("未找到下载链接")
            return False

        ok = download_file(
            target, filename, dir_username,
            headers={"User-Agent": ua, "Authorization": f"Bearer {token}"},
            max_retries=60, max_download_seconds=TIMEOUT_SEC, max_filename_length=50
        )
        shutil.rmtree(tmp, ignore_errors=True)
        return ok in ['下载成功', '下载成功，但文件大小未知']

# ------------------------------------------------------------------------------
def main(driver, headers, user_name, file_prefix, download_index,
         profile_name=None, query=None):
    """
    主流程：
      1. 获取 user_id（profile 或 search）
      2. 翻页拉取视频列表
      3. 按 download_index 筛选
      4. 依次调用 download_file_with_progress 下载
    """
    open(ERROR_LOG, 'w', encoding='utf-8').close()

    # 1. 获取 user_id
    if not query:
        api = f"{IWARA_API}profile/{profile_name or user_name}"
        resp = selenium_api_get_json(driver, api, headers=headers)
        if resp.get("message") == "errors.notFound":
            s = selenium_api_get_json(
                driver, IWARA_API + "search",
                params={"type": "user", "query": user_name, "page": 0},
                headers=headers
            )
            if not s.get("results"):
                print("用户不存在，跳过")
                return
            api  = f"{IWARA_API}profile/{s['results'][0]['username']}"
            resp = selenium_api_get_json(driver, api, headers=headers)
        user_id = resp["user"]["id"]
    else:
        user_id = None

    # 2. 拉取视频列表
    video_list = []
    if not query:
        page, count = 0, 1
        while page * 32 <= count:
            j = selenium_api_get_json(
                driver, IWARA_API + "videos",
                params={"user": user_id, "sort": "date", "page": page},
                headers=headers
            )
            count = j.get("count", 0)
            for itm in j.get("results", []):
                ct   = datetime.datetime.strptime(itm["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                slug = itm.get("slug") or ""
                url  = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                video_list.append({"url": url, "title": itm["title"], "create_time": ct})
            page += 1
    else:
        seen = set()
        for kw in query.split("|"):
            page, count = 0, 1
            while page * 32 <= count:
                j = selenium_api_get_json(
                    driver, IWARA_API + "search",
                    params={"type": "video", "query": kw, "page": page},
                    headers=headers
                )
                count = j.get("count", 0)
                for itm in j.get("results", []):
                    ct   = datetime.datetime.strptime(itm["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    slug = itm.get("slug") or ""
                    url  = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                    key  = (itm["id"], slug)
                    if key in seen:
                        continue
                    seen.add(key)
                    video_list.append({"url": url, "title": itm["title"], "create_time": ct})
                page += 1

    # 倒序排序并打 index
    video_list.sort(key=lambda x: x["create_time"])
    for idx, v in enumerate(video_list, 1):
        v["index"] = idx
        print(f"{idx:3d} | {v['title']} | {v['create_time']}")

    # 3. 根据 download_index 构建下载列表
    download_list = []
    if isinstance(download_index, str):
        if download_index.endswith(":"):
            start = int(download_index[:-1]) - 1
            download_list = video_list[start:]
        else:
            download_list = video_list[:]
    elif isinstance(download_index, list) and download_index:
        for i in download_index:
            if 1 <= i <= len(video_list):
                download_list.append(video_list[i - 1])
    else:
        download_list = video_list[:]

    # 4. 循环下载
    success_list, error_list = [], []
    base_dir = "downloads"
    for v in download_list:
        idx    = v["index"]
        prefix = file_prefix or user_name or query or "视频"
        fn     = f"{prefix}.{idx:03d}.{v['title']}.mp4"
        fn     = fn.translate(str.maketrans({
            "\\": "——", "/": " ", ":": "：", "*": " ", "?": " ",
            "\"": "”", "<": "《", ">": "》", "|": "！"
        }))
        user_dir = file_prefix or user_name or query or "视频"
        if query and "[搜索]" not in user_dir:
            user_dir = "[搜索]" + user_dir
        save_dir = os.path.join(base_dir, user_dir)
        os.makedirs(save_dir, exist_ok=True)

        dest = os.path.join(save_dir, fn)
        if os.path.exists(dest) or os.path.exists(dest + ".lnk"):
            print(f"{idx:3d} 已存在，跳过")
            continue

        print(f"{idx:3d} 开始下载 → {dest}")
        ok = download_file_with_progress(v["url"], fn, save_dir)
        if ok:
            print(f"{idx:3d} 下载成功")
            success_list.append(fn)
        else:
            print(f"{idx:3d} 下载失败")
            with open(ERROR_LOG, 'a', encoding='utf-8') as ef:
                ef.write(f"{fn} 下载失败，URL: {v['url']}\n")
            error_list.append(fn)

    # 打印汇总
    if success_list:
        print("下载成功列表:")
        for x in success_list:
            print("   ", x)
    if error_list:
        print("下载失败列表:")
        for x in error_list:
            print("   ", x)

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # 1. 获取 token 和 UA
    ua, token = get_token()
    headers = {
        "User-Agent": ua,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    # 2. 启动 Selenium 会话
    driver = init_selenium_session(ua)
    # 3. 批量处理
    for u in USER_INFO:
        print("=" * 60)
        main(driver, headers,
             u.get("user_name", ""),
             u.get("file_prefix", ""),
             u.get("download_index", ""),
             profile_name=u.get("profile_name"),
             query=u.get("query"))
        print("")
    # 4. 退出
    driver.quit()
