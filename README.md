# 曹欣 · 个人学术主页

西北大学信息科学与技术学院副教授、硕士生导师。

## GitHub Pages 部署说明

### 1. 创建 GitHub 仓库

仓库名必须为：`caoxin918.github.io`

### 2. 上传文件

将本目录下所有文件上传至仓库根目录：

```
ScholarHome/
├── index.html              # 主页
├── publications.md         # 论文数据源
├── gen_pubs.py             # 论文HTML生成脚本
├── students.md             # 学生数据源
├── gen_students.py         # 学生HTML生成脚本
├── .gitignore
├── README.md
├── images/
│   └── pic.png             # 个人照片
└── files/                  # 论文PDF文件（需自行补充）
    ├── PDF_REFERENCE_LIST.txt  # 已引用的PDF清单
    ├── 张格格2023cmpb.pdf
    ├── 王昊霖2022.pdf
    └── 王浩宇2024RS.pdf
```

### 3. 补充 PDF 文件

主页中引用了约 **84 篇**论文的 PDF 原文链接，路径为 `https://caoxin918.github.io/files/文件名.pdf`。

当前已有 3 篇 PDF 在 `files/` 目录中，其余需要您自行收集并放入该目录。具体清单见 `files/PDF_REFERENCE_LIST.txt`。

### 4. 启用 GitHub Pages

1. 前往仓库 Settings → Pages
2. Source 选择 "Deploy from a branch"
3. Branch 选择 "main"，目录选择 "/ (root)"
4. 点击 Save

部署成功后访问 `https://caoxin918.github.io/` 即可看到页面。

---

## 如何添加新内容

### 添加新论文

1. 编辑 `publications.md`，在对应分类区（国际期刊 / 国际/国内会议 / 国内期刊 / 受理/授权发明专利 / 软件著作权）追加新条目

   **期刊/会议论文格式：**
   ```
   | 作者. "[论文标题](https://caoxin918.github.io/files/文件名.pdf)", **期刊名**. (年份). |
   ```
   如有代码链接，末尾追加 `CODE click [HERE](https://github.com/xxx)`

   **发明专利格式：**
   ```
   | 发明人。专利名称。申请/授权专利号：CNxxxxx |
   ```

   **软件著作权格式：**
   ```
   | 著作权人。软件名称。登记号：xxxx |
   ```

2. 运行生成脚本：
   ```bash
   python3 gen_pubs.py
   ```

3. 将对应的 PDF 放入 `files/` 目录

### 添加新学生

1. 编辑 `students.md`，在对应区域按格式添加：

   **在读学生格式：**
   ```
   - 姓名，年级，方向
   ```
   示例：`- 张三，24级，医学影像`

   **已毕业学生格式：** 同上，年级用入学年份（如 `2015级`），博士可标注 `2019博`

   **荣誉奖项格式：**
   ```
   ## 奖项名称

   年份：姓名1、姓名2、姓名3
   ```
   示例：
   ```
   ## 国家奖学金

   2025年：张三（研三）、李四（研二）
   ```

2. 运行生成脚本：
   ```bash
   python3 gen_students.py
   ```

   脚本会自动更新学生名单和荣誉按钮上的计数。

### 添加荣誉信息

荣誉信息和学生数据在同一个 `students.md` 中，位于末尾的 `# 荣誉奖项` 区域。每个奖项用 `## 奖项名称` 标注，下面按年份列出名单。
