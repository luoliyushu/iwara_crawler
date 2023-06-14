
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

import json
import math
import os
import random
import requests
import shutil
import string
import sys
import time


USER_INFO = [
    # {
    #   "user_name": The name of iwara user,
    #   "file_prefix": Add a prefix for all video files if needed,
    #   "download_index": Download the video by index in this list only. Leave it blank for all
    # }
    {"user_name": "Forget Skyrim.", "profile_name": "forgetskyrim", "file_prefix": "Forget Skyrim", "download_index": [-1]},
    {"user_name": "嫖阿姨", "profile_name": "user798290", "file_prefix": "P嫖阿姨", "download_index": [-1]},
    {"user_name": "491033063", "file_prefix": "S神经觉醒", "download_index": [-1]},
    {"user_name": "和颐雪", "profile_name": "user787392", "file_prefix": "H和颐雪", "download_index": [-1]},
    # {"user_name": "miraclegenesismmd", "file_prefix": "MiracleGenesisMMD", "download_index": [-1]},
    {"user_name": "嫚迷GirlFans", "profile_name": "girlfans", "file_prefix": "M嫚迷GirlFans", "download_index": [-1]},
    {"user_name": "JUSWE", "file_prefix": "AlZ", "download_index": [-1]},
    # {"user_name": "三仁月饼", "file_prefix": "S三仁月饼", "download_index": [-1]},
    # {"user_name": "LTDEND", "file_prefix": "", "download_index": [-1]},
    # {"user_name": "Mister Pink", "file_prefix": "", "download_index": [-1]},
    # {"user_name": "qimiaotianshi", "file_prefix": "", "download_index": [-1]},
    # {"user_name": "jvmpdark", "file_prefix": "", "download_index": [-1]},
    # {"user_name": "EcchiFuta", "file_prefix": "", "download_index": [-1]},
    {"user_name": "水水..", "profile_name": "user937858", "file_prefix": "S水水..", "download_index": [-1]},
    # {"user_name": "慕光", "file_prefix": "M慕光", "download_index": [-1]},
    {"user_name": "煜喵", "profile_name": "user1107866", "file_prefix": "Y煜喵", "download_index": [-1]},
    # {"user_name": "113458", "file_prefix": "Y113458", "download_index": [-1]},
    {"user_name": "腿 玩 年", "profile_name": "user221116", "file_prefix": "T腿玩年", "download_index": [-1]},
    # {"user_name": "sugokunemui", "file_prefix": "sugokunemui", "download_index": [-1]},
    # {"user_name": "mister-pink", "file_prefix": "mister-pink", "download_index": [-1]},
    {"user_name": "二两牛肉面jd", "profile_name": "user178752", "file_prefix": "E二两牛肉面", "download_index": [-1]},
    # {"user_name": "hisen", "file_prefix": "Hisen", "download_index": [-1]},
    {"user_name": "MMD_je", "profile_name": "mmdje", "file_prefix": "mmdje", "download_index": [-1]},
    {"user_name": "emisa", "file_prefix": "", "download_index": [-1]},
    {"user_name": "穴儿湿袭之", "profile_name": "user1235858", "file_prefix": "S穴儿湿袭之", "download_index": [-1]},
    {"user_name": "SEALING", "file_prefix": "", "download_index": [-1]},
    {"user_name": "icegreentea", "file_prefix": "", "download_index": [-1]},
    {"user_name": "NekoSugar", "file_prefix": "", "download_index": [-1]},
]

PROXIES = {
    "https": "http://127.0.0.1:18080",
}

IWARA_HOME = "https://www.iwara.tv/"
IWARA_API = "https://api.iwara.tv/"


def get_token():
    options = webdriver.ChromeOptions()
    options.add_argument(f"--proxy-server={PROXIES['https'].replace('http://', '')}")
    if not os.path.isfile("token.json"):
        ua = UserAgent()
        user_agent = ua.random
        print(user_agent)
        options.add_argument(f"--user-agent={user_agent}")
        with webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
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


def download_file_with_progress(url, local_dir):
    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en-US")
    # options.add_argument(f"--proxy-server=127.0.0.1:8080")
    options.add_argument(f"--proxy-server={PROXIES['https'].replace('http://', '')}")
    # options.add_argument("-devtools")
    options.add_experimental_option("prefs", {
        "download.default_directory": local_dir,
    })

    user_agent, token = get_token()

    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--headless=new")

    with webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    ) as driver:
        sys.stdout.write("\rlogin...")
        driver.get(f"{IWARA_HOME}login")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".inputField"))
            )
            driver.execute_script(f"window.localStorage.setItem('token', '{token}');")  # Login
            driver.execute_script(f"window.localStorage.setItem('ecchi', '1');")  # I am over 18
            time.sleep(random.randint(1, 3))
            sys.stdout.write("\rfetch download url...")
            driver.get(url)

            try:
                download_button = WebDriverWait(driver, 20).until(
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
                if target_url is not None:
                    sys.stdout.write("\rstart download...")
                    driver.get(target_url)
                    driver.get("chrome://downloads")

                    while True:
                        progress_string = driver.execute_script("""
                            return function(){
                                let res = null;
                                let downloads_manager = document.querySelector("downloads-manager");
                                if (downloads_manager != null) {
                                    let frb0 = downloads_manager.shadowRoot.querySelector("#frb0");
                                    if (frb0 != null) {
                                        let description = frb0.shadowRoot.querySelector("#description");
                                        res = description.innerHTML;
                                    }
                                }
                                return res;
                            }();
                        """)
                        if progress_string is not None:
                            progress_string = progress_string.replace("\n", "").strip(" ")
                            # sys.stdout.write(f"\r{progress_string}")
                            if progress_string == "":
                                sys.stdout.write("\rCompleted.")
                                break
                            des_list = progress_string.replace(",", "").split(" ")
                            progress = 0
                            if des_list[4] == des_list[7]:
                                progress = min(int(math.floor(50 * (float(des_list[3]) / float(des_list[6])))), 50)
                            sys.stdout.write("\r[{}{}] {}/{} {} ETC: {}".format(
                                "=" * progress,
                                " " * (50 - progress),
                                des_list[3] + des_list[4],
                                des_list[6] + des_list[7].rstrip(","),
                                des_list[0] + des_list[1],
                                (des_list[8] if len(des_list) > 8 else "") + (des_list[9] if len(des_list) > 9 else "")
                            ))
            except TimeoutException:
                sys.stdout.write(" Timeout.")

        except TimeoutException:
            sys.stdout.write(" Timeout.")

        driver.quit()
        print("")


def main(user_name, file_prefix, download_index, profile_name=None):
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
            print("-" * 80)
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
        print(f"Reading Page No.{page + 1} ...")
        video_api = f"{IWARA_API}videos"
        video_api_req = requests.get(video_api, params={
            "user": user_id,
            "sort": "date",
            "page": page,
        }, proxies=PROXIES)
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
            video_list.append((
                video_url,
                item["title"],
            ))
        page += 1
        # print page, limit, page * limit, count
    # video_list.reverse()
    print("Video List:")
    for i, video in enumerate(video_list):
        print(u"{} {}".format(i + 1, video[1]))
        video_list[i] += (i + 1,)
    print("-" * 80)

    download_list = list()
    if len(download_index) > 0:
        for index in download_index:
            if index > 0:
                download_list.append(video_list[index - 1])
            else:
                download_list.append(video_list[index])
    else:
        download_list = video_list[:]
        download_list.reverse()

    for i, video in enumerate(download_list):
        print(f"{video[2]} {video[1]} {video[0]}")
        _file_prefix = "{}.{:03d}.".format(
            file_prefix if file_prefix != "" else user_name,
            video[2],
        )
        _file_name = u"{}.mp4".format(
            video[1].replace("/", " ").replace("?", " ").replace("*", " "),
        )

        print(f"Downloading to {_file_prefix + _file_name}")
        if os.path.exists(_file_prefix + _file_name):
            print("Completed.")
        else:
            tmp_dir = create_dir()
            download_file_with_progress(video[0], tmp_dir)
            actual_file_name = os.listdir(tmp_dir)[0]
            shutil.move(os.path.join(tmp_dir, actual_file_name), _file_prefix + _file_name)
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    USER_INFO.reverse()
    for user in USER_INFO:
        main(
            user["user_name"],
            user["file_prefix"],
            user["download_index"],
            user["profile_name"] if "profile_name" in user else None,
        )
        print("-" * 80)

    # print(download_file_with_progress("https://www.iwara.tv/video/VMtsceXOEFnGP9/mmdeevee-3"))
