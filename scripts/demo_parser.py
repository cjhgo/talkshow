#!/usr/bin/env python3
"""
Demo script to test TalkShow parsing functionality.

This script demonstrates how to:
1. Parse MD files from history directory
2. Generate summaries
3. Store data in JSON format
4. Display basic statistics
"""

import sys
import os
from pathlib import Path

# Add the parent directory to path so we can import talkshow
sys.path.insert(0, str(Path(__file__).parent.parent))

from talkshow.parser.md_parser import MDParser
from talkshow.storage.json_storage import JSONStorage
from talkshow.summarizer.rule_summarizer import RuleSummarizer


def main():
    """Main demo function."""
    print("🎭 TalkShow Demo - Chat History Analyzer")
    print("=" * 50)
    
    # Configuration
    history_dir = "history"
    storage_path = "data/parsed_sessions.json"
    
    # Check if history directory exists
    if not Path(history_dir).exists():
        print(f"❌ History directory '{history_dir}' not found!")
        print("Please make sure you're running this script from the project root.")
        return 1
    
    # Initialize components
    print("🔧 Initializing components...")
    parser = MDParser()
    storage = JSONStorage(storage_path)
    summarizer = RuleSummarizer()
    
    # Parse all MD files
    print(f"📁 Parsing files from '{history_dir}' directory...")
    sessions = parser.parse_directory(history_dir)
    
    if not sessions:
        print("❌ No valid sessions found!")
        return 1
    
    print(f"✅ Found {len(sessions)} valid chat sessions")
    
    # Generate summaries
    print("📝 Generating summaries...")
    for session in sessions:
        for qa_pair in session.qa_pairs:
            q_summary, a_summary = summarizer.summarize_both(
                qa_pair.question, qa_pair.answer
            )
            qa_pair.question_summary = q_summary
            qa_pair.answer_summary = a_summary
    
    # Save to storage
    print(f"💾 Saving sessions to '{storage_path}'...")
    if storage.save_sessions(sessions):
        print("✅ Sessions saved successfully!")
    else:
        print("❌ Failed to save sessions!")
        return 1
    
    # Display statistics
    print("\n📊 Session Statistics:")
    print("-" * 30)
    
    total_qa_pairs = sum(len(session.qa_pairs) for session in sessions)
    total_questions_with_summary = sum(
        1 for session in sessions 
        for qa in session.qa_pairs 
        if qa.question_summary
    )
    total_answers_with_summary = sum(
        1 for session in sessions 
        for qa in session.qa_pairs 
        if qa.answer_summary
    )
    
    print(f"Total sessions: {len(sessions)}")
    print(f"Total Q&A pairs: {total_qa_pairs}")
    print(f"Questions with summaries: {total_questions_with_summary}")
    print(f"Answers with summaries: {total_answers_with_summary}")
    
    # Show storage info
    print(f"\n💾 Storage Information:")
    print("-" * 30)
    info = storage.get_storage_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Display sample sessions
    print(f"\n📋 Sample Sessions (first 3):")
    print("-" * 30)
    
    for i, session in enumerate(sessions[:3]):
        print(f"\n{i+1}. {session.meta.theme}")
        print(f"   File: {session.meta.filename}")
        print(f"   Time: {session.meta.ctime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Q&A pairs: {len(session.qa_pairs)}")
        
        # Show first Q&A pair
        if session.qa_pairs:
            qa = session.qa_pairs[0]
            print(f"   First Q: {qa.get_question_display(use_summary=True)[:60]}...")
            print(f"   First A: {qa.get_answer_display(use_summary=True)[:80]}...")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"📁 Processed data saved to: {storage_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())