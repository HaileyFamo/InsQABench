# InsQABench

- 评测数据集
  - [客观评测集 InsuranceQA_zh](datasets/InsuranceQA_zh.json)
  - [主观评测集](./datasets/subjective/)

- 评测代码
  - 主观评测：运行 `subjective/src/eval_seq2seq.py` 进行主观评测，其中的模型答案路径需要自行修改。当运行评测代码时，评分结果将会被保存在 `result/` 文件夹下（`jsonl`格式）。
  - 您可以在[此处](../README.md)查看关于我们使用的评测方法的更多详情。


- 评测结果:
  - `objective`文件夹中保存了我们的技术报告中的客观评测结果。包括[基座模型（Qwen-1.5-Chat）](./objective/base_model)和[InsLLM](./InsLLM/base_model)。