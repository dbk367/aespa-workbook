#!/usr/bin/env python3
"""
OCR 错题识别脚本
从红笔批改的试卷图片中提取错题信息

Usage: python extract_errors.py --input /path/to/image.jpg --subject 物理 --week 1
"""

import argparse
import os
import re
import cv2
import numpy as np
from PIL import Image
import pytesseract

class ErrorExtractor:
    def __init__(self):
        # 红笔颜色范围 (HSV)
        self.red_lower1 = np.array([0, 100, 100])
        self.red_upper1 = np.array([10, 255, 255])
        self.red_lower2 = np.array([160, 100, 100])
        self.red_upper2 = np.array([180, 255, 255])
        
    def detect_red_marks(self, image_path):
        """检测图片中的红笔标记区域"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
            
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 创建红色掩码
        mask1 = cv2.inRange(hsv, self.red_lower1, self.red_upper1)
        mask2 = cv2.inRange(hsv, self.red_lower2, self.red_upper2)
        red_mask = cv2.bitwise_or(mask1, mask2)
        
        # 形态学操作，连接相近的红色区域
        kernel = np.ones((5, 5), np.uint8)
        red_mask = cv2.dilate(red_mask, kernel, iterations=2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 过滤太小的区域
        min_area = 500
        error_regions = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                error_regions.append({
                    'bbox': (x, y, w, h),
                    'area': area,
                    'center': (x + w//2, y + h//2)
                })
        
        return img, error_regions, red_mask
    
    def extract_question_regions(self, img, error_regions, margin=100):
        """根据红笔位置提取完整题目区域"""
        questions = []
        h, w = img.shape[:2]
        
        for idx, region in enumerate(error_regions):
            x, y, bw, bh = region['bbox']
            
            # 扩大区域以包含完整题目
            x1 = max(0, x - margin)
            y1 = max(0, y - margin * 2)  # 题目通常在红笔上方
            x2 = min(w, x + bw + margin)
            y2 = min(h, y + bh + margin)
            
            question_img = img[y1:y2, x1:x2]
            questions.append({
                'id': idx + 1,
                'image': question_img,
                'bbox': (x1, y1, x2, y2),
                'error_center': region['center']
            })
        
        return questions
    
    def ocr_question(self, question_img, lang='chi_sim+eng'):
        """对题目区域进行 OCR 识别"""
        # 转换为 PIL Image
        rgb_img = cv2.cvtColor(question_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        
        # OCR 识别
        text = pytesseract.image_to_string(pil_img, lang=lang)
        
        # 清理文本
        text = self._clean_text(text)
        
        return text
    
    def _clean_text(self, text):
        """清理 OCR 识别结果"""
        # 移除多余空白
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        # 移除页眉页脚常见干扰
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # 跳过页码、日期等
            if re.match(r'^\d+$', line) and len(line) < 3:
                continue
            if '年' in line and '月' in line and '日' in line:
                continue
            if len(line) > 0:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def parse_question_info(self, text):
        """解析题目信息：题号、题目内容、错误答案"""
        info = {
            'number': None,
            'content': '',
            'wrong_answer': '',
            'options': [],
            'has_diagram': False
        }
        
        lines = text.split('\n')
        
        # 提取题号 (如: 46. 或 46、或 (46))
        for line in lines[:3]:  # 只看前几行
            match = re.search(r'[(（]?\s*(\d+)\s*[)）]?\s*[\.、．]', line)
            if match:
                info['number'] = match.group(1)
                break
            # 备选格式: 纯数字开头
            match = re.search(r'^\s*(\d+)\s*[\.、]', line)
            if match:
                info['number'] = match.group(1)
                break
        
        # 提取选项 (A. B. C. D.)
        options_pattern = r'([A-D])[\.、．]\s*([^\n]+)'
        options = re.findall(options_pattern, text)
        if options:
            info['options'] = [{'label': opt[0], 'text': opt[1].strip()} for opt in options]
        
        # 检查是否有图示标记
        if '[图]' in text or '图示' in text or '如图所示' in text:
            info['has_diagram'] = True
        
        # 提取学生错误答案（通常在红笔旁边）
        # 查找被划掉或标记的答案
        wrong_patterns = [
            r'[×✗✕][\s:：]*(\w+)',
            r'错[\s:：]*(\w+)',
            r'(\w+)\s*[×✗]',
        ]
        for pattern in wrong_patterns:
            match = re.search(pattern, text)
            if match:
                info['wrong_answer'] = match.group(1)
                break
        
        # 题目内容（移除题号后的所有内容）
        content_lines = []
        started = False
        for line in lines:
            if info['number'] and (line.startswith(info['number']) or re.search(rf'^\s*[(（]?{info["number"]}[)）]?', line)):
                started = True
            if started:
                # 跳过选项行
                if re.match(r'^[A-D][\.、．]', line.strip()):
                    continue
                content_lines.append(line)
        
        info['content'] = '\n'.join(content_lines)
        
        return info
    
    def process_image(self, image_path, subject, week):
        """处理单张图片，返回错题列表"""
        print(f"\n🔍 处理图片: {os.path.basename(image_path)}")
        
        # 1. 检测红笔标记
        img, error_regions, red_mask = self.detect_red_marks(image_path)
        print(f"   发现 {len(error_regions)} 处红笔标记")
        
        if len(error_regions) == 0:
            print("   ⚠️ 未检测到红笔标记，跳过")
            return []
        
        # 2. 提取题目区域
        questions = self.extract_question_regions(img, error_regions)
        
        # 3. OCR 识别
        errors = []
        for q in questions:
            print(f"   📝 识别第 {q['id']} 题...", end='')
            
            text = self.ocr_question(q['image'])
            info = self.parse_question_info(text)
            
            # 补充元数据
            info['source_image'] = os.path.basename(image_path)
            info['subject'] = subject
            info['week'] = week
            info['region_bbox'] = q['bbox']
            
            if info['number']:
                print(f" 题号: {info['number']}")
                errors.append(info)
            else:
                print(" 未能识别题号")
        
        return errors


def save_raw_results(errors, output_path):
    """保存原始 OCR 结果供验证"""
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(errors, f, ensure_ascii=False, indent=2)
    print(f"\n💾 原始结果已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='从红笔批改的试卷中提取错题')
    parser.add_argument('--input', '-i', required=True, help='输入图片路径或目录')
    parser.add_argument('--subject', '-s', required=True, help='科目 (如: 物理, 数学)')
    parser.add_argument('--week', '-w', type=int, required=True, help='周次')
    parser.add_argument('--output', '-o', help='输出 JSON 文件路径')
    parser.add_argument('--visualize', '-v', action='store_true', help='生成可视化结果图')
    
    args = parser.parse_args()
    
    extractor = ErrorExtractor()
    
    # 处理单张图片或整个目录
    if os.path.isfile(args.input):
        image_paths = [args.input]
    else:
        image_paths = [
            os.path.join(args.input, f) 
            for f in os.listdir(args.input) 
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
    
    all_errors = []
    for img_path in sorted(image_paths):
        errors = extractor.process_image(img_path, args.subject, args.week)
        all_errors.extend(errors)
    
    print(f"\n✅ 共识别 {len(all_errors)} 道错题")
    
    # 保存结果
    if args.output:
        save_raw_results(all_errors, args.output)
    else:
        default_output = f"/home/zhangxi/aespa/week{args.week}_{args.subject}_errors_raw.json"
        save_raw_results(all_errors, default_output)
    
    return all_errors


if __name__ == '__main__':
    main()
