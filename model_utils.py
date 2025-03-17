from pathlib import Path
from typing import Union
import ktrain
from peft import AutoPeftModelForCausalLM, PeftModelForCausalLM
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    AutoModelForSeq2SeqLM
)
import spacy
import tensorflow as tf

#加载训练后的大语言模型
ModelType = Union[PreTrainedModel, PeftModelForCausalLM]
TokenizerType = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]


def _resolve_path(path: Union[str, Path]) -> Path:
    return Path(path).expanduser().resolve()


def load_model_and_tokenizer(model_dir: Union[str, Path]) -> tuple[ModelType, TokenizerType]:
    model_dir = _resolve_path(model_dir)
    if (model_dir / 'adapter_config.json').exists():
        model = AutoPeftModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model.peft_config['default'].base_model_name_or_path
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_dir, trust_remote_code=True, device_map='auto'
        )
        tokenizer_dir = model_dir
    tokenizer = AutoTokenizer.from_pretrained(
        tokenizer_dir, trust_remote_code=True
    )
    return model, tokenizer


#修改为训练后的大语言参数位置
model_dir = r"/home/fength/model/ChatGLM/NEW_TRAIN/2024.6.8NEW_Training/checkpoint-1000"
model, tokenizer = load_model_and_tokenizer(model_dir)


#加载Bert问句分类模型
# 获取所有可用的 GPU 设备
gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:
    try:
        # 限制指定 GPU 设备的显存增长
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)


        # 加载模型
        predictor_load = ktrain.load_predictor('/home/fength/model/bert-ch-marc')
    
    except RuntimeError as e:
        print(e)
else:
    print("No GPU devices found.")


#加载翻译语言模型
#修改为翻译语言模型保存地址
save_directory = "/home/fength/model/Translator"
trans_tokenizer = AutoTokenizer.from_pretrained(save_directory)
trans_model = AutoModelForSeq2SeqLM.from_pretrained(save_directory)

#加载训练后的分词模型用于关键词判断
nlp = spacy.load("/home/fength/fllm/NER/model_best")

