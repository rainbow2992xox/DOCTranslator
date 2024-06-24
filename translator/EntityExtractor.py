from GPT import get_gpt_result
import asyncio
from commons import parse_markdown_result

lang_map = {'en': '英文', 'cn': '中文'}


def get_extract_entity_prompt(text, language, entities=[],descriptions=[]):
    for i in range(len(entities)):
        entities[i] = entities[i].replace('\n', '<br>').replace('\r', '').replace('|', '/')
    lang = lang_map[language]
    if (len(entities) == 0):
        entities = ['专有名词']
        if (language == 'en'):
            entities = ['special nouns']
    headers1 = ''
    headers2 = ''
    entity_str = ''
    for e in entities:
        if (len(entity_str) > 0):
            entity_str += '、'
        entity_str += '"' + e + '"'
        headers1 += '|' + e
        headers2 += '|---'
    headers1 += '|'
    headers2 += '|'

    prompt = '以下是一段' + lang + '文档：\n‘‘‘' + text + '’’’'
    prompt += '\n\n请根据以上文档，提取文档中提及的所有如下信息的专有名词:' + entity_str + '。具体要求如下。'
    prompt += '\n1、以Markdown表格形式输出，表头为：' + entity_str + '。'
    ridx=2
    for i in range(len(descriptions)):
        prompt += '\n' + str(ridx) + '、'+descriptions[i]
        ridx = ridx+1
    prompt += '\n'+str(ridx)+'、请严格按照给定文档进行提取，不能添加和编造信息。'
    prompt += '\n'+str(ridx+1)+'、仅需要输出包含表头的完整的Markdown表格，输出语言为' + lang + ',不需要注释和其他额外输出。'
    prompt += '\n'+str(ridx+2)+'、严格按照以下Markdown表头进行输出(输出包含表头),输出语言为' + lang + ':\n' + headers1 + '\n' + headers2
    return prompt, entities


def get_extract_entity_pairs_prompt(text1, language1,text2, language2, entities=[],datas=[]):
    for i in range(len(entities)):
        entities[i] = entities[i].replace('\n', '<br>').replace('\r', '').replace('|', '/')
    lang1 = lang_map[language1]
    lang2 = lang_map[language2]
    headers1 = ''
    headers2 = ''
    entity_str = ''
    for e in entities:
        if (len(entity_str) > 0):
            entity_str += '、'
        entity_str += '"' + e + '"'
        headers1 += '|' + e
        headers2 += '|---'
    headers1 += '|'
    headers2 += '|'
    prompt = '以下是一段' + lang1 + '文档：\n‘‘‘' + text1 + '’’’'
    prompt+= '\n\n对应着以上文档，以下是一段' + lang2 + '翻译：\n‘‘‘' + text2 + '’’’'
    prompt += '\n\n我将提供给你一写'+lang1+'的专有词汇，帮我在'+lang2+'的翻译中找到对应的词汇。具体要求如下：'
    prompt += '\n1、以Markdown表格形式输出，表头为：' + entity_str + '。'
    prompt += '\n2、在所有表头以('+lang1+')为结尾的列中提供的名词都需要找到对应的翻译词汇，并填写到以('+lang2+')为结尾的对应列中。'
    prompt += '\n3、如果表头以(' + lang1 + ')为结尾的列中为空，则对应的翻译单元格也无需输出。'
    prompt += '\n4、请严格按照给定文档进行提取，不能添加和编造信息。'
    prompt += '\n5、仅需要输出包含表头的完整的Markdown表格,不需要注释和其他额外输出。'
    prompt += '\n6、严格按照以下Markdown表头进行输出(输出包含表头):\n' + headers1 + '\n' + headers2
    for data in datas:
        line = '\n|'
        for s in data:
            line+=s+'||'
        prompt+=line
    return prompt

async def get_entities(texts, languages=['zh'], entities=[],descriptions=[]):
    prompt1, ents2 = get_extract_entity_prompt(texts[0], languages[0], entities,descriptions=descriptions)
    gpt_result = await get_gpt_result(prompt1)
    md_result = parse_markdown_result(gpt_result, len(ents2), first_header=ents2[0])
    results = []
    for data in md_result:
        if (len(data) >= len(ents2)):
            d = {}
            for i in range(len(ents2)):
                d[ents2[i]] = data[i]
            results.append({languages[0]: d})
    if(len(languages)==1 or len(results)==0):
        return results
    lang1 = lang_map[languages[0]]
    lang2 = lang_map[languages[1]]
    ents3 = []
    for e in ents2:
        ents3.append(e+'('+lang1+')')
        ents3.append(e+'('+lang2+')')
    datas = []
    for data in results:
        arr = []
        for e in ents2:
            arr.append(data[languages[0]][e])
        datas.append(arr)
    prompt2 = get_extract_entity_pairs_prompt(texts[0],languages[0],texts[1],languages[1],entities=ents3,datas=datas)
    gpt_result2 = await get_gpt_result(prompt2)
    md_result2 = parse_markdown_result(gpt_result2, len(ents3))
    results = []
    for data in md_result2:
        if (len(data) >= len(ents3)):
            d1 = {}
            d2 = {}
            for i in range(0,len(ents2)):
                if(i*2+1<len(data)):
                    d1[ents2[i]] = data[i*2]
                    d2[ents2[i]] = data[i*2+1]
            results.append({languages[0]:d1,languages[1]:d2})
    return results
if __name__ == '__main__':
    s_zh = "在研究治疗干预首次给药前24小时（对于尿液检测）或72小时（对于血清检测）内，根据当地法规要求进行的高灵敏度妊娠试验（尿液或血清）结果为阴性。如不能确定尿液试验结果为阴性（例如，结果不明确），则需进行血清妊娠试验。在这种情况下，如果血清妊娠结果呈阳性，则必须将受试者从研究中排除。研究干预期间和之后进行妊娠试验的其他要求请参见第8.3.5节。"
    s_en = "Has a negative highly sensitive pregnancy test (urine or serum) as required by local regulations within 24 hours (for a urine test) or 72 hours (for a serum test) before the first dose of study intervention. If a urine test cannot be confirmed as negative (eg.an ambiguous result), a serum pregnancy test is required. In such cases, the participant must be excluded from participation if the serum pregnancy result is positive.Additional requirements for pregnancy testing during and after study intervention are in Section 8.3.5."
    print(asyncio.run(get_entities([s_zh,s_en], ['cn','en'], ['检验项目','检验条件'])))
    # print(asyncio.run(get_entities([s_zh,s_en], ['zh','en'], ['专有名词'])))
    # prompt = get_extract_entity_pairs_prompt(s_zh,'zh',s_en,'en',['专有名词(中文)','专有名词(英文)'],datas=[['高灵敏度妊娠试验'],['尿液检测'],['血清检测']])
    # print(prompt)
    # [{'zh': {'专有名词': '高灵敏度妊娠试验'}}, {'zh': {'专有名词': '尿液检测'}}, {'zh': {'专有名词': '血清检测'}}, {'zh': {'专有名词': '尿液试验'}}, {'zh': {'专有名词': '血清妊娠试验'}}, {'zh': {'专有名词': '研究干预'}}, {'zh': {'专有名词': '妊娠试验'}}]
    # print(asyncio.run(get_gpt_result(prompt)))
    print('---DONE---')
