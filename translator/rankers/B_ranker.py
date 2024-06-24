from FlagEmbedding import FlagReranker
import os


class reranker:
    def __init__(self, model_path, gpu_id_str=None):
        # if (not gpu_id_str is None and not len(gpu_id_str) == 0):
        #     os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id_str
        self.model = FlagReranker(model_path, use_fp16=False)

    def get_rank_scores(self, query, texts):
        pairs = []
        for text in texts:
            pairs.append([query, text])
        scores = self.model.compute_score(pairs)
        if not isinstance(scores, list):
            scores = [scores]
        return scores

    def get_rerank_result(self,query,texts,keys=None,min_score=-999,top_k=5):
        scores = self.get_rank_scores(query,texts)
        scores2 = []
        if not isinstance(scores,list):
            scores = [scores]
        for i in range(len(texts)):
            obj = {"score":float(scores[i]),"text":texts[i],"key":None}
            if(not keys is None):
                obj["key"] = keys[i]
            scores2.append(obj)
        scores2.sort(key = lambda x:x["score"],reverse=True)
        results = []
        for i in range(len(scores2)):
            obj = scores2[i]
            if(obj["score"] < min_score):
                break
            results.append(obj)
            if(len(results)>=top_k):
                break
        return results

if (__name__ == '__main__'):
    model_id = r"D:\models\quietnight\bge-reranker-large"
    rr = reranker(model_id)
    query = '胸痛'
    texts = ['轻微胸痛', '小狗', '咳嗽', '阿莫西林', '疼痛']
    print(rr.get_rerank_result(query, texts,keys=texts,top_k=3,min_score=0))
    print('---DONE---')
