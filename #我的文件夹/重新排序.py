import os

new_order_path = r"G:\CloneCode_1\iwara_crawler-master\#错误备份\视频列表_紳士枠.txt" # 新序号文件
need_order_dir = r"G:\CloneCode_1\iwara_crawler-master\downloads\[搜索]紳士枠" # 需要重新排序的目录
file_prefix = "紳士枠." # 文件前缀

def get_new_order_list(new_order_path)-> list[tuple[str, str]]:
    """ 获取新的序号 """
    new_order_list = []
    with open(new_order_path, "r", encoding="utf-8") as f:
        for line in f:
            new_order = "%03d" % int(line.strip()[:line.find(" ")])
            # ---------------------
            filename_start_index = line.find(" ") + 1
            filename_end_index = line.rfind(" ", filename_start_index, line.rfind(" "))
            filename = u"{}.mp4".format(
                    line[filename_start_index:filename_end_index]
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
            # ---------------------
            new_order_list.append((new_order, filename))
    return new_order_list

count = 0
total_count = 2
while count < total_count:
    count += 1
    need_order_list = os.listdir(need_order_dir)
    new_order_list = get_new_order_list(new_order_path)
    # 002 【MMD】江風でPINK CAT(ハンドリメイク).mp4
    for (new_order, new_filename) in new_order_list:
        for need_item in need_order_list:
            if need_item.startswith(file_prefix):
                old_order = need_item[len(file_prefix) : need_item.find(".", len(file_prefix))]
                filename = need_item[len(file_prefix) + len(old_order) + 1 : ]

                if (filename.replace(".lnk", "") == new_filename) and (old_order != new_order):
                    old_path = os.path.join(need_order_dir, need_item)
                    fullname = f"{file_prefix}{new_order}.{filename}"
                    new_path = os.path.join(need_order_dir, fullname)

                    if os.path.exists(new_path) or os.path.exists(new_path.replace(".lnk", "")) or os.path.exists(new_path+".lnk"):
                        print(f"文件已存在：{new_path}")
                        continue
                    
                    print(f"{old_path}\n--->\n{new_path}\n\n")
                    os.rename(old_path, new_path)
                    # need_order_list.remove(need_item)
                    print("\n")
    print(f"运行次数：{count}")