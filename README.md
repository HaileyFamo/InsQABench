<div align="center">

ZH | EN

<h1>InsQABench</h1>
  
[![Generic badge](https://img.shields.io/badge/🤗-Huggingface%20Repo-green.svg)](https://huggingface.co/FrankRin/InsLLM)
[![license](https://img.shields.io/github/license/modelscope/modelscope.svg)](./LICENSE)

Demo | 技术报告

</div>

InsQABench 是中国保险领域首个大规模的专用问答数据集和评估基准，由华中科技大学 VLR Lab（视觉与深度学习研究组）开发并开源。

我们将在该项目中开源如下资源：
* [Insure-QA 数据集](https://huggingface.co/datasets/FrankRin/Insur-QA)
* [InsLLM 模型权重](https://huggingface.co/FrankRin/InsLLM)
* [中文保险条款数据集](#insur-qa-数据集)
* [Insure-QA Benchmark](./eval/)


## 新闻

**[2024/10/07]** InsQABench v1.0 已正式发布，开源 [InsLLM 模型](https://huggingface.co/FrankRin/InsLLM) 、 [Insure-QA 数据集](https://huggingface.co/datasets/FrankRin/Insur-QA) 和[中文保险条款数据集](#insur-qa-数据集).

## 目录

- [新闻](#新闻)
- [目录](#目录)
- [概述](#概述)
  - [模型在 Benchmark上的测试结果](#模型在-benchmark上的测试结果)
  - [模型效果演示](#模型效果演示)
  - [Insur-QA 数据集](#insur-qa-数据集)
  - [中文保险条款数据集](#中文保险条款数据集)
- [模型评测](#模型评测)
  - [评测代码以及数据](#评测代码以及数据)
  - [客观评测](#客观评测)
  - [主观评测](#主观评测)
- [推理和部署](#推理和部署)
  - [Python](#python)
  - [项目源码](#项目源码)
- [引用](#引用)
- [协议](#协议)
- [Star History](#star-history)

## 概述


<p></p>


InsLLM 是一个具备保险知识问答、数据库查询和合同解析能力的智能保险系统，专为不同用户群体和应用场景设计，具备以下主要特点：

* **保险文本处理能力：** 针对保险领域复杂的专业术语和文档格式，系统能够理解并生成相关内容，包括信息提取、文档摘要等。我们基于公开的保险数据和真实世界的保险文档，构建了微调数据集。
* **保险推理能力：** 系统通过 SQL-ReAct 方法，能够针对用户查询进行 SQL 语句的优化与纠错，有效处理保险数据库中的复杂查询任务。
* **保险知识遵循能力：** 系统配备了 Insur-Know 模块，支持基于检索增强的合同解析与事实提取，确保能够准确处理保险合同中的复杂问题。

此外，我们的研究还包括以下贡献：

* **高质量的保险问答训练数据集和有效的训练范式**
* **完整的保险模型评测框架和评测数据集**


### 模型在 Benchmark上的测试结果

<!-- 论文里的 Benchmark 图表 -->

### 模型效果演示

<!-- Demo GIF -->
![Demo GIF](./clause.gif)

### InsQABench 数据集

基本保险知识部分，我们对 InsuranceQA 数据集进行了翻译，得到 InsuranceQA_zh 数据集。

保险合同数据部分，我们在互联网上下载了多家保险公司 PDF 格式的保险条款（见[中文保险条款数据集](#中文保险条款数据集)），并使用 Adobe PDF Extract API 解析。基于对解析结果进行段落文本重组后的数据使用 Gemini 生成 QA 对，组成 <Q,A,E> 三元组。

具体的数据集的组成如下：

<table border="1">
  <tr>
    <th>任务</th>
    <th>数据集</th>
    <th>来源</th>
    <th>规模</th>
  </tr>
  <tr>
    <td rowspan="2">基本保险知识问答</td>
    <td>训练集</td>
    <td>BX_GPT3.5</td>
    <td>10k</td>
  </tr>
  <tr>
    <td>测试集</td>
    <td>Insurance_QA_zh</td>
    <td>3k</td>
  </tr>
  <tr>
    <td rowspan="2">保险合同问答</td>
    <td>训练集</td>
    <td>保险合同</td>
    <td>40k</td>
  </tr>
  <tr>
    <td>测试集</td>
    <td>保险合同</td>
    <td>100</td>
  </tr>
  <tr>
    <td rowspan="2">保险数据库问答</td>
    <td>训练集</td>
    <td>保险合同</td>
    <td>44k</td>
  </tr>
  <tr>
    <td>测试集</td>
    <td>保险合同</td>
    <td>546</td>
  </tr>
</table>




### 中文保险条款数据集

下载方式：[百度网盘](https://pan.baidu.com/s/10UCb0EWC3Mz9iPoLwE-oaA?pwd=1037)（提取码：1037）


## 模型评测

受保险行业特点的启发，我们构建了一个全面的评估体系从客观和主观两个维度对保险领域的大语言模型进行性能评估，以衡量模型在处理中文保险数据时的有效性。客观评估主要依赖于自动化的度量标准，如 BLEU-4、 ROUGE-l 分数，而主观评估则通过模拟真实用户查询的场景，由裁判模型对模型生成的答案进行打分。

### 评测代码以及数据

见[模型评估](./eval/)

### 客观评测

使用 InsuranceQA_zh 数据集（由 InsuranceQA 数据集翻译得到）进行客观评测，我们使用 BLEU-4、ROUGE-l 分数等指标对模型进行评估。

### 主观评测

我们手动构建了包含 100 个问题的高质量测试集，力求使问题涵盖更广的范围。

使用 GPT-4 作为裁判模型。


## 推理和部署

InsLLM 是基于 [Qwen1.5-14B-Chat](https://huggingface.co/Qwen/Qwen1.5-14B-Chat) 进行微调训练得到的。您可以直接从 [Hugging Face](https://huggingface.co/FrankRin/InsLLM/tree/main) 上下载我们的模型权重，或者根据下面的代码样例自动获取。推理前请安装依赖：

```
pip install -r requirements.txt
```

### Python

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig

model_path = "FrankRin/InsLLM"
model = AutoModelForCausalLM.from_pretrained(
    model_path, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True
)
model.generation_config = GenerationConfig.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(
    model_path, use_fast=False, trust_remote_code=True,
)

messages = [
    {"role": "user", "content": "生产销售假冒伪劣商品罪如何判刑？"},
]
response = model.chat(tokenizer, messages)
```

### 项目源码

本项目构建过程中使用到的工具代码见 [src](./src/) 目录。

| 文件 | 描述 |
| --- | --- |
| `config.py` | Gemini 的配置数据 |
| `extract.py` | 处理 PDF 解析结果，将文本按照段落重新组织。 |
| `gemini.py` | 基于保险条款数据生成问题和答案，生成 <Q,A,E> 三元组并。 |
| `prompt.py` | `gemini.py`中用于生成问题和答案的提示词。 |
| `utils.py` | 工具类，包含文件读写、数据集划分等函数。 |



## 引用

如果我们的项目对您的研究和工作有帮助，请如下引用我们的项目：

```
@misc{
    
}
```

## 协议

InsQABench 可在 Apache 许可证下使用。请查看 [LICENSE](./LICENSE) 文件获取更多信息。

## Star History

<picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HaileyFamo/InsQABench&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HaileyFamo/InsQABench&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HaileyFamo/InsQABench&type=Date" />
</picture>
