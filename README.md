# 词义消歧数据集标注实用工具
基于 Gradio 编写的简单标注工具，需要读取指定格式的语料文件。
## 安装
首先需要安装对应操作系统的 Python 环境
- Windows：点击“1_安装程序”即可安装对应依赖。
- 其他：确定 Python 环境内存在 Gradio 和 Pandas 包即可
## 数据集格式
数据集为 .csv 格式，表头分别为“word,meaning,sentence”，对应目标词、词义和例句。标注后的数据集会增加“true_meaning”列，表示标注后的词义。
待标注数据放在 raw_data 文件夹下，标注结果生成于 annotated_data 文件夹下。