#!/usr/bin/env python3
"""
思维日记 - Daily Insights
按天查看每日问题的分析工具

基于已解析的会话数据进行日期分组分析
"""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from talkshow.storage.json_storage import JSONStorage
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text


def round_to_half_hour(dt):
    """将时间归整到最近的半点或整点"""
    # 获取分钟数
    minutes = dt.minute
    
    # 确定最近的半点或整点
    if minutes <= 15:
        # 归整到整点
        rounded_minutes = 0
    elif minutes <= 45:
        # 归整到半点
        rounded_minutes = 30
    else:
        # 归整到下一个整点
        rounded_minutes = 0
        dt = dt + timedelta(hours=1)
    
    return dt.replace(minute=rounded_minutes, second=0, microsecond=0)


def group_questions_by_date_and_time(sessions):
    """按日期和时间分组问题"""
    daily_questions = defaultdict(list)
    
    for session in sessions:
        # 使用解析器已经提取的时间信息
        session_start_time = session.start_time  # ChatSession.start_time 属性
        date_str = session_start_time.strftime('%Y-%m-%d')
        
        # 为这个会话的每个QA pair创建时间条目
        for qa_pair in session.qa_pairs:
            question = qa_pair.question.strip()
            if question:
                # 使用QA pair的时间戳，如果没有则使用会话开始时间
                qa_time = qa_pair.timestamp or session_start_time
                
                # 归整时间到最近的半点或整点
                rounded_time = round_to_half_hour(qa_time)
                
                # 使用已有的摘要，如果没有则使用原问题
                q_summary = qa_pair.question_summary or question
                
                daily_questions[date_str].append({
                    'time': rounded_time,
                    'time_str': rounded_time.strftime('%H:%M'),
                    'original': question,
                    'summary': q_summary,
                    'session_theme': session.meta.theme
                })
    
    # 对每天的问题按时间排序
    for date_str in daily_questions:
        daily_questions[date_str].sort(key=lambda x: x['time'])
    
    return daily_questions


def print_daily_insights(daily_questions):
    """使用 Rich 打印思维日记表格"""
    console = Console()
    
    # 标题
    title = Text("🎭 TalkShow - 思维日记 (Daily Insights)", style="bold magenta")
    console.print(title, justify="center")
    console.print()
    
    # 按日期排序
    sorted_dates = sorted(daily_questions.keys())
    
    total_days = len(sorted_dates)
    total_questions = sum(len(questions) for questions in daily_questions.values())
    
    # 统计概览
    stats_text = f"📊 统计概览：{total_days} 天，共 {total_questions} 个问题"
    console.print(stats_text, style="bold blue")
    console.print()
    
    # 为每一天创建一个表格
    for date in sorted_dates:
        questions = daily_questions[date]
        
        if not questions:
            continue
            
        # 创建当天的表格
        table = Table(
            title=f"📅 {date} ({len(questions)} 个问题)",
            box=box.ROUNDED,
            title_style="bold cyan",
            show_header=True,
            header_style="bold white on blue"
        )
        
        # 添加列
        table.add_column("时间", width=8, style="green", no_wrap=True)
        table.add_column("问题", min_width=80, max_width=120, style="white")
        table.add_column("主题", width=30, style="yellow", no_wrap=True)
        
        # 添加行
        for q in questions:
            # 处理问题文本，限制长度
            question_text = q['summary'] or q['original']
            if len(question_text) > 120:
                question_text = question_text[:117] + "..."
            
            # 处理主题文本，限制长度
            theme_text = q['session_theme']
            if len(theme_text) > 25:
                theme_text = theme_text[:22] + "..."
                
            table.add_row(
                q['time_str'],
                question_text,
                theme_text
            )
        
        console.print(table)
        console.print()  # 表格之间的空行


def save_daily_insights_json(daily_questions, output_file):
    """保存为 JSON 格式"""
    # 转换为可序列化的格式
    serializable_data = {}
    for date, questions in daily_questions.items():
        serializable_data[date] = [
            {
                'time': q['time_str'],
                'summary': q['summary'],
                'original': q['original'][:200] + "..." if len(q['original']) > 200 else q['original'],
                'session_theme': q['session_theme']
            }
            for q in questions
        ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_data, f, ensure_ascii=False, indent=2)
    
    console = Console()
    console.print(f"💾 思维日记已保存至：{output_file}", style="bold green")


def main():
    """主函数"""
    console = Console()
    console.print(f"🕒 {datetime.now()}", style="dim")
    console.print()
    
    # 尝试从已有的存储加载数据
    storage_path = "data/parsed_sessions.json"
    
    if Path(storage_path).exists():
        console.print(f"📁 从存储加载数据：{storage_path}", style="blue")
        storage = JSONStorage(storage_path)
        sessions = storage.load_all_sessions()
        console.print(f"✅ 加载了 {len(sessions)} 个会话", style="green")
    else:
        console.print(f"❌ 未找到存储文件：{storage_path}", style="red")
        console.print("💡 请先运行以下命令生成数据：", style="yellow")
        console.print("   python scripts/demo_parser.py")
        console.print("   或")
        console.print("   python scripts/simple_cli.py parse history -o data/parsed_sessions.json")
        return
    
    if not sessions:
        console.print("❌ 没有找到有效的会话数据", style="red")
        return
    
    console.print()
    
    # 按日期和时间分组问题
    daily_questions = group_questions_by_date_and_time(sessions)
    
    # 显示思维日记
    print_daily_insights(daily_questions)
    
    # 保存 JSON 文件
    output_file = "data/daily_insights.json"
    os.makedirs("data", exist_ok=True)
    save_daily_insights_json(daily_questions, output_file)


if __name__ == "__main__":
    main()