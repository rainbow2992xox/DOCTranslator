import asyncio
import time

import aiohttp
import json
from openai import AsyncAzureOpenAI

client = AsyncAzureOpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    azure_endpoint="https://iapi-test.merck.com/gpt/libsupport",
    api_version="2024-05-01-preview"
)

async def async_post(url, data, timeout=1000, header=None):
    async with aiohttp.ClientSession() as session:
        if header is None:
            async with session.post(url, json=data, timeout=timeout) as response:
                status = response.status
                return status, await response.text()
        else:
            async with session.post(url, json=data, timeout=timeout, headers=header) as response:
                status = response.status
                return status, await response.text()


async def get_gpt_result_yy(query, top_p=0.01, temperatrue=0.01, max_tokens=4096):
    gpt_url = 'http://101.35.211.193:31001/fast_chat'
    data = {'text': query, 'history': [], 'top_p': top_p, 'temperature': temperatrue, 'max_tokens': max_tokens}
    status, result = await async_post(gpt_url, data)
    response = json.loads(str(result))
    return response['result']


async def get_gpt_result_ali(query, top_p=0.0, temperatrue=0.0, max_tokens=2000):
    gpt_url = 'https://dashscope.aliyuncs.com/api/v1/apps/228df0170bf441cc9d0d05fa5f5e728a/completion'
    data = {"input": {"prompt": query,'top_p': top_p, 'temperature': temperatrue, 'max_tokens': max_tokens},
            "parameters": {'top_p': top_p, 'temperature': temperatrue, 'max_tokens': max_tokens}, "debug": {}}
    header = {'Authorization': 'Bearer sk-yj3Sa8YueN'}
    status, result = await async_post(gpt_url, data, header=header)
    response = json.loads(str(result))
    # print('############################',response["output"]["text"])
    return response["output"]["text"]


async def gen_result(query):
    messages=[{"role":"user","content":query}]

    try:
        chat = await client.chat.completions.create(model="gpt-4-turbo-2024-04-09",messages=messages,temperature=0.0)
        reply = chat.choices[0].message.content
        return reply
    except Exception as e:
        print(e)
        return ""

async def get_gpt_result(query):
    # 选择hitales服务
    # return await get_gpt_result_yy(query)

    # 选择阿里云服务
    # return await get_gpt_result_ali(query)

    # MSD服务
    return await gen_result(query)


if __name__ == '__main__':
    stime = time.time()
    print(asyncio.run(get_gpt_result('写一首关于长江诗歌，不超过50个字。')))
    print('---DONE---', time.time() - stime)
