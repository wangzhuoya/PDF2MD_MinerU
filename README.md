# PDF2MD_MinerU



<p align="left">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python Version">
  <a href="https://github.com/wangzhuoya/PDF2MD_MinerU/blob/main/LICENSE"><img src="https://img.shields.io/github/license/wangzhuoya/PDF2MD_MinerU" alt="License"></a>
  <a href="https://arxiv.org/"><img src="https://img.shields.io/badge/Data%20Source-arXiv-B31B1B" alt="arXiv"></a>
  <a href="https://mineru.net/"><img src="https://img.shields.io/badge/API%20Provider-MinerU-orange" alt="MinerU"></a>
</p>

## 1. 项目简介
**PDF2MD_MinerU** 是一个命令行工具，旨在帮助用户高效地从 [arXiv](https://arxiv.org/) 网站批量搜索、下载论文，并利用 [MinerU](https://mineru.net/) API 将这些 PDF 文件转换为 Markdown 格式。
本项目中PDF→Markdown格式的转化基于[OpenDataLab](https://github.com/opendatalab)开发的[MinerU](https://github.com/opendatalab/MinerU/tree/master)，需要预先申请[MinerU API Token](https://mineru.net/apiManage/token)。

## 2. 功能特性

- **论文搜索**: 根据关键词在 arXiv 上搜索相关论文，并提取论文 ID。
- **批量下载**: 根据论文 ID 列表，自动、批量地下载对应的 PDF 全文。
- **格式转换**: 调用 MinerU API，将下载好的 PDF 文件批量转换为 Markdown 文件。
- **命令行界面**: 提供简单易用的命令行接口，方便集成到自动化脚本中。
- **可执行程序**: 已打包为单个可执行文件，无需安装 Python 环境即可在 Linux 系统上运行。

## 3. 如何使用

您有两种方式使用本工具：直接运行可执行文件（推荐），或从源代码运行。
### 方式一：直接运行可执行文件 (Linux only)

这是最简单的方式，无需关心 Python 环境和依赖安装。

1.  **下载程序**: 从 [GitHub Releases 页面](https://github.com/wangzhuoya/PDF2MD_MinerU/releases/download/v1.0.0/pdf2md_v1.0.0)下载最新的可执行文件 `pdf2md_v1.0.0`。

2.  **授予权限**: 下载后，需要给该文件添加可执行权限。
    ```bash
    chmod +x pdf2md_v1.0.0
    ```

3.  **运行命令**: 使用 `./pdf2md_v1.0.0` 来执行所有操作。例如，查看帮助信息：
    ```bash
    ./pdf2md_v1.0.0 --help
    ```
### 方式二：从源代码运行 (适合开发者)

如果您希望查看或修改源代码，可以按以下步骤操作。

1.  **安装依赖**: 确保您的环境中已安装 Python 3。然后通过 `requirements.txt` 文件安装所有必需的库。
    ```bash
    pip install -r requirements.txt
    ```

2.  **配置API Token**:
    - 在项目根目录 (`~/PDF2MD_MinerU/`) 下创建一个名为 `.env` 的文件。
    - 在该文件中添加您的 MinerU API Token，格式如下：
      ```
      MINERU_API_TOKEN="your_actual_api_token"
      ```
    > **重要**: 请将 `your_actual_api_token` 替换为您自己的真实 Token。

3.  **运行命令**: 使用 `python main.py` 来执行操作。
## 4. 命令详解

本工具包含三个子命令：`search`, `download`, `convert`。

### 4.1. `search`: 搜索论文

根据给定的关键词搜索 arXiv，并将找到的论文 ID 保存到一个文本文件中。

**用法**:
```bash
# 使用可执行文件
.pdf2md_v1.0.0 search "your query" [OPTIONS]

# 从源码运行
python main.py search "your query" [OPTIONS]
```

**参数**:
- `query` (必需): 您要搜索的关键词，如果包含空格，请用引号括起来。
- `--size` (可选): 希望获取的论文数量。**注意**: arXiv 接受的有效值为 `25`, `50`, `100`, `200`。如果提供无效值，程序将自动使用默认值 `50`。
- `--output` (可选): 保存论文 ID 的文件名。默认为 `arxiv_ids.txt`。

**示例**:
```bash
# 搜索关于 "deep learning" 的50篇论文，并将ID保存到 AIDD_ids.txt
.pdf2md_v1.0.0 search "deep learning" --size 50 --output "dl_ids.txt"
```
### 4.2. `download`: 下载 PDF

读取一个包含 arXiv 论文 ID 的文本文件，并批量下载这些论文的 PDF 版本。

**用法**:
```bash
# 使用可执行文件
.pdf2md_v1.0.0 download [OPTIONS]

# 从源码运行
python main.py download [OPTIONS]
```

**参数**:
- `--input-file` (可选): 包含论文 ID 的输入文件名。默认为 `arxiv_ids.txt`。
- `--output-dir` (可选): 下载的 PDF 文件存放的目录。默认为 `data/pdfs`。

**示例**:
```bash
# 读取 AIDD_ids.txt 文件，并将下载的PDF保存在 data/arxiv_papers 目录下
.pdf2md_v1.0.0 download --input-file "dl_ids.txt" --output-dir "data/arxiv_papers"
```
### 4.3. `convert`: 转换 PDF 为 Markdown

将指定目录下的所有 PDF 文件通过 MinerU API 转换为 Markdown 文件。

**用法**:
```bash
# 使用可执行文件
.pdf2md_v1.0.0 convert [OPTIONS]

# 从源码运行
python main.py convert [OPTIONS]
```

**参数**:
- `--input-dir` (可选): 存放待转换 PDF 文件的目录。默认为 `data/pdfs`。
- `--output-dir` (可选): 保存转换后 Markdown 文件的目录。默认为 `data/markdown`。

**示例**:
```bash
# 转换 data/arxiv_papers 目录下的所有PDF，并输出到 data/markdown_files 目录
.pdf2md_v1.0.0 convert --input-dir "data/arxiv_papers" --output-dir "data/markdown_files"
```

## 5. MinerU 接口说明​

MinerU API用户须先申请 Token，且有以下限制：
- 单个文件大小不能超过 **200MB**,文件页数不超出 **600 页**
- 每个账号每天享有 **2000 页**最高优先级解析额度，超过 2000 页的部分优先级降低
- 因网络限制，github、aws 等国外 URL 会请求超时
  
详情请见[MinerU API文档](https://mineru.net/apiManage/docs)。
