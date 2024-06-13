import math
import requests
import os
import json
import time
import urllib.parse
import re


def chunks(arr, m):
    n = int(math.ceil(len(arr) / float(m)))
    return [arr[i:i + n] for i in range(0, len(arr), n)]


def getLabel(model, col):
    return [s[1] for s in model._fields[col].selection if s[0] == model[col]][0]


def check_selection(field, id):
    for s in field.selection:
        if id == s[0]:
            return True
    return False


def deleteDuplicate(li):
    temp_list = list(set([str(i) for i in li]))
    li = [eval(i) for i in temp_list]
    return li


def check_datetime(dates):
    for date in dates:
        try:
            time.strptime(date, "%Y-%m-%d %H:%M:%S")
        except:
            return False
    return True


def download_file(folder_path, url):
    # 发送GET请求获取文件内容
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        filename = urllib.parse.unquote(query_params.get('filename', [None])[0])
        # 打开本地文件准备写入
        with open(os.path.join(folder_path, filename), 'wb') as file:
            # 逐块写入文件
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return os.path.join(folder_path, filename)


def check_filetype(filename):
    filename = filename.lower()
    if filename.endswith('.docx') or filename.endswith('.pdf'):
        return True
    else:
        return False


def contains_only_letters_and_symbols(s, symbols=('：', ':', '.', ';', '')):
    pattern = f"^[a-zA-Z{''.join(symbols)}]+$"
    return bool(re.match(pattern, s))


def is_number(string):
    pattern = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')
    return bool(pattern.match(string))

def contains_chinese_or_english(text):
    # 使用正则表达式匹配中文字符和英文字符
    pattern = re.compile(r'[\u4e00-\u9fa5a-zA-Z]+')
    # 查找匹配项
    match = re.search(pattern, text)
    # 如果找到了匹配项，返回True；否则返回False
    return match is not None

def is_corpus(string):
    c1 = contains_only_letters_and_symbols(string)
    c2 = is_number(string)
    c3 = len(string) <= 2
    c4 = not contains_chinese_or_english(string)

    if c1 or c2 or c3 or c4:
        return False
    else:
        return True


def import_corpus(folder_path, msd_id):
    en_ends = ['en', 'EN', '英']
    cn_ends = ['cn', 'CN', '中']
    translation_files = []
    for f in os.listdir(folder_path):
        if msd_id and f != msd_id:
            continue
        print(f)
        try:
            path = os.path.join(folder_path, f)
            if os.path.isdir(path):
                msd_usr_id = f
                alignment_path = os.path.join(path, 'alignment')
                if os.path.exists(alignment_path):
                    file_num = len(os.listdir(alignment_path))
                    if file_num > 5:
                        en_file_dict = {}
                        cn_file_dict = {}

                        for filename in os.listdir(alignment_path):
                            if check_filetype(filename):
                                for end in en_ends:
                                    if end in filename:
                                        filename_start = filename.split(end)[0]
                                        en_file_dict[filename_start] = filename
                                for end in cn_ends:
                                    if end in filename:
                                        filename_start = filename.split(end)[0]
                                        cn_file_dict[filename_start] = filename

                        for key in en_file_dict:
                            if key in cn_file_dict:
                                translation_files.append({
                                    "msd_usr_id": msd_usr_id,
                                    "en": os.path.join(alignment_path, en_file_dict[key]),
                                    "cn": os.path.join(alignment_path, cn_file_dict[key])
                                })
        except Exception as e:
            print(e)

    print(translation_files)

    return translation_files
