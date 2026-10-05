# BioSyn FASTA Batch Analyzer

> **批量 FASTA 序列分析工具** — 本地离线、隐私安全的 DNA / RNA / 蛋白质序列批量计算与质控。
>
> A local-first batch FASTA sequence analyzer for DNA, RNA, and protein — compute GC%, molecular weight, reverse complement, and quality control in one run.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Offline](https://img.shields.io/badge/Privacy-Offline%20First-orange.svg)](#privacy)

## 核心功能

| 功能 | 说明 |
|------|------|
| **批量 FASTA 解析** | 支持 `.fasta` / `.fa` / `.fna` / `.faa` / `.txt`，单文件 / 多文件 / 文件夹递归扫描 |
| **自动序列识别** | 根据字符集自动判断 DNA / RNA / Protein，支持手动覆盖 |
| **DNA 分析** | 长度、碱基组成、GC%、AT%、分子量估算、反向互补序列 |
| **RNA 分析** | A/U/G/C 计数、GC%、分子量估算 |
| **蛋白质分析** | 氨基酸组成、分子量估算、等电点 (pI) 估算 |
| **质量控制 (QC)** | PASS / REVIEW / INVALID 三级判定，空序列、非法字符、高歧义、重复 ID 自动标记 |
| **多格式导出** | CSV、XLSX（多 Sheet）、HTML 交互式报告 |
| **完全离线** | 所有计算本地完成，不上传任何序列数据 |

## 解决的痛点

网页端序列分析工具一次只能处理一条序列。当你手上有 **几百甚至上千条 FASTA 序列** 需要批量计算 GC 含量、分子量并做质控时，逐条复制粘贴既低效又容易出错。BioSyn FASTA Batch Analyzer 把整个流程搬到本地：拖入文件夹 → 一键分析 → 导出汇总报告。

> 网页版单条快速计算请访问 [BioSyn 在线序列分析](https://biosyn-inc.com/tools/fasta-sequence-analyzer) — 本工具是其桌面端批量增强版。

## 技术栈

- **Python 3.12+**
- **pandas** — 数据处理
- **openpyxl** — XLSX 导出
- **matplotlib** — 图表生成（可选）
- 标准库 `csv`, `dataclasses`, `argparse`

## 依赖与安装

### 环境要求

- **Python 3.10+**（推荐 3.12 或更高）

### 依赖包

| 包 | 用途 | 是否必需 |
|------|------|----------|
| `openpyxl` | XLSX 多 Sheet 导出 | 可选（无此包则仅输出 CSV + HTML） |
| `matplotlib` | GC% / 长度分布图（计划中） | 可选 |
| `biopython` | 更精确的 pI 计算（计划中） | 可选 |

> 核心分析引擎（FASTA 解析、GC%、分子量、反向互补、QC）**仅依赖 Python 标准库**，无需任何第三方包即可运行。

### 安装指令

```bash
# 1. 克隆仓库
git clone https://github.com/your-org/biosyn-fasta-batch-analyzer.git
cd biosyn-fasta-batch-analyzer

# 2. 安装依赖（最小安装：仅 openpyxl）
pip install -r requirements.txt

# 或者最小化运行（仅标准库，无 XLSX 导出）
# python -m src.main analyze ./examples/sample_sequences.fasta --output ./results
```

### 运行（CLI）

```bash
# 分析单个 FASTA 文件
python -m src.main analyze ./examples/sample_sequences.fasta --output ./results

# 分析整个文件夹（递归）
python -m src.main analyze ./sequences_folder --output ./results

# 强制指定序列类型为 DNA
python -m src.main analyze ./my_seqs.fasta --type DNA --output ./results
```

### 输出示例

运行后在 `./results/` 目录生成：

```
results/
├── fasta_analysis.csv          # 每条序列一行结果
├── fasta_analysis.xlsx         # 多 Sheet 工作簿（Summary / Results / Methods ...）
├── fasta_qc_report.html        # 可直接浏览器打开的 QC 报告
└── invalid_sequences.csv        # 仅含 REVIEW / INVALID 序列
```

## 输入格式

FASTA 标准格式：

```text
>sequence_id 可选描述
ATGCGTACGTTAGCGCTAGCTAGC...
```

支持多记录（multi-FASTA）文件，自动识别换行。

## 计算方法说明

| 指标 | 方法 |
|------|------|
| GC% | `(G + C) / (A + T + G + C) × 100`，分母为无歧义碱基 |
| 分子量 | 单链聚合物近似值（非实验测量值） |
| pI | Bjellqvist 方法，二分法求解 |
| 反向互补 | 标准 Watson-Crick 互补 + 5'→3' 反转 |

> 所有分子量和 pI 均为 **估算值 (estimated)**，不作为实验测量值使用。

## 目录结构

```
biosyn-fasta-batch-analyzer/
├── src/
│   ├── __init__.py          # 包元数据
│   ├── main.py              # CLI 入口与流水线编排
│   ├── parser.py            # FASTA 文件解析
│   ├── analyzer.py          # 核心序列分析引擎
│   ├── qc.py                # 质量控制检查
│   └── exporter.py          # CSV / XLSX / HTML 导出
├── examples/
│   └── sample_sequences.fasta
├── config/
│   └── default_rules.yaml   # 默认 QC 规则配置
├── tests/
│   └── test_analyzer.py
├── requirements.txt
├── README.md                # 本文件（中文）
├── README_EN.md              # English README
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
└── sitemap.xml
```

## 隐私与安全

- ✅ 所有计算在本地完成
- ✅ 不上传序列到任何服务器
- ✅ 不调用云端 API
- ✅ 原始数据不被修改或上传

## 关键关键词

`FASTA batch analysis`, `DNA sequence analyzer`, `RNA sequence analyzer`, `protein sequence analyzer`, `batch sequence QC`, `GC content calculator`, `molecular weight estimation`, `reverse complement tool`

## 关于

由 [BioSyn Inc.](https://biosyn-inc.com/) 开发维护。网页版单条序列快速计算、分子生物学知识库与更多工具请访问：

- [BioSyn 在线 DNA / RNA / Protein 序列分析](https://biosyn-inc.com/tools/fasta-sequence-analyzer)
- [BioSyn 工具集首页](https://biosyn-inc.com/)

## License

[MIT](LICENSE) — 自由使用、修改、分发。
