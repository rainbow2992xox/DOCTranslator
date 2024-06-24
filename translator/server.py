import os
os.environ["CUDA_VISIBLE_DEVICES"]='2'

import time
import random
import sys

import requests
import json
import threading
import http.server as hs
import datetime
import traceback
from fastapi import FastAPI
import uvicorn
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional,Dict,Any
import asyncio

global_info = {'request_idx': 0,'threads_status':[]}
server_port = 30124
server_address = '0.0.0.0'
n_threads = 4
timeout=300

for i in range(n_threads):
    global_info['threads_status'].append(0)


from ebs.bge_eb import embeddings as bge
from trans.csan_trans import translator as en2cn_translator
from trans.gpt_trans import translator as gpt_e2c_translator
from rankers.B_ranker import reranker as branker
from Translator_main import dataLoader
from GPT import get_gpt_result

zh_ebd = bge('./models/ebd-zh/')
en_ebd = bge('./models/ebd-en/')
ranker = branker('./models/ranker/')

# 本地粗翻译
# en_translator = en2cn_translator('./models/translation_en2zh_base/')
# GPT粗翻译
en_translator = gpt_e2c_translator(get_gpt_result)

ebds = {'cn': zh_ebd, 'en': en_ebd}
dl = dataLoader(ebds, ranker,   translators={'en':en_translator})
app = FastAPI()

default_path = './save0.pkl'
import pickle
datas = pickle.load(open(default_path, 'rb'))
dl.load_data(datas)

@app.post("/")
async def main_post(post_data : Dict[Any,Any]):
    global global_info,dl
    global_info['request_idx'] += 1
    threads_status = global_info['threads_status']
    request_idx = global_info['request_idx']
    thread_idx = -1
    print(datetime.datetime.now(), "INFO[RECEIVE REQUEST]", request_idx, post_data)
    try:
        while (True):
            for i in range(0, len(threads_status)):
                if (threads_status[i] == 0 or time.time() - threads_status[i] >= timeout * 1.2):
                    thread_idx = i
                    threads_status[thread_idx] = time.time()
                    if('task' in post_data):
                        task = post_data['task']
                        if(task=='add_data'):
                            db_name = '_all'
                            if('db_name' in post_data):
                                db_name = post_data['db_name']
                            dl.add_data(post_data['data'],db_name=db_name)
                            save_path = default_path
                            if('save_path' in post_data):
                                save_path = post_data['save_path']
                            if(not 'do_save' in post_data or post_data['do_save']):
                                dl.save(save_path)
                            return JSONResponse(content={'status':0}, media_type='application/json')
                        if(task=='load_datas'):
                            dl = dataLoader(ebds, ranker, translators={'en': en_translator})
                            datas = pickle.load(open(post_data['save_path'], 'rb'))
                            dl.load_data(datas)
                            return JSONResponse(content={'status': 0}, media_type='application/json')
                        if(task=='get_entities'):
                            result = await dl.get_entities(post_data['data'])
                            return JSONResponse(content={'status': 0,'result':result}, media_type='application/json')
                        if(task=='duiqi'):
                            n_jobs = 1
                            if ('n_jobs' in post_data):
                                n_jobs = post_data['n_jobs']
                            result = await dl.duiqi_en_cn(post_data['data'],n_jobs=n_jobs)
                            return JSONResponse(content={'status': 0, 'result': result}, media_type='application/json')
                        if(task=='get_relate_score'):
                            result = await dl.get_relate_score(post_data['data'])
                            return JSONResponse(content={'status': 0, 'result': result}, media_type='application/json')
                        if(task=='translate'):
                            language_origin = post_data['language_origin']
                            language_target = post_data['language_target']
                            entity_knowledges = {}
                            if('entity_knowledges' in post_data):
                                entity_knowledges = post_data['entity_knowledges']
                            db_name = '_all'
                            if('db_name' in post_data):
                                db_name = post_data['db_name']
                            if('texts' in post_data):
                                texts = post_data['texts']
                                n_jobs = 1
                                if('n_jobs' in post_data):
                                    n_jobs = post_data['n_jobs']
                                result = await dl.translate_texts(texts, language_origin, language_target,
                                                            entity_knowledges=entity_knowledges, db_name=db_name,n_jobs=n_jobs)
                                return JSONResponse(content={'status': 0, 'result': result},
                                                    media_type='application/json')
                            else:
                                text = post_data['text']
                                result = await dl.translate(text,language_origin,language_target,entity_knowledges=entity_knowledges,db_name=db_name)
                                return JSONResponse(content={'status': 0, 'result': result}, media_type='application/json')
                    return JSONResponse(content={'status':1,'error_info':'Task Not Found','post_data':post_data}, media_type='application/json')
            await asyncio.sleep(0.2)
    except Exception as e:
        import traceback
        err_info = traceback.format_exc()
        return JSONResponse(status_code=500, content={'status': 1, 'error_info': str(err_info),'post_data':post_data},
                            media_type='application/json')
    finally:
        if (thread_idx >= 0):
            threads_status[thread_idx] = 0
        print('Thread Status:', threads_status)

if __name__ == "__main__":
    uvicorn.run(app, host=server_address, port=server_port,timeout_graceful_shutdown=timeout*2)
    print('---DONE---')