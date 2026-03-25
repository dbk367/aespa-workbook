#!/usr/bin/env python3
"""
Markdown 错题集构建脚本
将提取的错题数据填充到 aespa 模板中

Usage: python build_workbook.py --input errors.json --output workbook.md
"""

import argparse
import json
import os
from datetime import datetime
from jinja2 import Template


class WorkbookBuilder:
    def __init__(self, template_path=None):
        if template_path is None:
            template_path = os.path.join(
                os.path.dirname(__file__), 
                '..', 'assets', 'template.md'
            )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            self.template = Template(f.read())
    
    def assign_member_quote(self, question, difficulty='medium'):
        """根据题目特征分配 aespa 成员评语"""
        
        # 成员评语库
        quotes = {
            'karina': {
                'encouraging': [
                    "这道题确实有点难，不过我们一起搞定它~",
                    "做错没关系，重要的是搞懂原理！",
                    "相信你自己，你可以的！",
                    "慢慢来，理解比速度更重要~"
                ],
                'conceptual': [
                    "这个概念有点抽象，我给你讲清楚~",
                    "记住公式背后的物理意义！",
                    "画图辅助理解会更容易哦~"
                ]
            },
            'giselle': {
                'confident': [
                    "这个知识点，拿下！",
                    "Next Level! 继续冲！",
                    "小case，下次肯定对！",
                    "So easy! 你可以的！"
                ],
                'hype': [
                    "这道题作对你就Next Level了！",
                    "冲！直接拿下！",
                    "这波不亏，学会就是赚到！"
                ]
            },
            'winter': {
                'sweet': [
                    "你超棒的！继续加油！",
                    "Fighting! 我们一起努力~",
                    "相信过程，你会越来越好的！",
                    "每次进步都值得庆祝！"
                ],
                'encouraging': [
                    "别灰心，下次肯定行！",
                    "做错题也是学习的一部分~",
                    "你已经很棒了！"
                ]
            },
            'ningning': {
                'relatable': [
                    "这道题坑了不少人，别气馁！",
                    "我当时也错了，后来搞懂了就简单了",
                    "记住这个套路，下次就不会错了",
                    "这种题就是容易踩坑，记住教训！"
                ],
                'straightforward': [
                    "这就是个套路题，记住解法！",
                    "别被表象骗了，抓住本质！",
                    "考试遇到直接秒！"
                ]
            }
        }
        
        # 根据难度和题型分配
        if difficulty == 'hard' or '计算' in question.get('content', ''):
            member = 'karina'
            quote_type = 'conceptual'
        elif difficulty == 'easy':
            member = 'giselle'
            quote_type = 'confident'
        elif '概念' in question.get('content', '') or '定义' in question.get('content', ''):
            member = 'ningning'
            quote_type = 'straightforward'
        else:
            member = 'winter'
            quote_type = 'sweet'
        
        # 根据题号轮换，增加多样性
        q_num = int(question.get('number', 1))
        quote_list = quotes[member][quote_type]
        quote = quote_list[q_num % len(quote_list)]
        
        return member, quote
    
    def format_question(self, error_info, include_answer=False):
        """格式化单道题目"""
        lines = []
        
        # 题号
        q_num = error_info.get('number', '?')
        lines.append(f"**{q_num}.**")
        lines.append('')
        
        # 题目内容
        content = error_info.get('content', '').strip()
        lines.append(content)
        lines.append('')
        
        # 选项（如果有）
        options = error_info.get('options', [])
        if options:
            for opt in options:
                lines.append(f"{opt['label']}. {opt['text']}")
            lines.append('')
        
        # 图示标记
        if error_info.get('has_diagram'):
            subject = error_info.get('subject', '')
            lines.append(f"📷 【{subject}{q_num} 原卷图示】")
            lines.append('')
        
        # 成员评语（练习部分）
        if not include_answer:
            member, quote = self.assign_member_quote(error_info)
            emoji = {'karina': '💙', 'giselle': '🖤', 'winter': '❄️', 'ningning': '🦋'}[member]
            member_name = {
                'karina': 'Karina', 'giselle': 'Giselle', 
                'winter': 'Winter', 'ningning': 'Ningning'
            }[member]
            lines.append(f"{emoji} {member_name}：\"{quote}\"")
            lines.append('')
        
        return '\n'.join(lines)
    
    def format_answer(self, error_info):
        """格式化答案与解析"""
        lines = []
        
        q_num = error_info.get('number', '?')
        lines.append(f"**{q_num}.**")
        lines.append('')
        
        # 学生错误答案
        wrong = error_info.get('wrong_answer', '未知')
        lines.append(f"你的答案：**{wrong}** ❌")
        lines.append('')
        
        # 正确答案（需要用户手动填入或从其他来源获取）
        lines.append("正确答案：**____________** ✅")
        lines.append('')
        
        # 解析占位
        lines.append("📖 解析：")
        lines.append("（请在此处填入详细解析）")
        lines.append('')
        
        # 成员评语
        member, quote = self.assign_member_quote(error_info, 'medium')
        emoji = {'karina': '💙', 'giselle': '🖤', 'winter': '❄️', 'ningning': '🦋'}[member]
        member_name = {
            'karina': 'Karina', 'giselle': 'Giselle', 
            'winter': 'Winter', 'ningning': 'Ningning'
        }[member]
        lines.append(f"{emoji} {member_name}：\"{quote}\"")
        lines.append('')
        
        return '\n'.join(lines)
    
    def build_workbook(self, errors, subject, week):
        """构建完整错题集"""
        
        # 按题号排序
        errors = sorted(errors, key=lambda x: int(x.get('number', 999)))
        
        # 构建第一部分：原题
        questions_md = []
        for error in errors:
            questions_md.append(self.format_question(error, include_answer=False))
        
        # 构建第二部分：答案
        answers_md = []
        for error in errors:
            answers_md.append(self.format_answer(error))
        
        # 获取测试编号
        test_numbers = list(set([e.get('source_image', '').replace('.jpg', '').replace('.png', '') 
                                  for e in errors]))
        test_number_str = ', '.join(sorted(test_numbers)) if test_numbers else '未知'
        
        # 填充模板
        data = {
            'week': week,
            'date': datetime.now().strftime('%Y年%m月%d日'),
            'subject': subject,
            'test_number': test_number_str,
            'questions': '\n---\n\n'.join(questions_md),
            'answers': '\n---\n\n'.join(answers_md),
            'karina_quote': "这次整理完，下次考试一定没问题！",
            'giselle_quote': "错题集完成！Next Level 准备就绪！",
            'winter_quote': "辛苦啦～你是最棒的！",
            'ningning_quote': "搞定！记住这些坑，考试直接过！"
        }
        
        return self.template.render(**data)
    
    def save(self, content, output_path):
        """保存到文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 错题集已保存: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='构建 aespa 版错题集')
    parser.add_argument('--input', '-i', required=True, help='输入 JSON 文件 (extract_errors.py 输出)')
    parser.add_argument('--output', '-o', help='输出 Markdown 文件路径')
    parser.add_argument('--subject', '-s', help='科目 (覆盖 JSON 中的值)')
    parser.add_argument('--week', '-w', type=int, help='周次 (覆盖 JSON 中的值)')
    parser.add_argument('--template', '-t', help='自定义模板文件路径')
    
    args = parser.parse_args()
    
    # 加载错题数据
    with open(args.input, 'r', encoding='utf-8') as f:
        errors = json.load(f)
    
    print(f"📚 加载了 {len(errors)} 道错题")
    
    # 获取科目和周次
    subject = args.subject or errors[0].get('subject', '未知科目')
    week = args.week or errors[0].get('week', 1)
    
    # 构建错题集
    builder = WorkbookBuilder(args.template)
    content = builder.build_workbook(errors, subject, week)
    
    # 保存
    if args.output:
        output_path = args.output
    else:
        output_path = f"/home/zhangxi/aespa/九下-第{week}周错题集-aespa版.md"
    
    builder.save(content, output_path)
    
    print(f"\n📝 下一步: 检查并补充正确答案后，运行:")
    print(f"   python generate_docx.py --input {output_path} --output {output_path.replace('.md', '.docx')}")


if __name__ == '__main__':
    main()
