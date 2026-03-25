#!/usr/bin/env python3
"""
完整工作流脚本 - 一键处理试卷图片到错题集

Usage: python workflow.py --input /path/to/images --subject 物理 --week 1
"""

import argparse
import os
import sys
import json
import subprocess
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extract_errors import ErrorExtractor, save_raw_results
from build_workbook import WorkbookBuilder


class AespaWorkflow:
    def __init__(self, output_dir="/home/zhangxi/aespa"):
        self.output_dir = output_dir
        self.extractor = ErrorExtractor()
        self.builder = WorkbookBuilder()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def step1_extract(self, input_path, subject, week):
        """步骤1: 从图片中提取错题"""
        print("\n" + "="*60)
        print("🔍 步骤 1/4: 提取错题")
        print("="*60)
        
        # 处理单张图片或目录
        if os.path.isfile(input_path):
            image_paths = [input_path]
        else:
            image_paths = sorted([
                os.path.join(input_path, f) 
                for f in os.listdir(input_path) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])
        
        if not image_paths:
            print("❌ 未找到图片文件")
            return None
        
        print(f"发现 {len(image_paths)} 张图片")
        
        all_errors = []
        for img_path in image_paths:
            errors = self.extractor.process_image(img_path, subject, week)
            all_errors.extend(errors)
        
        if not all_errors:
            print("❌ 未识别到任何错题")
            return None
        
        # 保存原始结果
        raw_path = os.path.join(self.output_dir, f"week{week}_{subject}_raw.json")
        save_raw_results(all_errors, raw_path)
        
        print(f"✅ 提取完成，共 {len(all_errors)} 道错题")
        return raw_path
    
    def step2_verify(self, json_path):
        """步骤2: 验证识别结果"""
        print("\n" + "="*60)
        print("✓ 步骤 2/4: 验证识别结果")
        print("="*60)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            errors = json.load(f)
        
        print(f"\n识别到的错题列表:")
        print("-" * 40)
        
        for i, err in enumerate(errors[:10], 1):  # 只显示前10道
            q_num = err.get('number', '?')
            content_preview = err.get('content', '')[:30] + '...'
            print(f"{i}. 题号 {q_num}: {content_preview}")
        
        if len(errors) > 10:
            print(f"... 还有 {len(errors) - 10} 道")
        
        print("\n⚠️  请检查上述识别结果，确认无误后继续")
        
        # 生成验证报告
        verify_report = os.path.join(self.output_dir, 
            f"week{errors[0].get('week', 1)}_{errors[0].get('subject', 'unknown')}_verify.txt")
        
        with open(verify_report, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("错题识别验证报告\n")
            f.write("="*60 + "\n\n")
            
            for err in errors:
                f.write(f"题号: {err.get('number', '?')}\n")
                f.write(f"来源: {err.get('source_image', 'unknown')}\n")
                f.write(f"内容:\n{err.get('content', '')}\n")
                f.write("-"*40 + "\n\n")
        
        print(f"📝 详细验证报告: {verify_report}")
        
        return json_path
    
    def step3_build(self, json_path, subject, week):
        """步骤3: 构建 Markdown 错题集"""
        print("\n" + "="*60)
        print("📚 步骤 3/4: 构建错题集")
        print("="*60)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            errors = json.load(f)
        
        # 使用 JSON 中的值或参数
        subject = subject or errors[0].get('subject', '未知')
        week = week or errors[0].get('week', 1)
        
        # 构建内容
        content = self.builder.build_workbook(errors, subject, week)
        
        # 保存 Markdown
        md_path = os.path.join(self.output_dir, f"九下-第{week}周错题集-aespa版.md")
        self.builder.save(content, md_path)
        
        print(f"✅ Markdown 已生成: {md_path}")
        return md_path
    
    def step4_generate(self, md_path, subject, week):
        """步骤4: 生成 Word 和 PDF"""
        print("\n" + "="*60)
        print("📄 步骤 4/4: 生成 Word/PDF")
        print("="*60)
        
        docx_path = md_path.replace('.md', '.docx')
        pdf_path = md_path.replace('.md', '.pdf')
        
        # 生成 DOCX
        try:
            from generate_docx import parse_and_create_docx
            
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            parse_and_create_docx(md_content, docx_path)
            print(f"✅ Word 文档: {docx_path}")
        except Exception as e:
            print(f"⚠️  Word 生成失败: {e}")
            print("   请手动运行: python generate_docx.py")
        
        # 生成 PDF（可选）
        try:
            from convert_pdf import docx_to_pdf
            
            success = docx_to_pdf(docx_path, pdf_path)
            if success:
                print(f"✅ PDF 文档: {pdf_path}")
        except Exception as e:
            print(f"⚠️  PDF 生成跳过: {e}")
        
        return docx_path, pdf_path
    
    def run(self, input_path, subject, week, skip_verify=False):
        """运行完整工作流"""
        print("\n🌟 aespa 错题集生成器")
        print("   让学习更有动力！💙🖤❄️🦋")
        
        # 步骤1: 提取
        json_path = self.step1_extract(input_path, subject, week)
        if not json_path:
            return False
        
        # 步骤2: 验证
        if not skip_verify:
            json_path = self.step2_verify(json_path)
            confirm = input("\n识别结果正确吗? (y/n/quit): ").lower()
            if confirm == 'quit':
                print("已退出")
                return False
            elif confirm != 'y':
                print("请修正后重新运行")
                return False
        
        # 步骤3: 构建 Markdown
        md_path = self.step3_build(json_path, subject, week)
        
        # 步骤4: 生成文档
        docx_path, pdf_path = self.step4_generate(md_path, subject, week)
        
        # 完成报告
        print("\n" + "="*60)
        print("🎉 完成！生成的文件:")
        print("="*60)
        print(f"📊 原始数据: {json_path}")
        print(f"📝 Markdown: {md_path}")
        print(f"📄 Word: {docx_path}")
        if os.path.exists(pdf_path):
            print(f"📕 PDF: {pdf_path}")
        
        print("\n💡 提示:")
        print("   - 请打开 Word 文件补充正确答案")
        print("   - 检查并完善解析内容")
        print("   - 最终确认后打印或导出 PDF")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='aespa 错题集一键生成工作流',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单张图片
  python workflow.py -i /path/to/物理46.jpg -s 物理 -w 1
  
  # 处理整个目录
  python workflow.py -i /path/to/images/ -s 数学 -w 2
  
  # 跳过验证（批量处理）
  python workflow.py -i ./images -s 物理 -w 3 --skip-verify
        """
    )
    
    parser.add_argument('--input', '-i', required=True, 
                       help='输入图片路径或目录')
    parser.add_argument('--subject', '-s', required=True, 
                       help='科目名称 (如: 物理, 数学)')
    parser.add_argument('--week', '-w', type=int, required=True, 
                       help='周次 (如: 1, 2, 3)')
    parser.add_argument('--output-dir', '-o', default='/home/zhangxi/aespa',
                       help='输出目录 (默认: /home/zhangxi/aespa)')
    parser.add_argument('--skip-verify', action='store_true',
                       help='跳过人工验证步骤')
    
    args = parser.parse_args()
    
    # 检查依赖
    try:
        import cv2
        import pytesseract
        from jinja2 import Template
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装: pip install opencv-python pytesseract jinja2 Pillow")
        return
    
    # 运行工作流
    workflow = AespaWorkflow(args.output_dir)
    success = workflow.run(args.input, args.subject, args.week, args.skip_verify)
    
    if success:
        print("\n✨ We are aespa! Be my ae! ✨")
    else:
        print("\n❌ 工作流未完成")
        sys.exit(1)


if __name__ == '__main__':
    main()
