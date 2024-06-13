import math
import json
import time
import docx
import requests
import sys

# url = 'http://101.35.211.193:31002'
# url = 'https://ac344ht1868.vicp.fun'
url = 'http://languagerepo-devtest.merck.com:30124'
# url = 'http://lit-research-poc.merck.com:30124'


def agent_align(doc_dict):
    payload = {
        "task": "duiqi", "data": doc_dict
    }

    headers = {
        'Content-Type': 'application/json',
    }
    try_count = 0
    while True:
        try:
            print(payload)

            res = requests.request('POST', url, headers=headers, json=payload)
            print(res.json())
            return res.json()['result']
        except Exception as e:
            try_count += 1
            print('-----语料对齐失败重试-----')
            print(e)
            time.sleep(1)

        if try_count >= 3:
            return False


def agent_extract(text_dict):
    payload = {
        "task": "get_entities", "data": text_dict
    }

    headers = {
        'Content-Type': 'application/json',
    }

    try_count = 0
    while True:
        try:
            res = requests.request('POST', url, headers=headers, json=payload)
            print(payload)
            print(payload)
            print(res.json())
            return res.json()['result']
        except Exception as e:
            try_count += 1
            print('-----实体提取失败重试-----')
            print(e)
            time.sleep(1)

        if try_count >= 3:
            return False


def add_data(adata, db_name=None):
    payload = {
        "task": "add_data", "data": adata
    }

    if db_name:
        payload['db_name'] = db_name

    headers = {
        'Content-Type': 'application/json',
    }

    res = requests.request('POST', url, headers=headers, json=payload)
    print(payload)
    print(res.json())
    return res.json()


def agent_translate(text, source_lang, target_lang, technical_terms, db_name=None):
    payload = {
        "task": "translate",
        "text": text,
        "language_origin": source_lang,
        "language_target": target_lang,
        "entity_knowledges": technical_terms
    }

    if db_name:
        payload['db_name'] = db_name

    headers = {
        'Content-Type': 'application/json',
    }

    try_count = 0
    while True:
        try:
            res = requests.request('POST', url, headers=headers, json=payload)
            print(payload)
            print(res.json())
            res = res.json()['result']
            return (res['result'], res['score'], res['references'])
        except Exception as e:
            try_count += 1
            print('-----翻译失败重试-----')
            print(text)
            print(e)
            time.sleep(1)

        if try_count >= 3:
            return False
