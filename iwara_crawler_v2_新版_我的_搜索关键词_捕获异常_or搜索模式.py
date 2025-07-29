#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整脚本：在原有 undetected-chromedriver + Selenium 框架上，
增加“Cookie”头注入。流程如下：
 1. headful 浏览器扫码登录，获取 localStorage token + 浏览器 cookies
 2. 将 token 与 cookie-string 一并保存到 token.json
 3. 后续所有 API 请求与下载请求的 headers 中，加入这条 cookie
 4. 其他功能（拉视频列表、筛选、下载）保持不变
详细中文注释，拷贝即用
"""

import os
import sys
import json
import time
import random
import shutil
import datetime
from urllib.parse import urlencode

from fake_useragent import UserAgent
import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 自定义下载工具，需要你自己实现
from mymodule import download_file

# --------------------------------------------------
# 用户配置区：username/file_prefix/download_index/profile_name/query
USER_INFO = [
    {
        "user_name": "",               # Iwara 用户名
        "profile_name": "",            # 优先按 profile_name 查找，不填则用 user_name
        "download_index": "",          # "3:" 表示从第3个到末尾下载，空串=全部
        "file_prefix": "ハンド",         # 文件名前缀
        "query": "ハンド|gentleman hand",# 若 query 不空，则走搜索接口，用 | 分隔
    },
    # 可添加更多任务...
]

# --------------------------------------------------
# 全局常量
IWARA_HOME    = "https://www.iwara.tv/"
IWARA_API     = "https://api.iwara.tv/"
TOKEN_FILE    = "token.json"  # 缓存 user_agent、token、cookie
ERROR_LOG     = os.path.join(os.path.dirname(__file__), "error_list.txt")
TIMEOUT_SEC   = 60
PROXIES       = {}            # 如需代理请填 {"http":"...","https":"..."}

# --------------------------------------------------
def get_token_and_cookie():
    """
    获取并缓存 Iwara 登录 token + 浏览器 cookies：
      1. 本地无 token.json 时，启动有界面 Chrome：
         - 注入 UA，打开登录页扫码
         - 扫码成功后，从 localStorage 读取 token
         - 从 driver.get_cookies() 读取所有 cookie，将其拼成 "n1=v1; n2=v2" 字符串
         - 保存到 token.json：{"user_agent":..., "token":..., "cookie": "..."}
      2. 本地已有 token.json，直接加载返回
    返回：(user_agent, token, cookie_header)
    """
    if not os.path.exists(TOKEN_FILE):
        # 随机 UA
        ua = UserAgent().random
        opts = uc.ChromeOptions()
        opts.headless = False
        opts.add_argument(f"--user-agent={ua}")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        # 如果需要代理，在此添加
        if PROXIES.get("http"):
            opts.add_argument(f"--proxy-server={PROXIES['http']}")

        # 启动带界面浏览器让你扫码
        driver = uc.Chrome(options=opts, driver_executable_path="./chromedriver.exe")
        driver.get(IWARA_HOME + "login")
        print("→ 请扫码登录 Iwara …")

        # 等待 localStorage.token 写入
        token = None
        while not token:
            token = driver.execute_script("return window.localStorage.getItem('token');")
            time.sleep(1 + random.random())

        # 读取浏览器 cookies 列表
        raw_cookies = driver.get_cookies()
        driver.quit()

        # 拼成单行 Cookie 头字符串
        cookie_pairs = [f"{c['name']}={c['value']}" for c in raw_cookies]
        cookie_header = "; ".join(cookie_pairs)

        # 保存到本地
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "user_agent": ua,
                "token": token,
                "cookie": cookie_header
            }, f, indent=2)

    # 直接加载已有的 token.json
    cfg = json.load(open(TOKEN_FILE, encoding="utf-8"))
    return cfg["user_agent"], cfg["token"], cfg["cookie"]

# --------------------------------------------------
def init_uc_session(user_agent: str):
    """
    初始化 undetected-chromedriver 会话，用于 API 调用（selenium_api_get_json）：
      - headless=False 仅为能操作 localStorage，同源注入 token
      - 设置浏览器 UA
      - 隐藏自动化特征
      - 注入 token 到 localStorage，设置 ecchi=1
    返回：已就绪 driver
    """
    opts = uc.ChromeOptions()
    opts.headless = True
    opts.add_argument(f"--user-agent={user_agent}")
    opts.add_argument("--lang=zh-CN")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    if PROXIES.get("http"):
        opts.add_argument(f"--proxy-server={PROXIES['http']}")

    driver = uc.Chrome(options=opts, driver_executable_path="./chromedriver.exe")

    # 打开首页保持同源，才能注入 localStorage
    driver.get(IWARA_HOME)
    # 注入 token & ecchi 标记
    ua, token, cookie_header = get_token_and_cookie()
    driver.execute_script(f"window.localStorage.setItem('token','{token}');")
    driver.execute_script("window.localStorage.setItem('ecchi','1');")

    return driver

# --------------------------------------------------
def selenium_api_get_json(
    driver,
    url: str,
    params: dict = None,
    headers: dict = None,
    retries: int = 5,
    retry_delay: tuple = (2, 4)
):
    """
    通过 undetected-chromedriver 访问 API 并返回 JSON：
      - 拼接查询参数
      - 注入请求头（包括新加的 Cookie）
      - driver.get(full_url)，等待 <body> text
      - 失败则重试
    """
    # 读取存储的 cookie 字符串
    _, _, cookie_header = get_token_and_cookie()

    for attempt in range(1, retries + 1):
        try:
            # 确保同源在主站
            if not driver.current_url.startswith(IWARA_HOME):
                driver.get(IWARA_HOME)

            # 拼 full_url
            full_url = url + ("?" + urlencode(params) if params else "")

            # 启用 CDP 设头
            driver.execute_cdp_cmd("Network.enable", {})
            # 加入用户自定义 headers
            all_headers = headers.copy() if headers else {}
            all_headers["Cookie"] = cookie_header
            driver.execute_cdp_cmd("Network.setExtraHTTPHeaders",
                                   {"headers": all_headers})

            # 发起请求并等待 JSON 渲染
            driver.get(full_url)
            WebDriverWait(driver, TIMEOUT_SEC).until(
                lambda d: d.find_element(By.TAG_NAME, "body")
                              .text.strip().startswith("{")
            )
            raw = driver.find_element(By.TAG_NAME, "body").text
            return json.loads(raw)

        except Exception as e:
            print(f"[Fetch JSON] 重试 {attempt}/{retries}，错误: {e}")
            if attempt == retries:
                raise
            time.sleep(random.uniform(*retry_delay))

# --------------------------------------------------
def download_file_with_progress(url, filename, dir_username):
    """
    单个视频下载：
      1. 启动 headless uc.Chrome
      2. 注入 token 到 localStorage
      3. 跳转详情页，点击下载按钮，解析 Source/540 链接
      4. 调用 download_file，headers 中追加 Cookie
    返回：True/False
    """
    # 从本地读 UA/token/cookie
    ua, token, cookie_header = get_token_and_cookie()

    opts = uc.ChromeOptions()
    opts.headless = True
    opts.add_argument(f"--user-agent={ua}")
    opts.add_argument("--lang=zh-CN")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    if PROXIES.get("http"):
        opts.add_argument(f"--proxy-server={PROXIES['http']}")

    with uc.Chrome(options=opts, driver_executable_path="./chromedriver.exe") as dl:
        # 保持同源注入 localStorage
        dl.get(IWARA_HOME)
        dl.execute_script(f"window.localStorage.setItem('token','{token}');")
        dl.execute_script("window.localStorage.setItem('ecchi','1');")

        # 打开视频详情
        dl.get(url)
        try:
            btn = WebDriverWait(dl, TIMEOUT_SEC).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".downloadButton"))
            )
        except TimeoutException:
            print("[下载] 按钮超时")
            return False

        # 下拉菜单查找 Source/540
        parent = btn.find_element(By.XPATH, "./ancestor::div[contains(@class,'dropdown')]")
        links  = parent.find_elements(By.TAG_NAME, "a")
        target = None
        for a in links:
            txt = a.text.strip()
            if txt in ("Source", "540"):
                target = a.get_attribute("href")
                break
        if not target:
            print("[下载] 未找到下载链接")
            return False

        # 调用外部下载，headers里加 Cookie
        ok = download_file(
            target, filename, dir_username,
            headers={
                "User-Agent": ua,
                "Authorization": f"Bearer {token}",
                "Cookie": cookie_header
            },
            max_retries=60, max_download_seconds=TIMEOUT_SEC
        )
        return ok in ["下载成功", "下载成功，但文件大小未知"]

# --------------------------------------------------
def main(driver, headers, user_name, file_prefix, download_index,
         profile_name=None, query=None):
    """
    主流程：
      1. 清空旧错误日志
      2. 获取 user_id（profile 或 search）
      3. 翻页拉视频列表
      4. 排序编号并打印
      5. 根据 download_index 筛选
      6. 循环下载并记录 成功/失败
      7. 汇总输出
    """
    # 1. 清空错误日志
    open(ERROR_LOG, "w", encoding="utf-8").close()

    # 2. 获取 user_id
    if not query:
        api = f"{IWARA_API}profile/{profile_name or user_name}"
        print(">> 爬取用户信息：", api)
        resp = selenium_api_get_json(driver, api, params=None, headers=headers)
        if resp.get("message") == "errors.notFound":
            # profile 查询不到，走 search
            s = selenium_api_get_json(
                driver, IWARA_API + "search",
                params={"type":"user","query":user_name,"page":0},
                headers=headers
            )
            if not s.get("results"):
                print(f"[跳过] 用户 {user_name} 不存在")
                return
            api = f"{IWARA_API}profile/{s['results'][0]['username']}"
            resp = selenium_api_get_json(driver, api, params=None, headers=headers)
        user_id = resp["user"]["id"]
    else:
        user_id = None

    # 3. 拉取视频列表
    video_list = []
    if not query:
        page, count = 0, 1
        while page * 32 <= count:
            print(f">> 抓取第 {page+1} 页…")
            j = selenium_api_get_json(
                driver, IWARA_API + "videos",
                params={"user":user_id,"sort":"date","page":page},
                headers=headers
            )
            count = j.get("count", 0)
            for itm in j.get("results", []):
                ct = datetime.datetime.strptime(
                    itm["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                slug = itm.get("slug","")
                url  = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                video_list.append({"url":url,"title":itm["title"],"ctime":ct})
            page += 1
            time.sleep(random.uniform(5, 10))
    else:
        seen = set()
        for kw in query.split("|"):
            print(f">> 搜索关键词：{kw}")
            page, count = 0, 1
            while page * 32 <= count:
                print(f">> 抓取第 {page+1} 页搜索结果…")
                j = selenium_api_get_json(
                    driver, IWARA_API + "search",
                    params={"type":"video","query":kw,"page":page},
                    headers=headers
                )
                count = j.get("count",0)
                for itm in j.get("results",[]):
                    key = (itm["id"], itm.get("slug",""))
                    if key in seen:
                        continue
                    seen.add(key)
                    ct   = datetime.datetime.strptime(
                        itm["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    )
                    slug = itm.get("slug","")
                    url  = f"{IWARA_HOME}video/{itm['id']}/{slug}"
                    video_list.append({"url":url,"title":itm["title"],"ctime":ct})
                page += 1
            time.sleep(random.uniform(5, 10))

    # 排序 & 编号
    video_list.sort(key=lambda x: x["ctime"])
    for idx, v in enumerate(video_list, 1):
        v["idx"] = idx
        print(f"{idx:3d} {v['title']}  {v['ctime']}")

    # 4. 筛选列表
    if isinstance(download_index, str) and download_index.endswith(":"):
        start = int(download_index[:-1]) - 1
        download_list = video_list[start:]
    else:
        download_list = video_list[:]

    # 5. 下载循环
    success, errors = [], []
    base_dir = "downloads"
    for v in download_list:
        idx = v["idx"]
        prefix = file_prefix or user_name or query or "视频"
        fn = f"{prefix}.{idx:03d}.{v['title']}.mp4"
        # 过滤 Windows 文件名非法字符
        fn = fn.translate(str.maketrans({
            "\\":"——","/":" ","*":" ","?":" ",
            ":":"：","\"":"”","<":"《",">":"》","|":"！"
        }))
        user_dir = prefix or user_name or query or "视频"
        save_dir = os.path.join(base_dir, user_dir)
        os.makedirs(save_dir, exist_ok=True)

        dest = os.path.join(save_dir, fn)
        if os.path.exists(dest):
            print(f"{idx:3d} 已存在，跳过")
            continue

        print(f"{idx:3d} 开始下载 → {dest}")
        ok = download_file_with_progress(v["url"], fn, save_dir)
        if ok:
            print(f"{idx:3d} 下载成功")
            success.append(fn)
        else:
            print(f"{idx:3d} 下载失败")
            with open(ERROR_LOG, "a", encoding="utf-8") as ef:
                ef.write(f"{fn} 下载失败，URL: {v['url']}\n")
            errors.append(fn)

    # 6. 输出汇总
    if success:
        print("\n下载成功列表:")
        for x in success:
            print("   ", x)
    if errors:
        print("\n下载失败列表:")
        for x in errors:
            print("   ", x)

# --------------------------------------------------
if __name__ == "__main__":
    # 1. 获取 token + cookie
    ua, token, cookie_header = get_token_and_cookie()

    # 2. 初始化 undetected-chromedriver 会话
    driver = init_uc_session(ua)

    # 3. 构造 API 请求头，加入 Cookie
    headers = {
        "User-Agent": ua,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Cookie": cookie_header
    }

    # 4. 批量执行
    for u in USER_INFO:
        print("\n" + "=" * 60)
        main(
            driver, headers,
            u.get("user_name",""),
            u.get("file_prefix",""),
            u.get("download_index",""),
            profile_name=u.get("profile_name"),
            query=u.get("query")
        )

    # 5. 退出
    driver.quit()
