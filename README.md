# aespa 错题集生成器 🌟💙🖤❄️🦋

将红笔批改的试卷自动转换为 **aespa 主题** 的精美错题集，让学习更有动力！

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ 功能特点

- 📸 **智能 OCR 识别** - 自动检测红笔批改标记，提取错题内容
- 🤖 **一键生成** - 单条命令完成从图片到 Word/PDF 的完整流程
- 💙 **aespa 主题** - 自动分配成员评语，让错题集充满活力
- ✅ **验证校对** - 交互式验证模式，确保识别准确率
- 📄 **专业排版** - 生成仿宋字体、带颜色标注的精美文档

---

## 🚀 快速开始

### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/dbk367/aespa-workbook.git
cd aespa-workbook

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Tesseract OCR (系统依赖)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# Windows:
# 下载安装包: https://github.com/UB-Mannheim/tesseract/wiki
```

### 一键生成错题集

```bash
python scripts/workflow.py -i /path/to/试卷图片.jpg -s 物理 -w 1
```

参数说明：
- `-i, --input`: 试卷图片路径或目录
- `-s, --subject`: 科目名称（如：物理、数学）
- `-w, --week`: 周次编号

---

## 📖 使用流程

### 方式一：一键工作流（推荐）

```bash
python scripts/workflow.py -i ./试卷图片/ -s 物理 -w 1
```

执行流程：
1. 🔍 **提取** - OCR 识别红笔标记，提取错题
2. ✓ **验证** - 显示识别结果供确认
3. 📝 **构建** - 生成带 aespa 评语的 Markdown
4. 📄 **生成** - 输出 Word 和 PDF 文档

### 方式二：分步执行

```bash
# 1. 提取错题
python scripts/extract_errors.py -i 物理46.jpg -s 物理 -w 1

# 2. 验证结果（交互式）
python scripts/verify_questions.py -j week1_物理_raw.json --interactive

# 3. 构建错题集
python scripts/build_workbook.py -i week1_物理_raw.json

# 4. 生成 Word
python scripts/generate_docx.py -i 九下-第1周错题集-aespa版.md -o 错题集.docx

# 5. 转换 PDF（可选）
python scripts/convert_pdf.py -i 错题集.docx -o 错题集.pdf
```

---

## 💙 aespa 成员介绍

| 成员 | Emoji | 性格 | 代表色 | 评语风格 |
|------|-------|------|--------|----------|
| **Karina** (柳智敏) | 💙 | 温柔队长 | 蓝色 | 鼓励型："这道题确实有点难，不过我们一起搞定它~" |
| **Giselle** (内永绘里) | 🖤 | 酷帅rapper | 紫色 | 自信型："这个知识点，拿下！" |
| **Winter** (金玟庭) | ❄️ | 可爱甜心 | 浅蓝 | 温暖型："你超棒的！继续加油！" |
| **Ningning** (宁艺卓) | 🦋 | 直率忙内 | 橙红 | 真实型："这道题坑了不少人，别气馁！" |

---

## 📁 项目结构

```
aespa-workbook/
├── SKILL.md                  # OpenClaw 技能文档
├── README.md                 # 本文件
├── requirements.txt          # Python 依赖
├── assets/
│   └── template.md          # 错题集模板
├── references/
│   └── aespa-style-guide.md # 成员风格详细指南
└── scripts/
    ├── extract_errors.py     # OCR 错题提取
    ├── verify_questions.py   # 验证校对
    ├── build_workbook.py     # 构建 Markdown
    ├── workflow.py           # 一键工作流
    ├── generate_docx.py      # 生成 Word
    ├── convert_pdf.py        # 转换 PDF
    └── init_output_dir.sh    # 初始化目录
```

---

## 🎯 输出示例

生成的错题集包含：

### 第一部分：原题（练习用）
- 原题内容 + 选项
- aespa 成员评语
- 图示标注

### 第二部分：答案与解析（参考用）
- 学生错误答案
- 正确答案（蓝色加粗）
- 详细解析
- 成员鼓励语

### 结尾
```
💙 Karina："这次整理完，下次考试一定没问题！"
🖤 Giselle："错题集完成！Next Level 准备就绪！"
❄️ Winter："辛苦啦～你是最棒的！"
🦋 Ningning："搞定！记住这些坑，考试直接过！"

💜 aespa 签名 💜
We are aespa！Be my ae！🌟
```

---

## ⚙️ 高级用法

### 批量处理

```bash
# 跳过验证，批量处理
python scripts/workflow.py -i ./images/ -s 数学 -w 2 --skip-verify
```

### 可视化调试

```bash
# 生成红笔标记识别可视化图
python scripts/extract_errors.py -i image.jpg -s 物理 -w 1 -v
```

### 自定义模板

```bash
# 使用自定义模板
python scripts/build_workbook.py -i errors.json -t my_template.md
```

---

## 🛠️ 系统要求

- **Python**: 3.8+
- **操作系统**: Windows / Linux / macOS
- **内存**: 建议 4GB+
- **依赖**: OpenCV, Tesseract OCR, python-docx

---

## 📝 注意事项

1. **图片质量** - 建议 300dpi 以上，红笔标记清晰可见
2. **光线均匀** - 避免阴影和反光影响 OCR 识别
3. **验证校对** - 重要考试前建议人工核对识别结果
4. **字体安装** - 确保系统安装了"仿宋"字体以获得最佳效果

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 💖 致谢

- 感谢 **aespa** 带来的音乐和正能量
- 感谢 OpenCV 和 Tesseract 提供的 OCR 能力
- 感谢所有使用和支持这个项目的朋友

---

**We are aespa! Be my ae! 🌟**

💙 🖤 ❄️ 🦋
