import jieba
import jieba.posseg as pseg
from model_utils import predictor_load, trans_model, trans_tokenizer, nlp

jieba.add_word("防火间距", freq=None, tag='n')
jieba.add_word("多层", freq=None, tag='n')
jieba.add_word("高层", freq=None, tag='n')
jieba.add_word("防火分区", freq=None, tag='n')


stop_words = [
    '后来', '比方', '总是', '它', '从', '一边', '很多', '即便', '这些', '部分', '一段', '那个', '建筑',
    '哈', '因而', '特别', '但是', '还是', '这里', '那儿', '至于', '什么', '该', '越过', '如', '假如',
    '她', '那', '除了', '而且', '之后', '纵使', '虽然', '另外', '吧', '确实', '和', '呀', '真的', '只',
    '往', '应该', '继续', '于是', '例如', '大部分', '起来', '关于', '由于', '对于', '可能', '一部分', '比如',
    '这', '然而', '你', '只是', '啊', '比起', '到', '旁边', '接近', '地', '必然', '虽说', '通过', '一下', '这边',
    '就是', '应当', '反而', '这样', '比较', '之前', '一般', '有', '哪边', '就', '就算', '而是', '里', '但',
    '他', '只要', '有些', '如此', '周围', '尽管', '上', '一起', '别的', '此外', '并且', '比如说', '还有', '着',
    '来说', '随着', '哪个', '一直', '来讲', '附近', '却', '同时', '那么', '因此', '始终', '说到', '除此', '朝',
    '较为', '或', '除外', '实际上', '要求', '非常', '以及', '能够', '不过', '一些', '极其', '很', '仅仅', '外',
    '一个', '那样', '而', '之间', '有时候', '再加', '当然', '多数', '距离', '所以', '要', '有时', '一份的', '每个',
    '的确', '如果', '实在', '呢', '还', '绝大部分', '在', '了', '故', '这个', '以至于', '我', '必须', '与', '过',
    '一次', '然后', '接着', '是', '的话', '少数', '一点', '哪里', '一定', '也', '就是说', '那边', '如何', '得', '及',
    '吗', '即使', '却是', '的', '可以', '下', '沿着', '一条', '这儿', '哪些', '因为', '譬如', '那里', '那些', '这么',
    '一种', '设置', '向','建筑','有什么'
]

stop_words = list(set(stop_words))

jieba.add_word("防火间距", freq=None, tag='n')
jieba.add_word("多层", freq=None, tag='n')
jieba.add_word("高层", freq=None, tag='n')
jieba.add_word("防火分区", freq=None, tag='n')


# Step 1: 提取问题中的关键字
def extract_keywords(content):
    # 使用jieba进行中文分词
    words = pseg.cut(content)
    # 过滤掉停用词等无关词语
    keyword = [word for word in words if word.word not in stop_words]
    input_keywords = [word.word for word in keyword if word.flag.startswith('n') or word.flag.startswith('l')]
    return input_keywords


#判断图片生成还是文字生成
def function_decision(question):
  function = predictor_load.predict(question)
  return function

#对于输入文字翻译为英语用于图像生成: SDXL
def translate(sentence):
  translated = trans_model.generate(**trans_tokenizer(sentence, return_tensors="pt", padding=True))
  res = [trans_tokenizer.decode(t, skip_special_tokens=True) for t in translated]
  return res

def question_check(question):
  doc = nlp(question)
  keywords = [token.text for token in doc.ents if token.label_ == "KEYWORD"]
  return keywords