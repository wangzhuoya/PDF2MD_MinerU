#!/usr/bin/env python3
"""
清洗markdown文档
删除图片链接和Figure开头的行
"""
import re
from pathlib import Path

def show_all_headings(file_path):
    """
    显示markdown文件中所有的标题（以#开头的行）
    Args:
        file_path (str): markdown文件路径
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    headings = []
    
    print("📋 文档中所有标题:")
    print("=" * 50)
    
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('#'):
            headings.append((i, line.strip()))
            print(f"第{i}行: {line.strip()}")
    
    print("=" * 50)
    print(f"共找到 {len(headings)} 个标题")
    print()
    
    return headings

def analyze_heading_structure(lines):
    """
    分析文档的标题结构，判断是否需要特殊处理
    Args:
        lines (list): 文档行列表
    Returns:
        dict: 分析结果
    """
    headings = []
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            # 检查标题级别
            level = len(line.strip()) - len(line.strip().lstrip('#'))
            headings.append({
                'line_index': i,
                'level': level,
                'content': line.strip(),
                'has_roman': bool(re.match(r'^\s*#+\s*([IVX]+)\.?\s+', line.strip())),
                'has_letter': bool(re.match(r'^\s*#+\s*([A-Z])\.?\s+', line.strip())),
                'has_number': bool(re.match(r'^\s*#+\s*(\d+(?:[\.\s]+\d+)*?)[\.\s]*\s+', line.strip()))
            })
    
    # 判断是否所有标题都是一级标题且没有特殊格式
    all_level_1 = all(h['level'] == 1 for h in headings)
    no_special_format = all(not (h['has_roman'] or h['has_letter'] or h['has_number']) for h in headings)
    
    return {
        'headings': headings,
        'all_level_1': all_level_1,
        'no_special_format': no_special_format,
        'needs_default_adjustment': all_level_1 and no_special_format and len(headings) > 1
    }

def adjust_heading_levels(line):
    """
    根据标题中数字、罗马数字、字母的个数调整标题级别
    Args:
        line (str): 标题行
    Returns:
        str: 调整后的标题行
    """
    # 1. 匹配罗马数字格式：# I. INTRODUCTION, # II. METHODS 等
    roman_match = re.match(r'^(#+)\s*([IVX]+)\.?\s+(.*)', line.strip())
    if roman_match:
        current_hashes, roman, title = roman_match.groups()
        # 罗马数字标题设为二级标题
        new_level = 2
        new_hashes = '#' * new_level
        new_line = f"{new_hashes} {roman}. {title}"
        
        if len(current_hashes) != new_level:
            print(f"🔧 调整罗马数字标题级别: {line.strip()[:50]}... -> {new_line[:50]}...")
            return new_line
        return line
    
    # 2. 匹配字母格式：# A anything, # B anything 等
    letter_match = re.match(r'^(#+)\s*([A-Z])\.?\s+(.*)', line.strip())
    if letter_match:
        current_hashes, letter, title = letter_match.groups()
        # 字母标题设为三级标题
        new_level = 3
        new_hashes = '#' * new_level
        new_line = f"{new_hashes} {letter} {title}"
        
        if len(current_hashes) != new_level:
            print(f"🔧 调整字母标题级别: {line.strip()[:50]}... -> {new_line[:50]}...")
            return new_line
        return line
    
    # 3. 匹配数字格式：# 数字[.空格]数字[.空格]数字... 标题内容
    number_match = re.match(r'^(#+)\s*(\d+(?:[\.\s]+\d+)*?)[\.\s]*\s+(.*)', line.strip())
    if number_match:
        current_hashes, numbers_part, title = number_match.groups()
        
        # 提取所有数字（忽略点和空格）
        numbers = re.findall(r'\d+', numbers_part)
        num_count = len(numbers)
        
        # 根据数字个数确定标题级别（最多5级）
        new_level = min(num_count + 1, 5)
        new_hashes = '#' * new_level
        
        # 重新构建数字部分，使用标准格式（数字.数字.数字）
        if num_count == 1:
            formatted_numbers = numbers[0]
        else:
            formatted_numbers = '.'.join(numbers)
        
        new_line = f"{new_hashes} {formatted_numbers} {title}"
        
        if len(current_hashes) != new_level:
            print(f"🔧 调整数字标题级别: {line.strip()[:50]}... -> {new_line[:50]}...")
            return new_line
    
    return line

def clean_markdown_file(file_path):
    """
    清洗markdown文件，删除图片链接和Figure开头的行
    Args:
        file_path (str): markdown文件路径
    """
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"🚀 开始清洗文件: {file_path}")
    print(f"📄 原始文件大小: {len(content)} 字符")
    
    # 按行分割内容
    lines = content.split('\n')
    
    # 分析标题结构
    heading_analysis = analyze_heading_structure(lines)
    if heading_analysis['needs_default_adjustment']:
        print(f"📝 检测到所有标题均为一级标题且无特殊格式，将应用默认调整规则")
    
    cleaned_lines = []
    removed_images = 0
    removed_figures = 0
    removed_references = False
    removed_acknowledgements = False
    removed_appendix = False
    adjusted_headings = 0
    first_heading_processed = False
    
    for line in lines:
        # 检查是否为图片链接行
        # 匹配 ![...](...)、<img ...>、[image: ...]等格式
        if re.search(r'!\[.*?\]\(.*?\)|<img.*?>|\[image:.*?\]', line, re.IGNORECASE):
            removed_images += 1
            print(f"🖼️ 删除图片链接: {line[:50]}...")
            continue
        
        # 检查是否为Figure开头的行或Fig./FIG.数字开头的行
        if (line.strip().startswith('Figure') or 
            re.match(r'^\s*Fig\.\s*\d+\.?', line, re.IGNORECASE)):
            removed_figures += 1
            print(f"📊 删除图注: {line[:50]}...")
            continue
        
        # 调整标题级别
        original_line = line
        
        # 如果需要默认调整（所有标题都是一级且无特殊格式）
        if heading_analysis['needs_default_adjustment'] and line.strip().startswith('#'):
            if not first_heading_processed:
                # 第一个标题保持一级
                first_heading_processed = True
                print(f"🔧 保持第一个标题为一级: {line.strip()[:50]}...")
            else:
                # 其余标题改为二级
                if line.strip().startswith('# ') and not line.strip().startswith('## '):
                    line = '##' + line[1:]
                    adjusted_headings += 1
                    print(f"🔧 调整标题为二级: {original_line.strip()[:50]}... -> {line.strip()[:50]}...")
        else:
            # 使用原有的标题级别调整逻辑
            line = adjust_heading_levels(line)
            if line != original_line:
                adjusted_headings += 1
        
        # 在标题调整后检查是否遇到需要删除的部分
        # 检查是否遇到References标题（不区分大小写，允许冒号等标点）
        if re.match(r'^\s*#+\s*references\s*[:\.]?\s*$', line, re.IGNORECASE):
            removed_references = True
            print(f"📚 发现References标题，删除此处及之后的所有内容: {line[:50]}...")
            break
        
        # 检查是否遇到Acknowledgements标题（不区分大小写）
        if re.match(r'^\s*#+\s*acknowledg.*\s*[:\.]?\s*$', line, re.IGNORECASE):
            removed_acknowledgements = True
            print(f"🙏 发现Acknowledgements标题，删除此处及之后的所有内容: {line[:50]}...")
            break
        
        # 检查是否遇到Appendix标题（不区分大小写）
        if re.match(r'^\s*#+\s*appendix.*', line, re.IGNORECASE):
            removed_appendix = True
            print(f"📎 发现Appendix标题，删除此处及之后的所有内容: {line[:50]}...")
            break
        
        # 保留其他行
        cleaned_lines.append(line)
    
    # 重新组合内容
    cleaned_content = '\n'.join(cleaned_lines)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"✅ 清洗完成!")
    print(f"📊 统计信息:")
    print(f"   - 删除图片链接: {removed_images} 个")
    print(f"   - 删除图注行: {removed_figures} 个")
    print(f"   - 调整标题级别: {adjusted_headings} 个")
    print(f"   - 删除References部分: {'是' if removed_references else '否'}")
    print(f"   - 删除Acknowledgements部分: {'是' if removed_acknowledgements else '否'}")
    print(f"   - 删除Appendix部分: {'是' if removed_appendix else '否'}")
    print(f"   - 清洗后大小: {len(cleaned_content)} 字符")
    print(f"   - 减少内容: {len(content) - len(cleaned_content)} 字符")

def main():
    """主函数"""
    # 目标文件路径
    file_path = "/home/wang2go/Code/CNOOC_RAG/CNOOC_RAG/data/01_data/arxiv_md/1401.5546.md"
    
    # 检查文件是否存在
    if not Path(file_path).exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 首先显示所有标题
    show_all_headings(file_path)
    
    # 清洗文件
    clean_markdown_file(file_path)

if __name__ == "__main__":
    main()