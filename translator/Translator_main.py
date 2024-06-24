import json
import sys
import warnings
import logging

import asyncio
import math
import random
import time

from MYDB import MyDB as db
from ebs.bge_eb import embeddings as bge
from GPT import get_gpt_result
from commons import parse_markdown_result
import numpy as np
from rankers.B_ranker import reranker as branker
from EntityExtractor import get_entities
from duiqi import find_en2cn_pairs,get_relate_score
from trans.csan_trans import translator as en2cn_translator
from trans.gpt_trans import translator as gpt_e2c_translator
import pickle

lang_map = {'en': '英文', 'cn': '中文'}


def get_pairs_markdown(language_origin, language_target, text_pairs):
    lang1 = lang_map[language_origin]
    lang2 = lang_map[language_target]
    res = '|原文(' + lang1 + ')|译文(' + lang2 + ')|\n|---|---|'
    for pair in text_pairs:
        res += '\n|' + pair[language_origin].replace('\n', '<br>').replace('\r', '') + '|' + pair[
            language_target].replace('\n', '<br>').replace('\r', '') + '|'
    return res


def get_entity_pairs_markdown(language_origin, language_target, entity_pairs):
    lang1 = lang_map[language_origin]
    lang2 = lang_map[language_target]
    res = '|专业词汇(' + lang1 + ')|专业词汇翻译(' + lang2 + ')|\n|---|---|'
    for pair in entity_pairs:
        res += '\n|' + pair[0].replace('\n', '<br>').replace('\r', '') + '|' + pair[1].replace('\n', '<br>').replace(
            '\r', '') + '|'
    return res


def get_translate_prompt(text, language_origin, language_target, entity_pairs=[], text_pairs=[]):
    cankao = False
    lang1 = lang_map[language_origin]
    lang2 = lang_map[language_target]
    prompt = ''
    if (len(text_pairs) > 0):
        cankao = True
        prompt += '以下是Markdown格式的文档翻译的例子:\n' + get_pairs_markdown(language_origin, language_target,
                                                                               text_pairs) + '\n\n'
    if (len(entity_pairs) > 0):
        cankao = True
        prompt += '以下是Markdown格式的专业词汇翻译的例子:\n' + get_entity_pairs_markdown(language_origin,
                                                                                          language_target,
                                                                                          entity_pairs) + '\n\n'
    prompt += '以下是一份需要翻译的' + lang1 + '文档:\n‘‘‘' + text + '’’’\n\n'
    if (cankao):
        prompt += '请结合提供的参考翻译资料，'
    prompt += '翻译以上文档，具体要求如下：'
    ridx = 1
    prompt += '\n' + str(ridx) + '、以Markdown表格形式输出，表头为："原文(' + lang1 + ')"、"译文(' + lang2 + ')"'
    ridx += 1
    if (cankao):
        prompt += '\n' + str(ridx) + '、如果参考资料中有需要翻译文档中的片段，需要优先参考使用。"'
        ridx += 1
    prompt += '\n' + str(ridx) + '、仅需要输出包含表头的完整的Markdown表格，不需要输出额外的文字和注释。'
    ridx += 1
    prompt += '\n' + str(ridx) + '、严格按照以下Markdown表头进行输出(输出包含表头)，只能在对应单元格填写译文，不能改变表格形式：\n'
    prompt += '|原文(' + lang1 + ')|译文(' + lang2 + ')|\n|---|---|\n|' + text.replace('\n', '<br>').replace('\r',
                                                                                                             '') + '||'
    return prompt


class dataLoader():
    def __init__(self, embedding_models, ranker, translators={}):
        self.embedding_models = embedding_models
        self.ranker = ranker
        self.dbs = {}
        self.translators = translators
        for lang in embedding_models:
            self.dbs[lang] = {}
            self.dbs[lang]['_all'] = db(embedding_models[lang])
            if (lang == 'cn'):
                global default_ebd
                default_ebd = embedding_models[lang]
        self.datas_map = {}
        self.datas_list = []

    def load_data(self, datas):
        for data in datas:
            key = data['key']
            self.datas_map[key] = data
            self.datas_list.append(data)
            for lang in self.embedding_models:
                db_name = '_all'
                if ('db_name' in data):
                    db_name = data['db_name']
                if (not db_name in self.dbs[lang]):
                    self.dbs[lang][db_name] = db(self.embedding_models[lang])
                if (lang in data):
                    self.dbs[lang][db_name].add_texts([key], vectors=[data[lang + '_vector']])
                    if (not db_name == '_all'):
                        self.dbs[lang]['_all'].add_texts([key], vectors=[data[lang + '_vector']])


    # sample {'cn':'XXXX','en':'XXXX'} source optional
    def add_data(self, data, db_name='_all'):
        data['db_name'] = db_name
        if not 'source' in data:
            data['source'] = ''
        if not 'key' in data:
            data['key'] = str(time.time()) + '_' + str(random.random())
        self.datas_map[data['key']] = data
        self.datas_list.append(data)
        for lang in self.embedding_models:
            if (not db_name in self.dbs[lang]):
                self.dbs[lang][db_name] = db(self.embedding_models[lang])
            if lang in data and not (lang + '_vector' in data):
                data[lang + '_vector'] = self.embedding_models[lang].get_vectors([data[lang]])[0]
            if lang in data:
                self.dbs[lang][db_name].add_texts([data['key']], vectors=[data[lang + '_vector']])
                if (not db_name == '_all'):
                    self.dbs[lang]['_all'].add_texts([data['key']], vectors=[data[lang + '_vector']])

    def save(self, path):
        file = open(path, 'wb+')
        pickle.dump(self.datas_list, file)
        file.close()

    # top1 score
    async def translate(self, text, language_origin, language_target, entity_knowledges={},db_name='_all'):
        entity_pairs = []
        for ename in entity_knowledges:
            for ename2 in entity_knowledges[ename]:
                entity_pairs.append([ename, ename2])
        trans_pairs = []
        references = []
        score0 = 0
        if(db_name in self.dbs[language_origin]):
            sres = self.dbs[language_origin][db_name].search([text], top_k=100, min_score=0.2)[0]
            if (len(sres) > 0):
                score0 = sres[0]['score']
            for data in sres:
                key = data['key']
                if (key in self.datas_map):
                    data2 = self.datas_map[key]
                    if (language_target in data2):
                        d2 = {}
                        d2[language_origin] = data2[language_origin]
                        d2[language_target] = data2[language_target]
                        trans_pairs.append(d2)
                        d3 = {'score': float(data['score'])}
                        for l in d2:
                            d3[l] = d2[l]
                        references.append(d3)
                if (len(trans_pairs) >= 10):
                    break
        # trans_pairs = []
        # references = []
        # print(trans_pairs)
        prompt = get_translate_prompt(text, language_origin, language_target, text_pairs=trans_pairs,
                                      entity_pairs=entity_pairs)
        # print(prompt)
        gpt_result = await get_gpt_result(prompt)
        md_result = parse_markdown_result(gpt_result, 2)
        if (len(md_result) >= 1 and len(md_result[0]) >= 2):
            rtext = md_result[0][1]
            rtext = rtext.replace('<br>', '\n').replace('<br/>', '\n')
            score1 = float(self.ranker.get_rank_scores(text, [rtext])[0])
            score1 = (score1 + 10) / 20
            if (score0 > score1):
                score1 = (2 * score0 + score1) / 3
                score2 = score1 + (1 - score1) * math.pow(score0, 3)
                score1 = max(score1, score2)
            if (score1 < 0.3):
                score1 = 0.3
            return {'result': rtext, 'score': score1, 'references': references}
        return None

    async def translate_texts(self, texts, language_origin, language_target, entity_knowledges={}, db_name='_all',n_jobs=1):
        semaphore = asyncio.Semaphore(n_jobs)
        async def limited_task(task):
            async with semaphore:  # 使用Semaphore来限制同时执行的任务数
                result = await task
                return result
        tasks = []
        for i in range(len(texts)):
            tasks.append(limited_task(self.translate(texts[i],language_origin,language_target,entity_knowledges=entity_knowledges,db_name=db_name)))
        results = await asyncio.gather(*tasks)
        return results
    async def get_entities(self, input):
        el = input['a_list']
        entities = []
        aids = []
        decps = []
        for obj in el:
            entities.append(obj['name'])
            aids.append(obj['a_id'])
            if ('description' in obj and len(obj['description'].strip()) > 0):
                s = '"' + obj['name'] + '"的定义是：' + obj['description']
                s = s.replace('\r', '').replace('\n', '<br/>')
                decps.append(s)
        langs = []
        texts = []
        for lang in self.embedding_models:
            if (lang in input):
                langs.append(lang)
                texts.append(input[lang])
        results1 = await get_entities(texts, langs, entities=entities, descriptions=decps)
        results = []
        for obj in results1:
            data = []
            for i in range(len(entities)):
                ename = entities[i]
                eid = aids[i]
                d2 = {}
                for lang in langs:
                    if (lang in obj and ename in obj[lang]):
                        d2[lang] = {'a_id': eid, "name": ename, "value": obj[lang][ename]}
                    else:
                        d2[lang] = {'a_id': eid, "name": ename, "value": ''}
                data.append(d2)
            results.append(data)
        return results

    async def duiqi_en_cn(self, input,n_jobs=1):
        return await find_en2cn_pairs(input, self.ranker, translator=self.translators['en'],n_jobs=n_jobs)

    async def get_relate_score(self,data):
        return await get_relate_score(data,self.ranker,translator=self.translators['en'])

if __name__ == '__main__':
    stime = time.time()
    # 初始化
    zh_ebd = bge('./models/ebd-zh/')
    en_ebd = bge('./models/ebd-en/')
    ranker = branker('./models/ranker/')
    #本地粗翻译
    # en_translator = en2cn_translator('./models/translation_en2zh_base/')
    #GPT粗翻译
    en_translator = gpt_e2c_translator(get_gpt_result)
    ebds = {'cn': zh_ebd, 'en': en_ebd}
    dl = dataLoader(ebds, ranker, translators={'en': en_translator})  # {'en':en_translator}
    print('-----初始化完成-----')
    # 加载数据

    datas = pickle.load(open('./datas.pkl', 'rb'))
    dl.load_data(datas)
    print('-----加载完成-----')

    # 添加数据
    s_cn = "在研究治疗干预首次给药前24小时（对于尿液检测）或72小时（对于血清检测）内，根据当地法规要求进行的高灵敏度妊娠试验（尿液或血清）结果为阴性。如不能确定尿液试验结果为阴性（例如，结果不明确），则需进行血清妊娠试验。在这种情况下，如果血清妊娠结果呈阳性，则必须将受试者从研究中排除。研究干预期间和之后进行妊娠试验的其他要求请参见第8.3.5节。"
    s_en = "Has a negative highly sensitive pregnancy test (urine or serum) as required by local regulations within 25 hours (for a urine test) or 72 hours (for a serum test) before the first dose of study intervention. If a urine test cannot be confirmed as negative (eg.an ambiguous result), a serum pregnancy test is required. In such cases, the participant must be excluded from participation if the serum pregnancy result is positive.Additional requirements for pregnancy testing during and after study intervention are in Section 8.3.5."
    adata = {'cn': s_cn, 'en': s_en}
    dl.add_data(adata,db_name='test1')
    print('-----添加完成-----')
    #保存数据
    dl.save('./save1.pkl')
    print('-----保存完成-----')

    #获取相关分数
    print('\n#####相关分数案例一#####',asyncio.run(dl.get_relate_score({"cn":"你好嘛","en":"hello"})))
    print('-----相关分数完成-----')

    #实体提取
    sample_input1 = {
        "en": s_en,
        "cn": s_cn,
        "a_list": [
            {
                "a_id": "1",
                "name": "检验名称"
            },
            {
                "a_id": "2",
                "name": "检验条件",
                "description": "检验条件是值该检验在给药前的时间。"
            }
        ]
    }
    print('\n#####实体提取案例一#####',asyncio.run(dl.get_entities(sample_input1)))
    sample_input2 = {
        "cn": s_cn,
        "a_list": [
            {
                "a_id": "1",
                "name": "专业词汇",
                "description":"专业词汇是指医学领域的词汇，通常是一个完整的单词，不带描述。"
            }
        ]
    }
    print('\n#####实体提取案例二#####',asyncio.run(dl.get_entities(sample_input2)))
    print('\n-----提取完成-----')
    #翻译
    s_trans_en = "Has a negative highly sensitive pregnancy test (urine or serum) as required by local regulations within 29 hours (for a urine test) or 76 hours (for a serum test) before the first dose of study intervention. If a urine test cannot be confirmed as negative (eg.an ambiguous result), a serum pregnancy test is required. In such cases, the participant must be excluded from participation if the serum pregnancy result is positive.Additional requirements for pregnancy testing during and after study intervention are in Section 8.3.5."
    print('\n#####翻译案例一#####',asyncio.run(dl.translate(s_trans_en,'en','cn')))
    s_trans_cn = "允许前瞻性批准招募和入选标准的方案偏低。"
    print('\n#####翻译案例二#####',asyncio.run(dl.translate(s_trans_cn,'cn','en')))
    texts = ['你的名字是什么?','你好','我去上学。','吃饭了么']
    print('\n#####翻译案例三（多并发）#####',asyncio.run(dl.translate_texts(texts,'cn','en',n_jobs=4)))
    print('\n-----翻译完成-----')

    #对齐
    duiqi_input1 = {
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

    print('\n#####对齐案例一(4线程)#####',asyncio.run(dl.duiqi_en_cn(duiqi_input1,n_jobs=4)))
    print('\n-----对齐完成-----')
    # 对齐添加专有名词知识协助翻译
    s_trans_en2 = 'ALT (SGPT)=alanine aminotransferase (serum glutamic pyruvic transaminase), AST (SGOT)=aspartate aminotransferase (serum glutamic oxaloacetic transaminase)  GFR=glomerular filtration rate;ULN=upper limit of normal'
    print('\n#####专有名词协助翻译（不添加知识对照组）#####', asyncio.run(dl.translate(s_trans_en2, 'en', 'cn')))
    entity_knowledges = {'alanine aminotransferase':['丙氨酸氨基转移酶'],'aspartate aminotransferase':['天门冬氨酸氨基转移酶']}
    print('\n#####专有名词协助翻译（添加知识组）#####', asyncio.run(dl.translate(s_trans_en2, 'en', 'cn',entity_knowledges=entity_knowledges)))
    print('\n-----专有名词协助翻译完成-----')

    s_trans_en = "Has a negative highly sensitive pregnancy test (urine or serum) as required by local regulations within 29 hours (for a urine test) or 76 hours (for a serum test) before the first dose of study intervention. If a urine test cannot be confirmed as negative (eg.an ambiguous result), a serum pregnancy test is required. In such cases, the participant must be excluded from participation if the serum pregnancy result is positive.Additional requirements for pregnancy testing during and after study intervention are in Section 8.3.5."
    print('\n#####指定数据库翻译案例一#####',asyncio.run(dl.translate(s_trans_en,'en','cn',db_name='test1')))
    print('\n-----指定数据库翻译完成-----')
    print('\n-----ALL DONE-----',time.time()-stime)
