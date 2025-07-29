#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整脚本：在原有 undetected-chromedriver + Selenium 框架上
增加 Cookie 注入与全局请求头支持，并实现以下功能：
 1. 每翻一页列表后随机 sleep 2～6 秒
 2. 如果目标文件或同名 .lnk 快捷方式已存在则跳过下载
 3. 若走搜索分支，存放文件的父级目录命名为 "[搜索]"+file_prefix
 4. 列表打印时，用单空格分隔标题与时间
 5. undetected-chromedriver 会话与下载会话都全局注入自定义 headers

其他功能（扫码登录、token/cookie 缓存、本地下载逻辑）保持不变
详细中文注释，拷贝即用
"""

import os
import json
import time
import random
import datetime
from urllib.parse import urlencode

from fake_useragent import UserAgent
import undetected_chromedriver as uc  # 隐藏 Selenium 自动化特征

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 自定义下载函数，需要自行实现 download_file(...)
from mymodule import download_file

# ---------------- 用户批量配置 ----------------
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
    # {"user_name": "LikeHugeB", "profile_name": "user3207206", "download_index": "", "file_prefix": ""},
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
    # {"user_name": "sola", "profile_name": "user2501342", "download_index": "", "file_prefix": ""},
    # # # -----------------------------------------------------------
    # # # 淫词艳曲
    # {"user_name": "琉璃狐", "profile_name": "user724850", "download_index": "", "file_prefix": ""},
    # {"user_name": "YZLZ", "profile_name": "yzlzhhzwty", "download_index": "", "file_prefix": ""},
    # {"user_name": "粉红色猫猫头", "profile_name": "user205029", "download_index": "", "file_prefix": ""},
    # {"user_name": "整夜下雪", "profile_name": "user340036", "download_index": "", "file_prefix": ""},
    # # # -----------------------------------------------------------
    # {"user_name": "水水..", "profile_name": "user937858", "file_prefix": "水水..a", "download_index": "305:"},
    # {"user_name": "qishi", "profile_name": "qishi", "download_index": "264:", "file_prefix": ""},
    # {"user_name": "LTDEND", "profile_name": "ltdend", "download_index": "236:", "file_prefix": ""},
    # # # -----------------------------------------------------------
    # # # R18的很少
    # {"user_name": "骑着牛儿追织女", "profile_name": "user1528210", "download_index": "", "file_prefix": ""},
    # # -----------------------------------------------------------
    # # # 搜索，使用|代表or搜索模式
    {"user_name": "", "profile_name": "", "download_index": "323:",
        "file_prefix": "ハンド", "query": "ハンド|gentleman hand"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "標識", "query": "標識|ero sign|sign strip|hentai sign"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "時間停止", "query": "時間 停止|time stop|时间 停止|时停|時停"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "紳士枠", "query": "枠|透視|框|透视"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "DATEN_ROUTE", "query": "DATEN"},
]

# ---------------- 全局常量 ----------------
IWARA_HOME = "https://www.iwara.tv/"
IWARA_API = "https://api.iwara.tv/"
TOKEN_FILE = "token.json"
ERROR_LOG = "error_list.txt"
TIMEOUT_SEC = 60
PROXIES = {}               # 如需代理填{"http":"...","https":"..."}

# --------------------------------------------------


def get_token_and_cookie():
    """
    获取并缓存 Iwara 登录 token + 浏览器 cookies：
      1. 本地无 token.json 时，启动带界面 Chrome 扫码登录
      2. 登录后读取 localStorage.token
      3. 读取 driver.get_cookies() 并拼成单行 Cookie 头
      4. 保存到 token.json：{"user_agent":..., "token":..., "cookie": "..."}
      5. 本地有文件时直接读取并返回
    返回：(user_agent, token, cookie_header)
    """
    if not os.path.exists(TOKEN_FILE):
        # 随机 UA
        ua = UserAgent().random
        opts = uc.ChromeOptions()
        opts.headless = False
        opts.add_argument(f"--user-agent={ua}")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        if PROXIES.get("http"):
            opts.add_argument(f"--proxy-server={PROXIES['http']}")

        # 启动有界面浏览器扫码登录
        driver = uc.Chrome(
            options=opts, driver_executable_path="./chromedriver.exe")
        driver.get(IWARA_HOME + "login")
        print("→ 请扫码登录 Iwara …")

        # 等待 localStorage.token 写入
        token = None
        while not token:
            token = driver.execute_script(
                "return window.localStorage.getItem('token');")
            time.sleep(1 + random.random())

        # 读取所有 cookie 并拼成字符串
        raw = driver.get_cookies()
        driver.quit()
        pairs = [f"{c['name']}={c['value']}" for c in raw]
        cookie_header = "; ".join(pairs)

        # 缓存到本地
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "user_agent": ua,
                "token":      token,
                "cookie":     cookie_header
            }, f, indent=2)

    cfg = json.load(open(TOKEN_FILE, encoding="utf-8"))
    return cfg["user_agent"], cfg["token"], cfg["cookie"]

# --------------------------------------------------


def init_uc_session(user_agent: str, headers: dict):
    """
    初始化 undetected-chromedriver 会话，用于 API 请求：
      - headless=False 以便注入 localStorage
      - 设置 UA、隐藏自动化特征
      - 全局注入自定义 headers
      - 注入 token & ecchi 标记
    返回：就绪的 driver
    """
    opts = uc.ChromeOptions()
    opts.headless = True
    opts.add_argument(f"--user-agent={user_agent}")
    opts.add_argument("--lang=zh-CN")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    if PROXIES.get("http"):
        opts.add_argument(f"--proxy-server={PROXIES['http']}")

    driver = uc.Chrome(
        options=opts, driver_executable_path="./chromedriver.exe")

    # 启用 Network 并注入全局 headers
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})

    # 打开首页，同源注入 token/ecchi
    driver.get(IWARA_HOME)
    driver.execute_script(
        f"window.localStorage.setItem('token','{headers['Authorization'].split()[1]}');")
    driver.execute_script("window.localStorage.setItem('ecchi','1');")

    return driver

# --------------------------------------------------


def selenium_api_get_json(
    driver, url: str, params: dict = None, headers: dict = None,
    retries: int = 30, retry_delay: tuple = (2, 4)
):
    """
    用 Selenium/CDP 访问 API 并获取 JSON：
      - 拼 full_url
      - 执行 driver.get(full_url)
      - 等待 <body> 以 "{" 开头
      - 失败重试，页间 sleep
    """
    for attempt in range(1, retries + 1):
        try:
            # 确保同源主站
            if not driver.current_url.startswith(IWARA_HOME):
                driver.get(IWARA_HOME)

            full_url = url + ("?" + urlencode(params) if params else "")
            driver.get(full_url)
            WebDriverWait(driver, TIMEOUT_SEC).until(
                lambda d: d.find_element(By.TAG_NAME, "body")
                .text.strip().startswith("{")
            )
            return json.loads(driver.find_element(By.TAG_NAME, "body").text)

        except Exception as e:
            print(f"[Fetch JSON] 重试 {attempt}/{retries}，错误: {e}")
            if attempt == retries:
                raise
            time.sleep(random.uniform(*retry_delay))

# --------------------------------------------------


def download_file_with_progress(
    url: str,
    filename: str,
    dir_username: str,
    headers: dict,
    max_retries: int = 60,
    retry_delay: tuple = (2, 5)
):
    """
    单个视频下载，带重试机制（默认60次）：
      1. 启动 headless undetected-chromedriver 浏览器
      2. 全局注入自定义 headers（包含 User-Agent、Authorization、Cookie…）
      3. 注入 token 与 ecchi 标记到 localStorage
      4. 跳转到视频详情页，等待并点击“下载”按钮
      5. 从下拉菜单中提取 Source/540 真正下载链接
      6. 调用 download_file 工具，headers 中附带同一批 headers
      7. 若失败，捕获异常并休眠 retry_delay 秒后重试，最多重试 max_retries 次
    参数：
      url           视频详情页 URL
      filename      保存时的文件名
      dir_username  下载目录
      headers       请求头字典
      max_retries   最大重试次数，默认 60
      retry_delay   重试间隔范围（秒），默认 (2,5)
    返回：
      True － 下载成功
      False － 下载失败（所有重试用尽）
    """
    ua = headers.get("User-Agent", "")
    token = headers.get("Authorization", "").split(" ", 1)[-1]

    for attempt in range(1, max_retries + 1):
        print(f"[下载] 尝试第 {attempt}/{max_retries} 次")

        # 配置 headless Chrome
        opts = uc.ChromeOptions()
        opts.headless = True
        opts.add_argument(f"--user-agent={ua}")
        opts.add_argument("--lang=zh-CN")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        if PROXIES.get("http"):
            opts.add_argument(f"--proxy-server={PROXIES['http']}")

        # 启动浏览器会话
        with uc.Chrome(options=opts, driver_executable_path="./chromedriver.exe") as dl:
            try:
                # 注入全局请求头
                dl.execute_cdp_cmd("Network.enable", {})
                dl.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
                                    "headers": headers})

                # 注入登录态到 localStorage
                dl.get(IWARA_HOME)
                dl.execute_script(
                    f"window.localStorage.setItem('token','{token}');")
                dl.execute_script("window.localStorage.setItem('ecchi','1');")

                # 打开视频详情页
                dl.get(url)

                #  等待加载完成
                WebDriverWait(dl, TIMEOUT_SEC).until_not(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.loading__spinner"))
                )

                # 检测是否是私人视频
                try:
                    private_video_el = dl.find_element(
                        By.CSS_SELECTOR, ".container-fluid>div+div.text")
                    if private_video_el.get_attribute("innerText") == "HTTP 403 - 私人视频":
                        return "私人视频"
                except NoSuchElementException:
                    pass

                # 从按钮父级下拉菜单中找 Source/540 链接
                btn = WebDriverWait(dl, TIMEOUT_SEC).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, ".downloadButton"))
                )
                parent = btn.find_element(By.XPATH, "./../..")
                links = parent.find_elements(
                    By.CSS_SELECTOR, ".dropdown__content li a")
                target = None
                for a in links:
                    if a.get_attribute("innerHTML") in ("Source", "540"):
                        target = a.get_attribute("href")
                        break
                if not target:
                    print("[下载] 未找到下载链接")
                    return False

                # 调用外部下载方法
                result = download_file(
                    target, filename, dir_username,
                    headers=headers,
                    max_retries=1,               # 内部 download_file 自行重试可以设置 1
                    max_download_seconds=TIMEOUT_SEC,
                    max_filename_length=50
                )
                # 判断返回值是否表示成功
                if result in ["下载成功", "下载成功，但文件大小未知"]:
                    return True
                else:
                    raise RuntimeError(f"download_file 返回异常：{result}")

            except Exception as e:
                print(f"[下载] 第{attempt}次失败：{e}")
                if attempt == max_retries:
                    print("[下载] 达到最大重试次数，放弃下载")
                    return False
                # 随机延迟后重试
                sleep_sec = random.uniform(*retry_delay)
                print(f"[下载] 等待 {sleep_sec:.1f}s 后重试…")
                if dl:
                    dl.quit()
                time.sleep(sleep_sec)
            finally:
                if dl:
                    dl.quit()
    return False

# --------------------------------------------------


def main(driver, headers, user_name, file_prefix, download_index,
         profile_name=None, query=None):
    """
    主流程：
      1. 清空旧错误日志
      2. 获取 user_id（profile 或 search）
      3. 翻页拉视频列表，每页后随机 sleep 2～6 秒
      4. 排序、编号并打印（用单空格分隔标题与时间）
      5. 筛选下载列表
      6. 循环下载，跳过已存在文件或同名 .lnk  
      7. 汇总输出
    """
    # 1. 清空错误日志
    open(ERROR_LOG, "w", encoding="utf-8").close()

    # 2. 获取 user_id
    if not query:
        api = f"{IWARA_API}profile/{profile_name or user_name}"
        print(">> 爬取用户信息：", api)
        resp = selenium_api_get_json(driver, api, None, headers)
        if resp.get("message") == "errors.notFound":
            s = selenium_api_get_json(
                driver, IWARA_API + "search",
                {"type": "user", "query": user_name, "page": 0},
                headers
            )
            if not s.get("results"):
                print(f"[跳过] 用户 {user_name} 不存在")
                return
            api = f"{IWARA_API}profile/{s['results'][0]['username']}"
            resp = selenium_api_get_json(driver, api, None, headers)
        user_id = resp["user"]["id"]
    else:
        user_id = None

    # 3. 拉取视频列表
    video_list = []
    if not query:
        page, total = 0, 1
        while page * 32 < total:
            print(f">> 抓取第 {page+1} 页…")
            j = selenium_api_get_json(
                driver, IWARA_API + "videos",
                {"user": user_id, "sort": "date", "page": page},
                headers
            )
            total = j.get("count", 0)
            for itm in j.get("results", []):
                ct = datetime.datetime.strptime(itm["createdAt"],
                                                "%Y-%m-%dT%H:%M:%S.%fZ")
                slug = itm.get("slug", "")
                url = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                video_list.append(
                    {"url": url, "title": itm["title"], "ctime": ct})
            page += 1
            # 新功能1：每翻一页随机 sleep 2～6 秒
            time.sleep(random.uniform(2, 6))
    else:
        seen = set()
        for kw in query.split("|"):
            page, total = 0, 1
            print(f">> 搜索关键词：{kw}")
            while page * 32 < total:
                print(f">> 抓取第 {page+1} 页搜索结果…")
                j = selenium_api_get_json(
                    driver, IWARA_API + "search",
                    {"type": "video", "query": kw, "page": page},
                    headers
                )
                total = j.get("count", 0)
                for itm in j.get("results", []):
                    key = (itm["id"], itm.get("slug", ""))
                    if key in seen:
                        continue
                    seen.add(key)
                    ct = datetime.datetime.strptime(itm["createdAt"],
                                                    "%Y-%m-%dT%H:%M:%S.%fZ")
                    slug = itm.get("slug", "")
                    url = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                    video_list.append(
                        {"url": url, "title": itm["title"], "ctime": ct})
                page += 1
                # 新功能1：每翻一页随机 sleep 2～6 秒
                time.sleep(random.uniform(2, 6))

    # 4. 排序、编号并打印（用单空格分隔）
    video_list.sort(key=lambda x: x["ctime"])
    for idx, v in enumerate(video_list, 1):
        v["idx"] = idx
        print(f"{idx:3d} {v['title']} {v['ctime']}")

    # 5. 筛选下载列表
    if isinstance(download_index, str) and download_index.endswith(":"):
        start = int(download_index[:-1]) - 1
        download_list = video_list[start:]
    else:
        download_list = video_list[:]

    # 6. 循环下载
    success, errors = [], []
    base_dir = "downloads"
    for v in download_list:
        idx = v["idx"]
        prefix = file_prefix or user_name or "视频"
        # 新功能3：搜索分支目录命名
        if query:
            user_dir = f"[搜索]{file_prefix}"
        else:
            user_dir = prefix
        fn = f"{prefix}.{idx:03d}.{v['title']}.mp4"
        # 过滤非法字符
        fn = fn.translate(str.maketrans({
            "\\": "——", "/": " ", "*": " ", "?": " ",
            ":": "：", "\"": "”", "<": "《", ">": "》", "|": "！"
        }))
        save_dir = os.path.join(base_dir, user_dir)
        os.makedirs(save_dir, exist_ok=True)

        dest = os.path.join(save_dir, fn)
        # 新功能2：文件或 .lnk 存在则跳过
        if os.path.exists(dest) or os.path.exists(dest + ".lnk"):
            print(f"{idx:3d} 已存在，跳过")
            continue

        print(f"{idx:3d} 开始下载 → {dest}")
        ok = download_file_with_progress(v["url"], fn, save_dir, headers)
        if ok != "私人视频" and ok:
            print(f"{idx:3d} 下载成功")
            success.append(fn)
        elif ok == "私人视频":
            print(f"{idx:3d} 私人视频")
            with open(ERROR_LOG, "a", encoding="utf-8") as ef:
                ef.write(f"{fn} 私人视频，URL: {v['url']}\n")
            errors.append(fn)
        else:
            print(f"{idx:3d} 下载失败")
            with open(ERROR_LOG, "a", encoding="utf-8") as ef:
                ef.write(f"{fn} 下载失败，URL: {v['url']}\n")
            errors.append(fn)

    # 7. 汇总输出
    if success:
        print("\n下载成功列表:")
        for x in success:
            print("   ", x)
    if errors:
        print("\n下载失败列表:")
        for x in errors:
            print("   ", x)


# -------------------- 脚本入口 --------------------
if __name__ == "__main__":
    try:
        # 1. 获取 token + cookie
        ua, token, cookie_header = get_token_and_cookie()
        headers = {
            "User-Agent":    ua,
            "Authorization": f"Bearer {token}",
            "Cookie":        cookie_header
        }

        # 2. 初始化 undetected-chromedriver 会话并全局注入 headers
        driver = init_uc_session(ua, headers)

        # 3. 批量执行任务
        for u in USER_INFO:
            print("\n" + "=" * 60)
            main(
                driver, headers,
                u.get("user_name", ""),
                u.get("file_prefix", ""),
                u.get("download_index", ""),
                profile_name=u.get("profile_name"),
                query=u.get("query")
            )

        # 4. 退出浏览器
        driver.quit()
    except Exception as e:
        print(f"报错信息：{e}")
        if driver:
            driver.quit()
    finally:
        if driver:
            driver.quit()
