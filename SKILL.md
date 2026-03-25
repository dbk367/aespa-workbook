---
name: aespa-workbook
description: Create aespa-themed error workbooks from corrected exam papers. Use when user asks to create error workbooks, practice sets, or study materials with aespa/K-pop styling. Supports processing corrected test images, extracting questions, formatting with aespa member quotes, and generating Word/PDF outputs.
---

# aespa Error Workbook Creator

Create stylish error workbooks from corrected exam papers with aespa K-pop group theming.

## When to Use

Use this skill when:
- User wants to create "aespa版错题集" (aespa-themed error workbook)
- Processing corrected exam/test papers with red marks
- Creating practice materials with K-pop member quotes and styling
- Generating Word or PDF study materials

## Quick Start

### Input Requirements

1. **Corrected test paper images** with visible red marks (红叉/圈画)
2. **Subject info** (e.g., "物理46", "数学期中")
3. **Week number** (e.g., "第一周", "第二周")

### Output

Generates in `/home/zhangxi/aespa/`:
- `九下-第X周错题集-aespa版.docx`
- `九下-第X周错题集-aespa版.pdf`

## Installation

```bash
# 安装依赖
cd /root/.openclaw/workspace/skills/aespa-workbook
pip install -r requirements.txt

# 安装 Tesseract OCR (系统依赖)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# Windows:
# 下载安装包: https://github.com/UB-Mannheim/tesseract/wiki
```

## Quick Start - 一键生成

```bash
# 完整工作流：图片 → 错题集
python scripts/workflow.py -i /path/to/images -s 物理 -w 1

# 或分步执行：
# 1. 提取错题
python scripts/extract_errors.py -i /path/to/物理46.jpg -s 物理 -w 1

# 2. 验证结果
python scripts/verify_questions.py -j week1_物理_raw.json --interactive

# 3. 构建错题集
python scripts/build_workbook.py -i week1_物理_raw.json -o workbook.md

# 4. 生成 Word
python scripts/generate_docx.py --input workbook.md --output workbook.docx

# 5. 转换为 PDF (可选)
python scripts/convert_pdf.py --input workbook.docx --output workbook.pdf
```

## Workflow

### Step 1: Identify Errors

From corrected test images:
1. Locate questions with red marks (红叉/圈画)
2. Record: question number, wrong answer, correct answer

### Step 2: Extract Questions

**Critical: Extract text exactly as shown, no rewriting or summarizing**

- Copy question text **word-for-word**
- Include all sub-questions (①②③④⑤)
- Preserve all diagrams: `📷 【物理XX 原卷图示】`

### Step 3: Verify Before Output

**Mandatory check before generating Word/PDF:**
- Compare extracted text against original images
- Ensure **zero differences** - no rewriting, abbreviating, or expanding
- Check: question text, options, units, symbols

### Step 4: Format Document

See [references/aespa-style-guide.md](references/aespa-style-guide.md) for:
- Member personalities and colors
- Quote placement rules
- Lyric references
- Document formatting specs

### Step 5: Generate Output

```bash
# Generate Word
python scripts/generate_docx.py --input workbook.md --output filename.docx

# Convert to PDF
python scripts/convert_pdf.py --input filename.docx --output filename.pdf
```

## Automated Workflow

### One-Command Generation

```bash
python scripts/workflow.py -i /path/to/images -s 物理 -w 1
```

This runs the complete pipeline:
1. **Extract** - OCR detects red marks and extracts questions
2. **Verify** - Shows extracted questions for confirmation
3. **Build** - Generates Markdown with aespa formatting
4. **Generate** - Creates Word and PDF documents

### Batch Processing

```bash
# Skip verification for batch processing
python scripts/workflow.py -i ./images -s 数学 -w 2 --skip-verify
```

## Individual Tools

### extract_errors.py - OCR Extraction

Detects red correction marks and extracts question text.

```bash
python scripts/extract_errors.py -i image.jpg -s 物理 -w 1 -v
```

Options:
- `-i, --input`: Image file or directory
- `-s, --subject`: Subject name
- `-w, --week`: Week number
- `-o, --output`: Output JSON path
- `-v, --visualize`: Generate visualization images

### verify_questions.py - Verification

Validates OCR accuracy against original images.

```bash
# Automatic verification
python scripts/verify_questions.py -j errors.json

# Interactive correction mode
python scripts/verify_questions.py -j errors.json --interactive
```

### build_workbook.py - Markdown Builder

Builds formatted workbook from extracted errors.

```bash
python scripts/build_workbook.py -i errors.json -o workbook.md
```

Features:
- Auto-assigns aespa member quotes based on difficulty
- Formats questions with proper structure
- Generates answer key section

## File Organization

Output to: `/home/zhangxi/aespa/`
Create folder if not exists.

## Document Structure

```
第一部分：原题（练习用）
- Original questions only
- aespa member quotes after key questions
- Group cheer at section end

第二部分：答案与解析（参考用）  
- Student wrong answers
- Correct answers (bold, blue highlight)
- Explanations (compact format)
- Member comments in their colors
```

## Member Reference

| Member | Emoji | Personality | Color (RGB) |
|--------|-------|-------------|-------------|
| Karina (柳智敏) | 💙 | Gentle leader, encouraging | 0, 102, 204 |
| Giselle (内永绘里) | 🖤 | Cool rapper, confident | 102, 0, 153 |
| Winter (金玟庭) | ❄️ | Cute, warm, sweet | 0, 153, 204 |
| Ningning (宁艺卓) | 🦋 | Straightforward, relatable | 204, 51, 0 |

## Common Mistakes to Avoid

1. **Don't rewrite questions** - Copy exactly from source
2. **Don't skip verification** - Always compare against original images
3. **Don't forget diagrams** - Label all figure references clearly
4. **Don't mix member voices** - Keep each member's personality consistent

## Example Usage

User: "做aespa版错题集，物理46、47、48"

→ Process images
→ Extract questions verbatim  
→ Verify against originals
→ Apply aespa formatting
→ Output to /home/zhangxi/aespa/
