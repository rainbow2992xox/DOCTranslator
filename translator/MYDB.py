import faiss
import numpy as np


class FDB:

    def __init__(self, vector_len, use_gpu=False, gpu_id=0):
        db = faiss.IndexFlatL2(vector_len)
        if (use_gpu):
            res = faiss.StandardGpuResources()
            db = faiss.index_cpu_to_gpu(res, gpu_id, db)
        self.db = db
        self.keys = []
        self.vectors = []

    def add(self, vectors, keys):
        for i in range(0, len(keys)):
            self.keys.append(keys[i])
            self.vectors.append(vectors[i])
        self.db.add(np.array(vectors))

    # def add_texts(self):

    def search(self, vectors, top_k=3):
        D, I = self.db.search(vectors, top_k)
        result = []
        for i in range(0, len(D)):
            res = []
            for j in range(0, len(D[i])):
                if(I[i][j]<0 or I[i][j]>=len(self.keys)):
                    continue
                score = 1 - D[i][j]
                # if(score<0):
                #     score = 0
                res.append({"key": self.keys[I[i][j]], "score": score})
            result.append(res)
        return result

    def reset(self):
        self.db.reset()
        del self.keys
        del self.vectors
        self.keys = []
        self.vectors = []

class MyDB:
    def __init__(self, embedding_model, use_gpu=False, gpu_id=0):
        self.embedding_model = embedding_model
        self.vector_length = len(self.embedding_model.get_vectors(['hello'])[0])
        # print('Vector Length:', self.vector_length)
        if (use_gpu):
            self.FDB = FDB(self.vector_length, use_gpu=True, gpu_id=gpu_id)
        else:
            self.FDB = FDB(self.vector_length)

    def reset(self):
        self.FDB.reset()
    def get_vectors(self, texts, vector_norm=False):
        if (not vector_norm):
            return self.embedding_model.get_vectors(texts)
        else:
            return self.embedding_model.get_vectors_norm(texts)

    def add_texts(self, texts, vector_norm=False, vectors=None):
        if (vectors is None):
            vectors = self.get_vectors(texts, vector_norm=vector_norm)
        self.FDB.add(vectors, texts)
        return vectors

    def search(self, texts, top_k=3, min_score=0.5, vector_norm=False):
        vectors = self.get_vectors(texts, vector_norm=vector_norm)
        result1 = self.FDB.search(np.array(vectors), top_k=top_k)
        results = []
        for i in range(0, len(result1)):
            arr = []
            for obj in result1[i]:
                if (obj['score'] >= min_score):
                    arr.append(obj)
            results.append(arr)
        return results


if (__name__ == '__main__'):
    # model_id = r"C:\tests\对话导诊240223\nlp_corom_sentence-embedding_chinese-base-medical"
    model_id = 'D:/models/AI-ModelScope/bge-base-zh-v1___5'
    from ebs.bge_eb import embeddings
    ebd = embeddings(model_id)
    db = MyDB(ebd, use_gpu=False)
    vector_norm = False
    db.add_texts(['胸闷', '发热', '咳嗽'], vector_norm=vector_norm)
    print(db.search(["有一点胸闷", "体温39摄氏度", "胸口发热"], vector_norm=vector_norm))
    db.reset()
    print(db.search(["有一点胸闷", "体温39摄氏度", "胸口发热"], vector_norm=vector_norm))
    print('---DONE---')
