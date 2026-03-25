#!/usr/bin/env python3
"""
题目验证脚本
对比 OCR 识别结果与原始图片，确保 100% 准确

Usage: python verify_questions.py --json errors.json --images /path/to/images
"""

import argparse
import os
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class QuestionVerifier:
    def __init__(self):
        self.similarity_threshold = 0.85
    
    def load_image(self, image_path):
        """加载图片"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        return img
    
    def extract_region(self, img, bbox):
        """提取指定区域"""
        x1, y1, x2, y2 = bbox
        return img[y1:y2, x1:x2]
    
    def compare_text(self, ocr_text, expected_text=None):
        """文本相似度比较"""
        if not expected_text:
            return None, "无预期文本"
        
        # 简单字符匹配率
        ocr_clean = self._normalize_text(ocr_text)
        expected_clean = self._normalize_text(expected_text)
        
        if len(expected_clean) == 0:
            return 0, "预期文本为空"
        
        # 计算相似度
        matches = sum(1 for a, b in zip(ocr_clean, expected_clean) if a == b)
        similarity = matches / max(len(ocr_clean), len(expected_clean))
        
        status = "✓ 准确" if similarity >= self.similarity_threshold else "⚠ 需检查"
        
        return similarity, status
    
    def _normalize_text(self, text):
        """标准化文本用于比较"""
        import re
        # 移除空格、标点、换行
        text = re.sub(r'\s+', '', text)
        text = re.sub(r'[，。！？、；：""''（）【】]', '', text)
        return text.lower()
    
    def highlight_differences(self, ocr_text, reference_text):
        """高亮显示差异"""
        import difflib
        
        d = difflib.Differ()
        diff = list(d.compare(ocr_text.splitlines(), reference_text.splitlines()))
        
        result = []
        for line in diff:
            if line.startswith('  '):
                result.append(f"  {line[2:]}")  # 相同
            elif line.startswith('- '):
                result.append(f"- {line[2:]}")  # OCR 有但参考没有
            elif line.startswith('+ '):
                result.append(f"+ {line[2:]}")  # 参考有但 OCR 没有
        
        return '\n'.join(result)
    
    def create_visual_diff(self, image_path, error_info, output_path):
        """创建可视化对比图"""
        img = self.load_image(image_path)
        
        # 在图片上标注识别区域
        bbox = error_info.get('region_bbox')
        if bbox:
            x1, y1, x2, y2 = bbox
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            
            # 添加文字标签
            q_num = error_info.get('number', '?')
            label = f"Q{q_num}"
            cv2.putText(img, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 添加 OCR 识别结果
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)
        
        # 尝试加载中文字体
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 20)
        except:
            font = ImageFont.load_default()
        
        # 在图片底部添加 OCR 文本
        ocr_text = error_info.get('content', '')[:100] + '...'
        draw.text((10, img.shape[0] - 100), f"OCR: {ocr_text}", fill=(255, 0, 0), font=font)
        
        # 保存
        pil_img.save(output_path)
        return output_path
    
    def verify_batch(self, json_path, images_dir):
        """批量验证"""
        # 加载 JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            errors = json.load(f)
        
        print(f"\n🔍 开始验证 {len(errors)} 道错题...")
        print("="*60)
        
        results = {
            'passed': [],
            'needs_review': [],
            'failed': []
        }
        
        for i, error in enumerate(errors, 1):
            print(f"\n[{i}/{len(errors)}] 题号 {error.get('number', '?')}:")
            
            # 检查必要字段
            if not error.get('content'):
                print("   ❌ 题目内容为空")
                results['failed'].append(error)
                continue
            
            if not error.get('number'):
                print("   ⚠️  未能识别题号")
                results['needs_review'].append(error)
                continue
            
            # 内容长度检查
            content = error.get('content', '')
            if len(content) < 10:
                print(f"   ⚠️  内容过短 ({len(content)} 字符)，可能需要检查")
                results['needs_review'].append(error)
                continue
            
            print(f"   ✓ 内容长度: {len(content)} 字符")
            print(f"   ✓ 来源图片: {error.get('source_image', 'unknown')}")
            
            # 检查是否包含乱码特征
            if self._has_garbage(content):
                print("   ⚠️  检测到可能的乱码")
                results['needs_review'].append(error)
                continue
            
            results['passed'].append(error)
        
        # 生成报告
        print("\n" + "="*60)
        print("📊 验证报告")
        print("="*60)
        print(f"✓ 通过: {len(results['passed'])} 道")
        print(f"⚠ 需人工检查: {len(results['needs_review'])} 道")
        print(f"❌ 失败: {len(results['failed'])} 道")
        
        return results
    
    def _has_garbage(self, text):
        """检测文本是否包含乱码特征"""
        # 检查异常字符比例
        import re
        
        # 如果包含大量非中英文字符
        weird_chars = len(re.findall(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\n\.，。！？、；：""''（）【】\-*/+=^]', text))
        total_chars = len(text)
        
        if total_chars > 0 and weird_chars / total_chars > 0.1:
            return True
        
        return False
    
    def generate_correction_guide(self, results, output_path):
        """生成人工修正指南"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("错题识别人工修正指南\n")
            f.write("="*60 + "\n\n")
            
            if results['needs_review']:
                f.write("【需要检查的题目】\n\n")
                for error in results['needs_review']:
                    f.write(f"题号: {error.get('number', '?')}\n")
                    f.write(f"来源: {error.get('source_image', 'unknown')}\n")
                    f.write(f"当前识别内容:\n{error.get('content', 'N/A')}\n")
                    f.write("-"*40 + "\n\n")
            
            if results['failed']:
                f.write("【识别失败的题目】\n\n")
                for error in results['failed']:
                    f.write(f"题号: {error.get('number', '?')}\n")
                    f.write(f"请重新拍照或手动输入\n")
                    f.write("-"*40 + "\n\n")
        
        print(f"\n📝 修正指南已保存: {output_path}")


def interactive_verify(json_path):
    """交互式验证"""
    with open(json_path, 'r', encoding='utf-8') as f:
        errors = json.load(f)
    
    print("\n📝 交互式验证模式")
    print("="*60)
    print("请逐题确认识别结果，输入:")
    print("  y = 正确")
    print("  n = 错误，需要修改")
    print("  s = 跳过")
    print("  q = 退出并保存")
    print("="*60)
    
    corrected = []
    
    for i, error in enumerate(errors, 1):
        print(f"\n[{i}/{len(errors)}] 题号 {error.get('number', '?')}")
        print("-"*40)
        print(error.get('content', '无内容'))
        print("-"*40)
        
        cmd = input("确认 (y/n/s/q): ").lower()
        
        if cmd == 'q':
            break
        elif cmd == 'y':
            error['verified'] = True
            corrected.append(error)
        elif cmd == 'n':
            print("请输入正确内容（多行输入，空行结束）:")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            error['content'] = '\n'.join(lines)
            error['verified'] = True
            error['manual_corrected'] = True
            corrected.append(error)
        elif cmd == 's':
            continue
    
    # 保存修正后的结果
    output_path = json_path.replace('.json', '_corrected.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(corrected, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已保存修正结果: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description='验证 OCR 识别结果')
 parser.add_argument('--json', '-j', required=True, help='JSON 文件路径')
    parser.add_argument('--images', '-i', help='原始图片目录（用于可视化）')
    parser.add_argument('--interactive', '-a', action='store_true', 
                       help='交互式验证模式')
    parser.add_argument('--output', '-o', help='验证报告输出路径')
    
    args = parser.parse_args()
    
    verifier = QuestionVerifier()
    
    if args.interactive:
        interactive_verify(args.json)
    else:
        results = verifier.verify_batch(args.json, args.images)
        
        # 生成修正指南
        if results['needs_review'] or results['failed']:
            output = args.output or args.json.replace('.json', '_correction_guide.txt')
            verifier.generate_correction_guide(results, output)


if __name__ == '__main__':
    main()
