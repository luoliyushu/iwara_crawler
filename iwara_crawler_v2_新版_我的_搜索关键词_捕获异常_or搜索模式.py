
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.core.http import HttpClient

import datetime
import json
import math
import os
import random
import re
import requests
import shutil
import string
import sys
import time

from mymodule import download_file
from requests.exceptions import SSLError

# {
#   "user_name": The name of iwara user
#   "file_prefix": Add a prefix for all video files if needed
#   "download_index": Download the video by index in this list only. Leave it blank for all
#   "profile_name": Optional. Actual name in profile page link. eg: https://www.iwara.tv/profile/user787392
# }
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
    {"user_name": "sola", "profile_name": "user2501342", "download_index": "", "file_prefix": ""},
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
    {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "ハンド", "query": "ハンド|gentleman hand"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "標識", "query": "標識|ero sign|sign strip|hentai sign"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "時間停止", "query": "時間 停止|time stop|时间 停止|时停|時停"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "紳士枠", "query": "枠|透視|框|透视"},
    # {"user_name": "", "profile_name": "", "download_index": "", "file_prefix": "DATEN_ROUTE", "query": "DATEN"},
]

DATE_LIMIT = 0   # Prevent downloading aged videos, 0 for unlimited / 假设为14，则表示只下载近14天的视频

PROXIES = {
    # "http": "http://127.0.0.1:8080",
    # "https": "http://127.0.0.1:8080",
}

IWARA_HOME = "https://www.iwara.tv/"
IWARA_API = "https://api.iwara.tv/"

# Chrome Driver https://googlechromelabs.github.io/chrome-for-testing/


class HttpClientWithProxy(HttpClient):
    def get(self, url, params=None, **_kwargs) -> requests.Response:
        return requests.get(url, params, proxies=PROXIES, verify=False)


def get_token():
    options = webdriver.ChromeOptions()
    if "http" in PROXIES:
        options.add_argument(f"--proxy-server={PROXIES['http'].replace('http://', '')}")
    if not os.path.isfile("token.json"):
        ua = UserAgent()
        user_agent = ua.random
        print(user_agent)
        options.add_argument(f"--user-agent={user_agent}")
        with webdriver.Chrome(
            # service=ChromeService(ChromeDriverManager(
            #     version="114.0.5735.90",
            #     download_manager=WDMDownloadManager(HttpClientWithProxy())
            # ).install()),
            service=ChromeService("./chromedriver.exe"),
            options=options,
        ) as driver:
            driver.get(f"{IWARA_HOME}login")
            while True:
                token = driver.execute_script("""
                    return window.localStorage.getItem("token");;
                """)
                time.sleep(random.randint(1, 3))
                if token is not None:
                    break

            with open("token.json", "w") as f:
                f.write(json.dumps({
                    "user_agent": user_agent,
                    "token": token,
                }, indent=4))
    else:
        with open("token.json", "r") as f:
            data = json.load(f)
            user_agent = data["user_agent"]
            token = data["token"]

    return user_agent, token


def create_dir():
    root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tmp_dir")
    while True:
        dir_name = "".join([random.choice(string.ascii_lowercase) for i in range(8)])
        if not os.path.isdir(os.path.join(root_dir, dir_name)):
            break
    # os.mkdir(dir_name)
    return os.path.join(root_dir, dir_name)


success_list = list()
error_list = list()


def download_file_with_progress(url, filename, dir_username):
    local_dir = create_dir()

    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en-US")
    if "http" in PROXIES:
        options.add_argument(f"--proxy-server={PROXIES['http'].replace('http://', '')}")
    options.add_argument("--devtools")
    options.add_experimental_option("prefs", {
        "download.default_directory": local_dir,
    })

    user_agent, token = get_token()

    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--headless=new")

    with webdriver.Chrome(
        # service=ChromeService(ChromeDriverManager(
        #     version="114.0.5735.90",
        #     download_manager=WDMDownloadManager(HttpClientWithProxy()),
        # ).install()),
        service=ChromeService("./chromedriver.exe"),
        options=options,
    ) as driver:
        sys.stdout.write("\rlogin...")
        driver.get(f"{IWARA_HOME}login")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".inputField"))
            )
            driver.execute_script(f"window.localStorage.setItem('token', '{token}');")  # Login
            driver.execute_script(f"window.localStorage.setItem('ecchi', '1');")  # I am over 18
            time.sleep(random.randint(1, 3))
            sys.stdout.write("\rfetch download url...")
            driver.get(url)
            try:
                r = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".header__content"))
                )
                r = r.find_element(By.CSS_SELECTOR, ".header__link")
                if "Register" in r.get_attribute("innerHTML"):
                    sys.stdout.write(" login failed. Please delete token.json and retry.")
                    driver.quit()
                    print("")
                    return False
            except TimeoutException:
                sys.stdout.write(" timeout(1).")
                driver.quit()
                print("")
                return False
            try:
                download_button = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".downloadButton"))
                )
                # download_button = driver.find_element(By.CSS_SELECTOR, ".downloadButton")
                download_parent = download_button.find_element(By.XPATH, "./../..")
                download_content = download_parent.find_element(By.CSS_SELECTOR, ".dropdown__content")
                download_li = download_content.find_elements(By.TAG_NAME, "li")
                target_url = None
                for li in download_li:
                    a = li.find_elements(By.TAG_NAME, "a")
                    if a[0].get_attribute("innerHTML") == "Source":
                        target_url = a[0].get_attribute("href")
                        break
                    elif a[0].get_attribute("innerHTML") == "540": # 我修改的代码
                        target_url = a[0].get_attribute("href")
                        break
                if target_url is not None:
                    sys.stdout.write("\rstart download...")
                    # 我修改的代码
                    if '下载成功' in download_file(target_url, filename, dir_username, headers=headers, max_retries=60, max_download_seconds=20, max_filename_length=50):
                        return True
                    else:
                        return False
                                      
                    # region 原版下载代码
                    # driver.get(target_url)
                    # driver.get("chrome://downloads")

                    # while True:
                    #     progress_string = driver.execute_script("""
                    #         return function(){
                    #             let res = null;
                    #             let downloads_manager = document.querySelector("downloads-manager");
                    #             if (downloads_manager != null) {
                    #                 let frb0 = downloads_manager.shadowRoot.querySelector("#frb0");
                    #                 if (frb0 != null) {
                    #                     let description = frb0.shadowRoot.querySelector(".description");
                    #                     if (description != null) {
                    #                         res = description.innerHTML;
                    #                     }
                    #                 }
                    #             }
                    #             return res;
                    #         }();
                    #     """)
                    #     if progress_string is not None:
                    #         progress_string = progress_string.replace("\n", "").strip(" ")
                    #         progress_string = re.sub(r"<!--.+-->", "", progress_string)
                    #         sys.stdout.write(f"\r{progress_string}")
                    #         if progress_string == "":
                    #             # resume_button = driver.execute_script("""
                    #             #     return function(){
                    #             #         let res = null;
                    #             #         let downloads_manager = document.querySelector("downloads-manager");
                    #             #         if (downloads_manager != null) {
                    #             #             let frb0 = downloads_manager.shadowRoot.querySelector("#frb0");
                    #             #             if (frb0 != null) {
                    #             #                 let resume_button = frb0.shadowRoot.querySelector("#pauseOrResume");
                    #             #                 if (resume_button != null) {
                    #             #                     let button_panel = resume_button.parentElement;
                    #             #                     if (button_panel.style.display !== "none") {
                    #             #                         resume_button.click();
                    #             #                         res = "true";
                    #             #                     }
                    #             #                 }
                    #             #             }
                    #             #         }
                    #             #         return res;
                    #             #     }();
                    #             # """)
                    #             # if resume_button is not None:
                    #             #     continue
                    #             # else:
                    #             sys.stdout.write("\rprocessing...")
                    #             actual_file_list = os.listdir(local_dir)
                    #             if len(actual_file_list) == 0:
                    #                 sys.stdout.write("\rFailed.")
                    #                 return False
                    #             actual_file_name = os.listdir(local_dir)[0]
                    #             shutil.move(os.path.join(local_dir, actual_file_name), filename)
                    #             shutil.rmtree(local_dir)
                    #             sys.stdout.write("\rCompleted.")
                    #             break
                    #         des_list = progress_string.replace(",", "").split(" ")
                    #         progress = 0
                    #         if des_list[4] == des_list[7]:
                    #             progress = min(int(math.floor(50 * (float(des_list[3]) / float(des_list[6])))), 50)
                    #         sys.stdout.write("\r[{}{}] {}/{} {} ETC: {}".format(
                    #             "=" * progress,
                    #             " " * (50 - progress),
                    #             des_list[3] + des_list[4],
                    #             des_list[6] + des_list[7].rstrip(","),
                    #             des_list[0] + des_list[1],
                    #             (des_list[8] if len(des_list) > 8 else "") + (des_list[9] if len(des_list) > 9 else "")
                    #         ))
                    # endregion
            except TimeoutException:
                sys.stdout.write(" timeout(2).")
                driver.quit()
                print("")
                return False

        except TimeoutException:
            sys.stdout.write(" timeout(3).")
            driver.quit()
            print("")
            return False

        driver.quit()
        print("")
        return True


def main(user_name, file_prefix, download_index, profile_name=None, query=None): # 我修改的代码
    if not query: # 我修改的代码，用户搜索，原版
        if profile_name is not None:
            user_api = f"{IWARA_API}profile/{requests.utils.quote(profile_name)}"
            print(f"{user_name} {IWARA_HOME}profile/{profile_name}")
        else:
            user_api = f"{IWARA_API}profile/{requests.utils.quote(user_name)}"
            print(f"{user_name} {IWARA_HOME}profile/{user_name}")
        user_api_req = requests.get(user_api, proxies=PROXIES)
        while user_api_req.status_code not in [200]:
            print("profile_api", user_api_req.status_code)
            time.sleep(random.randint(1, 3))
            user_api_req = requests.get(user_api, proxies=PROXIES)
        if "message" in user_api_req.json() and user_api_req.json()["message"] == "errors.notFound":
            search_api = f"{IWARA_API}search"
            search_api_req = requests.get(search_api, params={
                "type": "user",
                "query": user_name,
                "page": 0,
            }, proxies=PROXIES)
            if len(search_api_req.json()["results"]) == 0:
                print("user not found")
                return
            id_like_username = search_api_req.json()["results"][0]["username"]
            print(f"{user_name} {IWARA_HOME}profile/{id_like_username}")
            user_api = f"{IWARA_API}profile/{requests.utils.quote(id_like_username)}"
            user_api_req = requests.get(user_api, proxies=PROXIES)
        user_id = user_api_req.json()["user"]["id"]

        video_list = list()
        page = 0
        count = 0
        limit = 32
        while page * limit <= count:
            try:
                print(f"Reading Page No.{page + 1} ...")
                video_api = f"{IWARA_API}videos"
                video_api_req = requests.get(video_api, params={
                    "user": user_id,
                    "sort": "date",
                    "page": page,
                }, headers=headers, proxies=PROXIES) # 我修改的代码
                if video_api_req.status_code not in [200]:
                    print("video_api", video_api_req.status_code)
                    time.sleep(random.randint(1, 3))
                    continue
                count = video_api_req.json()["count"]
                for item in video_api_req.json()["results"]:
                    if item["slug"] is not None:
                        video_url = f"{IWARA_HOME}video/{item['id']}/{item['slug']}"
                    else:
                        video_url = f"{IWARA_HOME}video/{item['id']}"
                    video_list.append({
                        "url": video_url,
                        "title": item["title"],
                        "create_time": datetime.datetime.strptime(item["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    })
                page += 1
                # print page, limit, page * limit, count
            except SSLError as ssl_err:
                print(f"捕获到SSLError: {ssl_err}")
                time.sleep(random.randint(1, 3))
                # 这里可以添加额外的错误处理逻辑，比如重试请求、记录日志等
            except requests.exceptions.RequestException as req_err:
                # 捕获其他requests库可能抛出的异常，如连接错误、超时等
                print(f"请求发生错误: {req_err}")
                time.sleep(random.randint(1, 3))
        video_list.reverse()
        print("Video List:")
        for i, video in enumerate(video_list):
            print(f"{i + 1} {video['title']} {video['create_time']}")
            video_list[i]["index"] = i + 1
        print("-" * 80)
    else: # 我修改的代码，关键词搜索，新增，支持or搜索模式
        video_list = list()
        for query_item in query.split("|"):
            print(f"{query_item} {IWARA_HOME}search/{profile_name}")
            page = 0
            count = 0
            limit = 32
            while page * limit <= count:
                try:
                    print(f"Reading Page No.{page + 1} ...")
                    video_api = f"{IWARA_API}search"
                    video_api_req = requests.get(video_api, params={
                        "type": "video",
                        "page": page,
                        "query": query_item,
                    }, headers=headers, proxies=PROXIES) # 我修改的代码
                    if video_api_req.status_code not in [200]:
                        print("video_api", video_api_req.status_code)
                        time.sleep(random.randint(1, 3))
                        continue
                    count = video_api_req.json()["count"]
                    for item in video_api_req.json()["results"]:
                        if item["slug"] is not None:
                            video_url = f"{IWARA_HOME}video/{item['id']}/{item['slug']}"
                        else:
                            video_url = f"{IWARA_HOME}video/{item['id']}"
                        video_info = {
                            "url": video_url,
                            "title": item["title"],
                            "create_time": datetime.datetime.strptime(item["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                        }
                        if video_info not in video_list:
                            video_list.append(video_info)
                    page += 1
                    # print page, limit, page * limit, count
                except SSLError as ssl_err:
                    print(f"捕获到SSLError: {ssl_err}")
                    time.sleep(random.randint(1, 3))
                    # 这里可以添加额外的错误处理逻辑，比如重试请求、记录日志等
                except requests.exceptions.RequestException as req_err:
                    # 捕获其他requests库可能抛出的异常，如连接错误、超时等
                    print(f"请求发生错误: {req_err}")
                    time.sleep(random.randint(1, 3))
        video_list.reverse()
        print("Video List:")
        for i, video in enumerate(video_list):
            print(f"{i + 1} {video['title']} {video['create_time']}")
            video_list[i]["index"] = i + 1
        print("-" * 80)
        file_prefix = file_prefix.replace("|", "｜")
        query = query.replace("|", "｜")

    # region 我修改的代码
    download_list = list()
    if isinstance(download_index, str):
        if download_index.endswith(':'):
            # 处理第三种情况 "264:"
            start_index = int(download_index[:-1]) - 1
            download_list = video_list[start_index:]
        elif not download_index:
            # 处理第一种情况（空字符串）""
            download_list = video_list[:]
            download_list.reverse()
    elif isinstance(download_index, list):
        # 处理第二种情况（复杂列表）list(range(1,10)) + list(range(11,14)) + list(range(15,17)) + list(range(18,33))
        if len(download_index) > 0:
            for index in download_index:
                if index == 0:
                    pass
                elif index > 0:
                    if index - 1 < len(video_list):
                        download_list.append(video_list[index - 1])
                else:
                    if index + len(video_list) > 0:
                        if (DATE_LIMIT > 0 and video_list[index]["create_time"] <
                                datetime.datetime.now() - datetime.timedelta(DATE_LIMIT)):
                            continue
                        download_list.append(video_list[index])
        else:
            download_list = video_list[:]
            download_list.reverse()
    else:
        # 处理其他可能的情况
        print("Unexpected download_index type")
    # endregion

    for i, video in enumerate(download_list):
        print(f"{video['index']} {video['title']} {video['url']} {video['create_time']}")
        _file_prefix = "{}.{:03d}.".format(
            file_prefix if file_prefix != "" else user_name or query, # 我修改的代码
            video["index"],
        )
        _file_name = u"{}.mp4".format(
            video["title"]
            .replace("\\", "——")
            .replace("/", " ")
            .replace(":", "：")
            .replace("*", " ")
            .replace("?", " ")
            .replace("\"", "”")
            .replace("<", "《")
            .replace(">", "》")
            .replace("|", "!")
            ,
        )
        
        # region 修改的代码
        dir_username = file_prefix or user_name or query
        if query and "[搜索]" not in dir_username:
            dir_username = "[搜索]" + dir_username
        # endregion
        print(f"Downloading to {_file_prefix + _file_name}")
        if os.path.exists(os.path.join("downloads", dir_username, _file_prefix + _file_name)) or os.path.exists(os.path.join("downloads", dir_username, _file_prefix + _file_name + ".lnk")):  # 我修改的代码
            print("Completed.")
        else:
            if download_file_with_progress(video["url"], _file_prefix + _file_name, os.path.join("downloads", dir_username)): # 我修改的代码
                success_list.append(_file_prefix + _file_name)
            else:
                # region 我修改的代码
                with open("error_list.txt", "a", encoding="utf-8") as f:
                    my_url = video["url"]
                    f.write(f"文件名：{_file_prefix + _file_name}\n链接：{my_url}\n\n")
                # endregion
                error_list.append(_file_prefix + _file_name)


if __name__ == "__main__":
    # region 我修改的代码，在运行之前重置error_list.txt
    with open("error_list.txt", "w", encoding="utf-8") as f:
        f.truncate(0)  
    user_agent, token = get_token()
    headers = {
        'User-Agent': user_agent,
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % token
    }
    # endregion

    # USER_INFO.reverse()
    for user in USER_INFO:
        main(
            user["user_name"],
            user["file_prefix"],
            user["download_index"],
            user["profile_name"] if "profile_name" in user else None,
            user["query"] if "query" in user else None,
        )
        print("")

    if len(success_list) > 0:
        print("Success List:")
        for i in success_list:
            print(i)
    if len(error_list) > 0:
        print("Error List:")
        for i in error_list:
            print(i)
