
class translator():
    def __init__(self,path):
        from modelscope.pipelines import pipeline
        from modelscope.utils.constant import Tasks
        self.translator = pipeline(task=Tasks.translation, model=path)

    async def translate(self,text):
        try:
            outputs = self.translator(input=text)
            return outputs['translation']
        except Exception as e:
            return None

if __name__ == '__main__':
    import asyncio
    input_sequence = 'As stated in the Code of Conduct for Clinical Trials (Appendix 1.1), this study includes participants of varying age (as applicable), race, ethnicity, and sex (as applicable). The collection and use of these demographic data will follow all local laws and participant confidentiality guidelines while supporting the study of the disease, its related factors,and the IMP under investigation.'
    trans = translator(r"C:\proj\chat\LLM2402\translator\models\translation_en2zh_base")
    print(asyncio.run(trans.translate(input_sequence)))