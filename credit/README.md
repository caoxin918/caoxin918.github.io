# CRediT Statement Generator

科研论文贡献者角色与贡献声明自动生成工具。

基于 [CRediT Taxonomy](https://credit.niso.org/)（Contributor Roles Taxonomy）标准，帮助研究者快速生成规范的作者贡献声明文本，可直接用于论文投稿。

---

## 功能特性

- ✅ **14 项 CRediT 标准角色**全覆盖
- ✅ **动态作者管理**：添加/删除作者，点击选中后为其分配角色
- ✅ **三种输出格式**：单行、多行、段落（Author contributions 格式）
- ✅ **可选论文信息**：支持填写论文标题和期刊名称（可选）
- ✅ **一键复制 / 导出 TXT**
- ✅ **角色说明侧栏**：随时查阅 14 项角色的中文释义

## 输出格式示例

**单行格式：**
```
caoxin: Conceptualization, Investigation. liuzichao: Project administration, Software.
```

**多行格式：**
```
caoxin: Conceptualization, Investigation.
liuzichao: Project administration, Software.
```

**段落格式：**
```
Author contributions: caoxin (Conceptualization, Investigation); liuzichao (Project administration, Software).
```

---

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动应用

```bash
python app.py
```

访问 `http://localhost:5000` 即可使用。

---

## 项目结构

```
CRediT_Statement_Generator/
├── app.py                    # Flask 主应用
├── requirements.txt          # Python 依赖
├── README.md                # 项目说明（本文件）
└── templates/
    └── index.html           # 主页面模板
```

---

## CRediT 14 项角色说明

| 英文角色名 | 中文说明 |
|---|---|
| Conceptualization | 提出核心概念或构思 |
| Data curation | 数据管理与整理 |
| Formal analysis | 正式数据分析 |
| Funding acquisition | 获取研究资金 |
| Investigation | 实验或调查研究 |
| Methodology | 方法论设计 |
| Project administration | 项目管理协调 |
| Resources | 提供研究资源 |
| Software | 软件开发/编程 |
| Supervision | 研究监督指导 |
| Validation | 研究验证与复现 |
| Visualization | 数据可视化 |
| Writing – original draft | 撰写初稿 |
| Writing – review & editing | 审阅与修改 |

---

## 使用流程

1. （可选）填写论文标题和期刊名称
2. 点击「＋ 添加新作者」添加作者，输入作者姓名
3. 点击左侧作者条目选中，在右侧勾选该作者的贡献角色（可多选）
4. 重复步骤 2-3 添加所有作者
5. 选择输出格式（单行/多行/段落）
6. 点击「✨ 生成声明」查看结果
7. 点击「📋 复制到剪贴板」或「💾 导出 TXT」获取结果

---

## 技术栈

- **后端**：Flask (Python)
- **前端**：原生 HTML + CSS + JavaScript（无框架依赖）
- **UI 风格**：简洁卡片式布局，左右分栏交互

---

## 作者

caoxin

## License

MIT
