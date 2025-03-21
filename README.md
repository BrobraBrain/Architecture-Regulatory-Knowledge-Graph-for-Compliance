# FUGPT 的文本回答功能


这是一个基于多个 Python 模块的项目，旨在使用大语言模型和自然语言处理技术回答建筑用户的问题，并提供相关的图片和内容。

## 目录

- [安装依赖](#安装依赖)
- [模型训练](#模型训练)
- [知识图谱](#知识图谱)
- [文件结构](#文件结构)
- [使用说明](#使用说明)
- [功能介绍](#功能介绍)


## 安装依赖

在使用此项目之前，请确保安装必要的依赖库。你可以通过以下步骤安装依赖：


1. 创建并激活虚拟环境（可选）：
    ```bash
    python -m venv venv
    source venv/bin/activate  # 对于 Windows，使用 `venv\Scripts\activate`
    ```

2. 安装依赖库：
    ```bash
    pip install -r requirements.txt
    ```

## 模型训练
本项目基于三种不同的模型算法进行微调及训练，分别用于问题分类判别、命名实体提取和问题回答：
1. Bert Models用于问题分类判别
2. SpaCy命名实体对象算法用于提取关键词
3. ChatGLM3 大语言模型算法用于问题回答

### 基于Bert Models的微调
使用 Bert Models 进行问题分类判别模型训练，以下是具体步骤。

#### 数据准备
将标注好的问题类别数据放入 Bert_Classification/data/questions.csv 文件中。

#### 训练步骤
1. 打开 Bert语句分类训练模型.ipynb。
2. 按顺序运行所有单元格进行数据加载、预处理和模型训练。
3. 模型训练完成后，会保存到指定目录。

#### 模型调用

    ```python
    import ktrain
    predictor_load = ktrain.load_predictor('模型保存地址')  # 输入示例文本

    data = ['描述建筑设计的方法',
        "论述古代罗马建筑中的“公共浴场”设计",
        "描述一座现代办公大楼的工作氛围",
        "设计一个传统日式庭院的别墅建筑",
        "设计一个有顶的亭子",
        "为我描述民用建筑高度有何相关规范",
        ""]

    predictor_load.predict(data)
    
    ```

### 基于SpaCy命名实体对象算法的训练
使用 `spaCy` 进行 NER 分词模型进行建筑类关键词训练，以下是具体步骤。

#### 建筑文本-json训练格式转换官网

使用 [NER Annotator](https://tecoholic.github.io/ner-annotator/) 将建筑相关的文本转换为 JSON 格式。

1. 访问 [NER Annotator](https://tecoholic.github.io/ner-annotator/)。
2. 根据页面提示进行文本标注，并导出为 JSON 格式。

#### 创建配置文件

使用 `spaCy` 提供的配置文件生成工具来创建训练所需的配置文件。

1. 进入 [spaCy 配置文件创建页面](https://spacy.io/usage/training#config)。
2. 在页面的 "Quickstart" 部分，根据你的需求选择配置（确保选中 NER，并根据要求选择语言）。
3. 下载生成的配置文件 `base_config.cfg`。

![调试自己的设置]

4. 在命令行中运行以下命令生成完整的配置文件：

    ```bash
    python -m spacy init fill-config base_config.cfg config.cfg
    ```

![在网站中下载]

#### 训练模型

使用生成的配置文件进行模型训练。

1. 确保你的训练数据已转换为 spaCy 支持的格式（`.spacy`）。
2. 在命令行中运行以下命令进行训练：

    ```bash
    python -m spacy train config.cfg --output ./output --paths.train ./train.spacy --paths.dev ./train.spacy
    ```

![模型训练]

训练完成后，模型将保存在 `./output` 目录下。

#### 调用模型

训练完成后，可以使用训练好的模型进行建筑类的关键词的预测和可视化。

1. 加载训练好的模型：

    ```python
    import spacy
    nlp1 = spacy.load(r"./output/model-best")  # 加载最优模型
    ```

2. 输入示例文本进行预测：

    ```python
    doc = nlp1("建筑相关问题")  # 输入示例文本
    ```

3. 在 Jupyter Notebook 中进行可视化：

    ```python
    spacy.displacy.render(doc, style="ent", jupyter=True)  # 在 Jupyter Notebook 中显示
    ```
### 基于ChatGLM3大语言模型算法的微调
使用 Bert Models 进行问题分类判别模型训练，以下是具体步骤。

#### 数据准备
1. 将问题回答的数据放入 `.\Fine_Tuning\training_file\test_data` 文件中。
2. 运行 `.\Fine_Tuning\training_file\test_train.py`
3. 训练集文件保存在 `.\Fine_Tuning\training_file\test_data\AdvertiseGen_fix` 中

#### 模型微调
1. 打开 ChatGLM3微调训练模型.ipynb
2. 按顺序运行所有单元格进行数据加载、预处理和模型训练
3. 模型训练完成后，会保存到指定目录


## 知识图谱
本项目基于建筑规范、建筑学术论文、建筑介绍等信息，构建了一个建筑领域的知识图谱。知识图谱利用关键词（KEYWORD）建立联系，框架联系了建筑规范、文献...中的目录、章节、内容以及图表和图片。

### 项目结构

```
knowledge_graph_project/
│
├── Bert_Classfication/ #Bert算法-判断句子类型
│ ├── csv/ # Bert算法训练集及验证集
│ └── Bert语句分类训练模型.ipynb/ # colab训练步骤
│
├── Text/
│ ├── book_directory/ # 建筑各类规范的目录
│ ├── book_list/ # 建筑各类规范的名称
│ ├── content/ # 建筑各类规范每个章节的名称
│ ├── word/ # 建筑各类规范的Word文档（包含图片及表格）
│ └── Text_Split.py # 将建筑各类规范内容按章节划分
│
├── NER/ #命名实体对象分词的训练模型算法
│ ├── Training_Data/ # 训练集及验证集
│ ├── docbin/ # 转化的训练集及验证集
│ ├── model-best/ # 采用的分词模型算法
│ ├── NER Training Data Annotation.py/ # colab训练步骤
│ └── README_TRAINING.md/ # 训练步骤
│
├── Fine_Tuning/ #ChatGLM3的训练模型算法
│ ├── training_file/ # 大语言模型的训练集及验证集
│ └── ChatGLM3微调.ipynb/ # colab训练步骤
│
├── XML_KG_generate/
│ ├── Image_KG_generator.py # 基于Text内容生成图表及图片知识图谱
│ └── Text_KG_generator.py # 基于Text内容生成文本类知识图谱
└── knowledge_graph.xml
└── picture_knowledge_graph.xml
```

### 使用说明

1. **文本处理**：
    运行 `Text_Split.py` 脚本，将建筑规范内容按照章节划分到单独的文本文件中：
    ```bash
    python Text/Text_Split.py
    ```

2. **生成知识图谱**：
    - 生成文本类知识图谱：
      ```bash
      python XML_KG_generate/Text_KG_generator.py
      ```

    - 生成图表及图片知识图谱：
      ```bash
      python XML_KG_generate/Image_KG_generator.py
      ```

### 文件说明

#### Text 文件夹

- `book_directory/`：存放建筑各类规范的目录信息。
- `book_list/`：存放建筑各类规范的名称列表。
- `content/`：存放建筑各类规范每个章节的名称。
- `word/`：存放建筑各类规范的 Word 文档，包含图片及表格。
- `Text_Split.py`：将建筑各类规范的内容按照每个章节划分成单独的文本文件。

#### XML_KG_generate 文件夹

- `Image_KG_generator.py`：基于 `Text` 文件夹中的内容生成图表及图片的知识图谱。
- `Text_KG_generator.py`：基于 `Text` 文件夹中的内容生成文本类的知识图谱。


## 文件结构

项目的主要代码文件和目录如下：

```
local_path/
├── requirements.txt # 所需的库
├── install_libraries.py # 安装库的脚本
├── main.py # 主程序
├── model_utils.py # 模型加载和处理
├── keyword_extraction.py # 关键词提取
├── content_extraction.py # 内容提取
├── similarity.py # 相似度计算
├── image_utils.py # 图片处理
└── README.md # 项目说明文件
```

## 使用说明

1. 运行主程序：
    ```bash
    python main.py
    ```

2. 按照提示输入问题，程序将基于ChatGLM大语言模型及各种大语言模型的API调用，辅助于建筑专业知识图谱提供答案，并展示相关的图片（如果有）。

## 功能介绍

### 模型加载和处理

文件：`model_utils.py`

加载预训练的 `THUDM/chatglm3-6b` 模型、分词模型、判别模型，并进行模型评估。

### 关键词提取

文件：`keyword_extraction.py`

进行中文分词，并提取问题中的关键词。

### 内容提取

文件：`content_extraction.py`

从 XML 文件中提取相关章节内容，并计算关键词相似度。

### 相似度计算

文件：`similarity.py`

使用 `sentence_transformers` 库计算输入问题和章节内容之间的相似度。

### 图片处理

文件：`image_utils.py`

从 XML 文件中提取并解码 Base64 编码的图片数据，并显示相关图片。
