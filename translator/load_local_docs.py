import json
from ebs.bge_eb import embeddings as bge
# 打开JSON文件
with open('documents.json', 'r', encoding='utf-8') as file:
    # 解析文件内容为Python数据结构（通常是字典）
    datas = json.load(file)

zh_ebd = bge('D:/models/AI-ModelScope/bge-base-zh-v1___5')
en_ebd = bge('D:/models/AI-ModelScope/bge-base-en-v1___5')
datas2 = []
# 现在可以对data进行操作，例如打印出来
for i in range(0,len(datas)):
    ens = datas[i]['en']
    zhs = datas[i]['cn']
    env = en_ebd.get_vectors([ens])[0]
    zhv = zh_ebd.get_vectors([zhs])[0]
    data = {'en':ens,'cn':zhs,'en_vector':env,'cn_vector':zhv,'key':'sample_'+str(i),'source':'samples','doc_definition_id':1}
    datas2.append(data)
import pickle
file = open('./datas.pkl','wb+')
pickle.dump(datas2,file)
file.close()
print('---DONE--')