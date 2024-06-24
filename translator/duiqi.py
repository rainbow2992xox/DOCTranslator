import asyncio
import time

from trans.baidu_online import get_en2cn_translate_text
from rankers.B_ranker import reranker as branker

async def get_translate_results(texts,translator,n_jobs=1):
    semaphore = asyncio.Semaphore(n_jobs)
    async def limited_task(task):
        async with semaphore:  # 使用Semaphore来限制同时执行的任务数
            result = await task
            return result
    tasks = []
    for i in range(len(texts)):
        tasks.append(limited_task(translator.translate(texts[i])))
    results = await asyncio.gather(*tasks)
    for i in range(len(texts)):
        if(len(texts[i].strip())==0):
            results[i] = ''
    print(results)
    return results
async def find_en2cn_pairs(input,ranker,translator=None,n_jobs=1):
    cn_texts = []
    cn_ids = []
    en_texts =[]
    en_ids = []
    for d in input['cn']:
        if('type' in d and 'id' in d and 'text' in d):
            t = d['type'].strip().lower()
            if(t=='title' or t=='text'):
                cn_ids.append(d['id'])
                cn_texts.append(d['text'])
            else:
                if(t=='table'):
                    print(d)
                    cn_ids.append(d['id'])
                    cn_texts.append(str(d['data']))
                else:
                    continue

    for d in input['en']:
        if('type' in d and 'id' in d and 'text' in d):
            t = d['type'].strip().lower()
            if(t=='title' or t=='text'):
                en_ids.append(d['id'])
                en_texts.append(d['text'])
            else:
                if (t == 'table'):
                    en_ids.append(d['id'])
                    en_texts.append(str(d['data']))
                else:
                    continue

    # en_trans = []
    # for i in range(len(en_texts)):
    #     t = en_texts[i].strip()
    #     if(len(t)==0):
    #         en_trans.append('')
    #     else:
    #         if(translator is None):
    #             en_trans.append(await get_en2cn_translate_text(t))
    #         else:
    #             en_trans.append(await translator.translate(t))
    en_trans = await get_translate_results(en_texts,translator,n_jobs=n_jobs)
    last_match = 0
    results = []
    for i in range(len(cn_texts)):
        n1 = min(i-20,last_match-20)
        if(n1<=0):
            n1 = 0
        n2 = max(i+21,last_match+21)
        if(n2>=len(en_trans)):
            n2 = len(en_trans)
        trans_compares = []
        id_compares = []
        for j in range(n1,n2):
            trans_compares.append(en_trans[j])
            id_compares.append(j)
        scores = ranker.get_rerank_result(cn_texts[i],trans_compares,keys=id_compares,min_score=2.5)
        if(len(scores)>0):
            j = scores[0]['key']
            match_score = (float(scores[0]['score'])+10)/20
            if(match_score>1):
                match_score = 1
            if(match_score<0):
                match_score = 0
            if(match_score>=0.6):
                match_score = 0.8+0.2*(match_score-0.6)/0.4
            else:
                match_score = 0.8*match_score/0.6
            cn_length = len(cn_texts[i])
            en_length = len(en_trans[j])
            ratio = cn_length/en_length
            if(ratio<1):
                ratio = 1/ratio
            if(ratio>2):
                match_score = match_score/(ratio-1)

            last_match = j
            d = {'en':{'id':en_ids[j],'text':en_texts[j]},'cn':{'id':cn_ids[i],'text':cn_texts[i]},'score':match_score}
            results.append(d)
    return results

async def get_relate_score(data,ranker,translator=None):
    en_text = data['en']
    cn_text = data['cn']
    en_trans = None
    if (translator is None):
        en_trans = await get_en2cn_translate_text(en_text)
    else:
        en_trans = await translator.translate(en_text)
    match_score = ranker.get_rank_scores(cn_text,[en_trans])[0]
    if(cn_text.strip()==en_trans.strip()):
        match_score = 10
    # print(cn_text,en_trans,match_score)
    match_score = (float(match_score) + 10) / 20
    if (match_score > 1):
        match_score = 1
    if (match_score < 0):
        match_score = 0
    if (match_score >= 0.6):
        match_score = 0.8 + 0.2 * (match_score - 0.6) / 0.4
    else:
        match_score = 0.8 * match_score / 0.6
    cn_length = len(cn_text)
    en_length = len(en_trans)
    ratio = cn_length / en_length
    if (ratio < 1):
        ratio = 1 / ratio
    if (ratio > 2):
        match_score = match_score / (ratio - 1)
    return match_score

if __name__ == '__main__':
    input = {
        "en": [
            {
                "id": "en1",
                "type": "Title",
                "text": "As stated in the Code of Conduct for Clinical Trials (Appendix 1.1), this study includes participants of varying age (as applicable), race, ethnicity, and sex (as applicable). The collection and use of these demographic data will follow all local laws and participant confidentiality guidelines while supporting the study of the disease, its related factors,and the IMP under investigation."
            },
            {
                "id": "en2",
                "type": "Text",
                "text": "Prospective approval of protocol deviations to recruitment and enrollment criteria,also known as protocol waivers or exemptions,is not permitted."
            },
            {
                "id": "en3",
                "type": "Text",
                "text": "An individual is eligible for inclusion in the study if the individual meets all of the following criteria:"
            },
            {
                "id": "en4",
                "type": "Text",
                "text": "This is not included."
            }
        ],
        "cn": [
            {
                "id": "cn1",
                "type": "Title",
                "text": "这段话是测试的，其实呢他并不存在。佛挡杀佛第三方防守打法广发的想法吃个肉东方闪电焚烧发电"
            },
            {
                "id": "cn2",
                "type": "Text",
                "text": "如临床试验实施准则（附录1.1）所述，本研究入组了不同年龄（如适用）、人种、种族和性别（如适用）的受试者。这些人口统计学数据的收集和使用将遵循所有当地法律和受试者保密指南，同时为疾病、其相关因素和在研IMP的研究提供支持。"
            },
            {
                "id": "cn3",
                "type": "Text",
                "text": "不允许前瞻性批准招募和入选标准的方案偏离（也称为方案豁免或免除）。 "
            },{
                "id": "cn4",
                "type": "Text",
                "text": "如果受试者符合以下所有标准，则有资格入选本研究： "
            }]}
    ranker = branker('./models/ranker/')
    # from trans.csan_trans import translator as translator1
    # trans = translator1(r"C:\proj\chat\LLM2402\translator\models\translation_en2zh_base")
    start_time = time.time()
    from GPT import get_gpt_result
    from trans.gpt_trans import translator as gpt_e2c_translator
    trans = gpt_e2c_translator(get_gpt_result)
    print(asyncio.run(find_en2cn_pairs(input,ranker,translator=trans,n_jobs=10)))
    print(asyncio.run(get_relate_score({"cn":"你好","en":"hello"},ranker,translator=trans)))
    print('---DONE---',time.time()-start_time)
