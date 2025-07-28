#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整脚本：将所有 requests.get 调用替换为 Selenium fetch (execute_async_script)，
其他功能保持一致，并做了少许优化和详细中文注释。
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
from requests.exceptions import SSLError

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
DATE_LIMIT = 0  # 天数限制：0 表示不限制，>0 表示只下载近 N 天的视频
PROXIES = {
    # 若需走代理，请取消注释并填写
    # "http": "http://127.0.0.1:8080",
    # "https": "http://127.0.0.1:8080",
}
IWARA_HOME = "https://www.iwara.tv/"
IWARA_API = "https://api.iwara.tv/"
# 脚本同级目录下的错误日志文件
ERROR_LOG = os.path.join(os.path.dirname(__file__), 'error_list.txt')

# ------------------------------------------------------------------------------
def get_token():
    """
    1. 用 Selenium 登录 iwara.tv，获取 localStorage 中的 token 并保存到 token.json
    2. 已存在 token.json 则直接读取
    返回：user_agent, token
    """
    if not os.path.exists("token.json"):
        # 第一次登录：随机 UA，打开浏览器，人工扫码登录或自动登录
        ua = UserAgent()
        user_agent = ua.random
        options = webdriver.ChromeOptions()
        options.add_argument(f"--user-agent={user_agent}")
        if "http" in PROXIES:
            options.add_argument(f"--proxy-server={PROXIES['http'].replace('http://','')}")
        driver = webdriver.Chrome(service=ChromeService("./chromedriver.exe"),
                                   options=options)
        driver.get(IWARA_HOME + "login")
        # 等待 localStorage 存入 token
        while True:
            token = driver.execute_script(
                "return window.localStorage.getItem('token');"
            )
            if token:
                break
            time.sleep(1 + random.random() * 2)
        driver.quit()
        # 保存 token.json
        with open("token.json", "w", encoding="utf-8") as f:
            json.dump({"user_agent": user_agent, "token": token}, f, indent=2)
    else:
        # 读取 token.json
        cfg = json.load(open("token.json", encoding="utf-8"))
        user_agent = cfg["user_agent"]
        token = cfg["token"]
    return user_agent, token

# ------------------------------------------------------------------------------
def init_selenium_session(user_agent: str):
    """
    初始化一个 Selenium ChromeDriver 实例，用于后续所有 API JSON 请求。
    这里主动导航到 IWARA_HOME，保证后续 fetch 都在正确的同源上下文执行，
    避免 “Failed to fetch” 的 CORS 问题。
    """
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--lang=zh")
    opts.add_argument(f"--user-agent={user_agent}")
    if "http" in PROXIES:
        opts.add_argument(f"--proxy-server={PROXIES['http'].replace('http://','')}")
    # 禁用 Blink 的 AutomationControlled 特征，绕过简单的自动化检测
    opts.add_argument("--disable-blink-features=AutomationControlled")
    # 可选：去掉 “enable-automation” 提示条，并关闭自动化扩展
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=ChromeService("./chromedriver.exe"),
                              options=opts)
    # region 隐藏爬虫特征
    with open('./stealth.min.js') as f:
        inject_js = f.read()
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": inject_js 
    })
    # endregion
    # 导航到 i-wara 主站，让浏览器上下文落在 https://www.iwara.tv
    driver.get(IWARA_HOME)
    # 把 token 注入到 localStorage
    token = json.load(open("token.json", encoding="utf-8"))["token"]
    driver.execute_script(f"window.localStorage.setItem('token','{token}');")
    driver.execute_script("window.localStorage.setItem('ecchi','1');")
    return driver

# ------------------------------------------------------------------------------
def selenium_api_get_json(driver, url: str, params: dict = None, headers: dict = None):
    """
    用 Selenium fetch API 请求 JSON 并返回 Python 对象
      - 先确保 driver.current_url 是 https://www.iwara.tv 或 https://api.iwara.tv
      - 再 execute_async_script 执行 fetch，带上 Authorization header
    """
    # 如果当前不在同源上下文，重定向一次
    if not driver.current_url.startswith(IWARA_HOME) and \
       not driver.current_url.startswith(IWARA_API):
        driver.get(IWARA_HOME)

    # 构造完整 URL
    full_url = url
    if params:
        qs = urlencode(params)
        full_url = f"{url}?{qs}"

    # Async fetch 脚本，最后一个参数是 Selenium 的 callback
    fetch_script = """
    const [url, headers, callback] = arguments;
    fetch(url, {
      method: 'GET',
      headers: headers,
      credentials: 'same-origin'
    })
      .then(res => {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      })
      .then(obj => callback(JSON.stringify(obj)))
      .catch(err => callback(JSON.stringify({__err: err.toString()})));
    """

    raw = driver.execute_async_script(fetch_script, full_url, headers)
    result = json.loads(raw)

    if isinstance(result, dict) and "__err" in result:
        # 把浏览器脚本里的错误抛出来，方便定位
        raise RuntimeError(f"Fetch 错误: {result['__err']}")

    return result

# ------------------------------------------------------------------------------
def download_file_with_progress(url, filename, dir_username):
    """
    Selenium + 本地下载目录方式：保留原 download_file 逻辑
    只做了一个拼写修正：add_experimental_option
    """
    # 创建临时下载目录
    root = os.path.join(os.path.dirname(__file__), "tmp_dir")
    # 生成随机子目录
    rand = "".join(random.choices(string.ascii_lowercase, k=8))
    tmp = os.path.join(root, rand)
    os.makedirs(tmp, exist_ok=True)

    # Selenium options：设置下载目录
    opts = webdriver.ChromeOptions()
    opts.add_argument("--lang=en-US")
    opts.add_experimental_option("prefs", {
        "download.default_directory": tmp,
    })
    if "http" in PROXIES:
        opts.add_argument(f"--proxy-server={PROXIES['http'].replace('http://','')}")
    ua, token = get_token()
    opts.add_argument(f"--user-agent={ua}")
    opts.add_argument("--headless=new")

    # 启动专用下载 driver
    with webdriver.Chrome(service=ChromeService("./chromedriver.exe"), options=opts) as driver:
        # 登录 localStorage
        driver.get(IWARA_HOME)
        driver.execute_script(f"window.localStorage.setItem('token','{token}')")
        driver.execute_script("window.localStorage.setItem('ecchi','1')")
        # 跳转视频页面，等待元素加载
        driver.get(url)
        # 等待下载按钮出现
        try:
            dl_btn = WebDriverWait(driver, 40).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".downloadButton"))
            )
        except TimeoutException:
            print("下载元素超时")
            return False

        # 点击下拉，提取 Source / 540 链接
        dl_parent = dl_btn.find_element(By.XPATH, "./../..")
        dl_list = dl_parent.find_elements(By.CSS_SELECTOR, ".dropdown__content li a")
        target_url = None
        for a in dl_list:
            txt = a.get_attribute("innerHTML")
            if txt in ("Source", "540"):
                target_url = a.get_attribute("href")
                break
        if not target_url:
            print("未找到下载链接")
            return False

        # 调用外部 download_file 完成下载
        ok = download_file(
            target_url, filename, dir_username,
            headers={"User-Agent": ua, "Authorization": f"Bearer {token}"},
            max_retries=60, max_download_seconds=40, max_filename_length=50
        )
        # 下载完成后清理临时目录
        shutil.rmtree(tmp, ignore_errors=True)
        return ok in ['下载成功', '下载成功，但文件大小未知']

# ------------------------------------------------------------------------------
def main(driver, headers, user_name, file_prefix, download_index,
         profile_name=None, query=None):
    """
    主流程：
      1. 根据 profile_name/user_name 调用 profile API，获取 user_id
      2. 根据 user_id 或 query 调用 videos/search API，生成 video_list
      3. 按 download_index 筛选下载项
      4. 依次调用 download_file_with_progress 完成下载
    """
    # 启动时清空老的 error_list.txt（可选，也可以保留历史）
    open(ERROR_LOG, 'w', encoding='utf-8').close()
    # 1. 获取 user_id
    if not query:
        api = f"{IWARA_API}profile/{profile_name or user_name}"
        print(f"Profile 请求: {api}")
        resp = selenium_api_get_json(driver, api, headers=headers)
        # 如果未找到，使用 search 查
        if resp.get("message") == "errors.notFound":
            print("Profile 未找到，尝试搜索")
            s = selenium_api_get_json(driver, IWARA_API + "search",
                                      params={"type": "user", "query": user_name, "page": 0},
                                      headers=headers)
            if not s.get("results"):
                print("用户不存在，跳过")
                return
            api = f"{IWARA_API}profile/{s['results'][0]['username']}"
            resp = selenium_api_get_json(driver, api, headers=headers)
        user_id = resp["user"]["id"]
    else:
        user_id = None

    # 2. 获取视频列表
    video_list = []
    if not query:
        # 按用户视频列表翻页
        page = 0
        count = 1
        while page * 32 <= count:
            j = selenium_api_get_json(
                driver, IWARA_API + "videos",
                params={"user": user_id, "sort": "date", "page": page},
                headers=headers
            )
            count = j.get("count", 0)
            for itm in j.get("results", []):
                ct = datetime.datetime.strptime(itm["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                slug = itm.get("slug") or ""
                url = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                video_list.append({
                    "url": url, "title": itm["title"], "create_time": ct
                })
            page += 1
    else:
        # 搜索关键词时支持 or 模式
        seen = set()
        for kw in query.split("|"):
            page = 0; count = 1
            while page * 32 <= count:
                j = selenium_api_get_json(
                    driver, IWARA_API + "search",
                    params={"type": "video", "query": kw, "page": page},
                    headers=headers
                )
                count = j.get("count", 0)
                for itm in j.get("results", []):
                    ct = datetime.datetime.strptime(itm["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    slug = itm.get("slug") or ""
                    url = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                    key = (itm["id"], slug)
                    if key in seen:
                        continue
                    seen.add(key)
                    video_list.append({
                        "url": url, "title": itm["title"], "create_time": ct
                    })
                page += 1

    # 按时间倒序，打 index
    video_list.sort(key=lambda x: x["create_time"])
    for idx, v in enumerate(video_list, 1):
        v["index"] = idx
        print(f"{idx:3d} | {v['title']} | {v['create_time']}")

    # 3. 根据 download_index 构造 download_list
    download_list = []
    if isinstance(download_index, str):
        if download_index.endswith(":"):
            start = int(download_index[:-1]) - 1
            download_list = video_list[start:]
        elif download_index == "":
            download_list = video_list[:]
    elif isinstance(download_index, list) and download_index:
        for i in download_index:
            if i > 0 and i <= len(video_list):
                download_list.append(video_list[i - 1])
            elif i < 0 and abs(i) <= len(video_list):
                download_list.append(video_list[i])
    else:
        print("download_index 类型异常，全部下载")
        download_list = video_list[:]

    # 4. 循环下载
    success_list = []
    error_list = []
    base_dir = "downloads"
    for v in download_list:
        idx = v["index"]
        prefix = file_prefix or user_name or query or "视频"
        filename = f"{prefix}.{idx:03d}.{v['title']}.mp4"
        # 文件名过滤非法字符
        filename = filename.translate(str.maketrans({
            "\\": "——", "/": " ", ":": "：", "*": " ", "?": " ",
            "\"": "”", "<": "《", ">": "》", "|": "！"
        }))
        # 存储目录
        dir_user = file_prefix or user_name or query or "视频"
        if query and "[搜索]" not in dir_user:
            dir_user = "[搜索]" + dir_user
        save_dir = os.path.join(base_dir, dir_user)
        os.makedirs(save_dir, exist_ok=True)

        # 已存在则跳过：如果文件或同名 .lnk 快捷方式已存在
        dest_path = os.path.join(save_dir, filename)
        if os.path.exists(dest_path) or os.path.exists(dest_path + ".lnk"):
            print(f"{idx:3d} 已存在，跳过")
            continue

        print(f"{idx:3d} 开始下载 → {dest_path}")
        ok = download_file_with_progress(v["url"], filename, save_dir)
        if ok:
            print(f"{idx:3d} 下载成功")
            success_list.append(filename)
        else:
            print(f"{idx:3d} 下载失败")
            # 追加写入 error_list.txt
            try:
                with open(ERROR_LOG, 'a', encoding='utf-8') as ef:
                    ef.write(f"{filename} 下载失败，URL: {v['url']}\n")
            except Exception as e:
                print(f"写入错误日志失败: {e}")
            error_list.append(filename)

    # 打印结果汇总
    if success_list:
        print("下载成功列表:")
        for x in success_list:
            print("  ", x)
    if error_list:
        print("下载失败列表:")
        for x in error_list:
            print("  ", x)


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
    # 3. 批量处理用户或搜索
    for u in USER_INFO:
        print("=" * 60)
        main(driver, headers,
             u.get("user_name", ""),
             u.get("file_prefix", ""),
             u.get("download_index", ""),
             profile_name=u.get("profile_name"),
             query=u.get("query"))
        print("")

    # 4. 退出 Selenium
    driver.quit()
