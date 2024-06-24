from FlagEmbedding import FlagModel
import os
import numpy as np


class embeddings:
    def __init__(self, embedding_model,gpu_id_str=None):
        # if(not gpu_id_str is None and not len(gpu_id_str)==0):
        #     os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id_str
        self.model = FlagModel(embedding_model,
              query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
              use_fp16=False)

    def get_vectors(self, texts):
        emds = self.model.encode(texts)
        return emds

    def get_vectors_norm(self, texts):
        emds = self.get_vectors(texts)
        for i in range(0, len(emds)):
            emd = emds[i]
            emd = emd / np.linalg.norm(emd)
            emds[i] = emd
        return emds

if(__name__=='__main__'):
    model_id = "../models/ebd-en"
    ebd = embeddings(model_id)
    print(ebd.get_vectors_norm(['你好']))
    print('---DONE---')