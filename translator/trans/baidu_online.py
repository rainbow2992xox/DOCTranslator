import time
import requests
import json

appKey = 'SCqSoggjYKNsplo22Juj7WtO'
appSec = 'GBgxiWtPROnSVrOzKsl0ZYYoJeEF3ycE'
token_info = {'time': 0, 'token': ''}
def get_baidu_token():
    global token_info
    for i in range(0, 5):
        try:
            if (time.time() - token_info['time'] < 3000):
                return token_info['token']
            url = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+appKey+'&client_secret='+appSec

            payload = ""
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload,timeout=60)
            robj = json.loads(str(response.text))
            token = robj['access_token']
            token_info['time'] = time.time()
            token_info['token'] = token
            return token
        except Exception as ex:
            time.sleep(1)
    return None

async def get_en2cn_translate_text(query):
    try:
        from_lang = 'en'
        to_lang = 'zh'
        headers = {'Content-Type': 'application/json'}
        payload = {'q': query, 'from': from_lang, 'to': to_lang}
        url = 'https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token=' + get_baidu_token()
        # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()
        return result['result']['trans_result'][0]['dst']
    except Exception as e:
        return ''

if __name__ == '__main__':
    stime = time.time()
    print(get_en2cn_translate_text('你好世界'))
    print(time.time()-stime)