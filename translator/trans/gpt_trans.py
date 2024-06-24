import json
import aiohttp

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

def parse_markdown_result(markdown_text, n_headers, first_header=''):
    texts = markdown_text.split("\n")
    first_index = -1
    row_index = 0
    results = []
    for i in range(0, len(texts)):
        text = texts[i].strip().replace('\r', '').replace('\n', '<br/>').replace(',', '，')
        arr = text.split('|')
        if (len(arr) >= n_headers):
            if (first_index == -1):
                if (len(arr) > n_headers):
                    if (len(first_header) == 0 or (len(first_header) > 0 and arr[1].find(first_header) >= 0)):
                        first_index = 1
                else:
                    if (len(arr) == n_headers):
                        if (len(first_header) == 0 or (len(first_header) > 0 and arr[0].find(first_header) >= 0)):
                            first_index = 0
            else:
                # print(arr, first_index)
                row_index = row_index + 1
                if (row_index > 1):
                    row_data = []
                    for j in range(0, n_headers):
                        if(first_index + j>=len(arr)):
                            break
                        row_data.append(arr[first_index + j].strip())
                    results.append(row_data)
    if(len(results)==0 and markdown_text.find('|')>=0 and not markdown_text.__contains__('---')):
        header = '|'
        for i in range(n_headers):
            if(i==0 and len(first_header)>0):
                header+=first_header+'|'
            else:
                header+='XXX|'
        header+='\n|'
        for i in range(n_headers):
            header += '---|'
        return parse_markdown_result(header+'\n'+markdown_text,n_headers,first_header=first_header)
    return results
def get_translate_prompt(text, language_origin,language_target):
    prompt = ''
    prompt += '以下是一份需要翻译的' + language_origin + '文档:\n‘‘‘' + text + '’’’\n\n'
    prompt += '翻译以上文档，具体要求如下：'
    ridx = 1
    prompt += '\n' + str(ridx) + '、以Markdown表格形式输出，表头为："原文(' + language_origin + ')"、"译文(' + language_target + ')"'
    ridx += 1
    prompt += '\n' + str(ridx) + '、仅需要输出包含表头的完整的Markdown表格，不需要输出额外的文字和注释。'
    ridx += 1
    prompt += '\n' + str(ridx) + '、严格按照以下Markdown表头进行输出(输出包含表头)，只能在对应单元格填写译文，不能改变表格形式：\n'
    prompt += '|原文(' + language_origin + ')|译文(' + language_target + ')|\n|---|---|\n|' + text.replace('\n', '<br>').replace('\r',                                                                                                             '') + '||'
    return prompt

def get_translate_prompt2(text, language_origin,language_target):
    prompt = ''
    prompt += '以下是一份需要翻译的' + language_origin + '文档:\n‘‘‘' + text + '’’’\n\n'
    prompt += '请将上述文档翻译成'+language_target+'，并输出翻译结果。只用输出翻译结果，不需要输出额外的符号或文字说明。'
    return prompt

class translator():
    def __init__(self,gpt):
        self.gpt = gpt

    async def translate(self,text,language_origin='英文',language_target='中文'):
        try:
            prompt1 = get_translate_prompt(text,language_origin,language_target)
            gpt_resp1 =  await self.gpt(prompt1)
            md_result = parse_markdown_result(gpt_resp1, 2)
            if (len(md_result) >= 1 and len(md_result[0]) >= 2):
                return md_result[0][1]
            return await self.gpt(get_translate_prompt2(text,language_origin,language_target))
        except Exception as e:
            return ''

if __name__ == '__main__':
    import asyncio
    async def get_gpt_result_yy(query, top_p=0.01, temperatrue=0.01, max_tokens=4096):
        gpt_url = 'http://101.35.211.193:31001/fast_chat'
        data = {'text': query, 'history': [], 'top_p': top_p, 'temperature': temperatrue, 'max_tokens': max_tokens}
        status, result = await async_post(gpt_url, data)
        response = json.loads(str(result))
        return response['result']
    trans = translator(get_gpt_result_yy)
    print(asyncio.run(trans.translate('')))
    print('---DONE---')