#!/usr/bin/env python3
"""
Advanced demo script for TalkShow with LLM integration.

This script demonstrates:
1. Configuration management
2. LLM-based summarization 
3. Comparison between rule-based and LLM summarization
4. Advanced statistics and analysis
"""

import sys
import os
from pathlib import Path

# Add the parent directory to path so we can import talkshow
sys.path.insert(0, str(Path(__file__).parent.parent))

from talkshow import (
    MDParser, JSONStorage, RuleSummarizer, LLMSummarizer, ConfigManager
)


def main():
    """Main advanced demo function."""
    print("🎭 TalkShow Advanced Demo - LLM-Enhanced Chat History Analyzer")
    print("=" * 70)
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    history_dir = config_manager.get_history_dir()
    storage_path = config_manager.get_data_file_path()
    
    # Check if history directory exists
    if not history_dir.exists():
        print(f"❌ History directory '{history_dir}' not found!")
        return 1
    
    # Initialize components
    print("🔧 Initializing components...")
    parser = MDParser()
    storage = JSONStorage(str(storage_path))
    rule_summarizer = RuleSummarizer()
    
    # Test LLM configuration
    print("🤖 Testing LLM integration...")
    try:
        llm_summarizer = LLMSummarizer(config_manager)
        llm_info = llm_summarizer.get_usage_info()
        
        print(f"   Provider: {llm_info['provider']}")
        print(f"   Model: {llm_info['model']}")
        print(f"   API Key: {'✅ Configured' if llm_info['api_key_configured'] else '❌ Missing'}")
        
        if llm_info['api_key_configured']:
            print("   Testing connection...")
            if llm_summarizer.test_connection():
                print("   ✅ LLM connection successful!")
                use_llm = True
            else:
                print("   ❌ LLM connection failed, falling back to rule-based summarization")
                use_llm = False
        else:
            print("   ❌ No API key found, using rule-based summarization only")
            use_llm = False
            llm_summarizer = None
    
    except Exception as e:
        print(f"   ❌ LLM initialization failed: {e}")
        print("   Using rule-based summarization only")
        use_llm = False
        llm_summarizer = None
    
    # Parse files
    print(f"📁 Parsing files from '{history_dir}' directory...")
    sessions = parser.parse_directory(str(history_dir))
    
    if not sessions:
        print("❌ No valid sessions found!")
        return 1
    
    print(f"✅ Found {len(sessions)} valid chat sessions")
    
    # Generate summaries
    print("📝 Generating summaries...")
    rule_summaries = 0
    llm_summaries = 0
    
    for i, session in enumerate(sessions):
        print(f"   Processing session {i+1}/{len(sessions)}: {session.meta.theme[:50]}...")
        
        for qa_pair in session.qa_pairs:
            # Always generate rule-based summaries
            rule_q_summary, rule_a_summary = rule_summarizer.summarize_both(
                qa_pair.question, qa_pair.answer
            )
            
            if rule_q_summary:
                rule_summaries += 1
            if rule_a_summary:
                rule_summaries += 1
            
            # Try LLM summarization if available
            if use_llm and llm_summarizer:
                try:
                    llm_q_summary, llm_a_summary = llm_summarizer.summarize_both(
                        qa_pair.question, qa_pair.answer
                    )
                    
                    if llm_q_summary:
                        qa_pair.question_summary = llm_q_summary
                        llm_summaries += 1
                    else:
                        qa_pair.question_summary = rule_q_summary
                    
                    if llm_a_summary:
                        qa_pair.answer_summary = llm_a_summary
                        llm_summaries += 1
                    else:
                        qa_pair.answer_summary = rule_a_summary
                        
                except Exception as e:
                    print(f"      ⚠️  LLM summarization failed for session {i+1}: {e}")
                    # Fallback to rule-based summaries
                    qa_pair.question_summary = rule_q_summary
                    qa_pair.answer_summary = rule_a_summary
            else:
                # Use rule-based summaries only
                qa_pair.question_summary = rule_q_summary
                qa_pair.answer_summary = rule_a_summary
    
    # Save to storage
    print(f"💾 Saving sessions to '{storage_path}'...")
    if storage.save_sessions(sessions):
        print("✅ Sessions saved successfully!")
    else:
        print("❌ Failed to save sessions!")
        return 1
    
    # Display advanced statistics
    print("\n📊 Advanced Statistics:")
    print("-" * 40)
    
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
    print(f"Rule-based summaries: {rule_summaries}")
    print(f"LLM summaries: {llm_summaries}")
    print(f"Questions with summaries: {total_questions_with_summary}")
    print(f"Answers with summaries: {total_answers_with_summary}")
    
    if use_llm:
        llm_percentage = (llm_summaries / (rule_summaries + llm_summaries)) * 100 if (rule_summaries + llm_summaries) > 0 else 0
        print(f"LLM summary success rate: {llm_percentage:.1f}%")
    
    # Show storage info
    print(f"\n💾 Storage Information:")
    print("-" * 30)
    info = storage.get_storage_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    # Display sample sessions with comparison
    print(f"\n📋 Sample Sessions with Summary Comparison:")
    print("-" * 50)
    
    for i, session in enumerate(sessions[:2]):
        print(f"\n{i+1}. {session.meta.theme}")
        print(f"   File: {session.meta.filename}")
        print(f"   Time: {session.meta.ctime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Q&A pairs: {len(session.qa_pairs)}")
        
        # Show first Q&A pair with summaries
        if session.qa_pairs:
            qa = session.qa_pairs[0]
            print(f"   First Q: {qa.question[:60]}...")
            if qa.question_summary:
                print(f"   Q Summary: {qa.question_summary}")
            print(f"   First A: {qa.answer[:80]}...")
            if qa.answer_summary:
                print(f"   A Summary: {qa.answer_summary}")
    
    print(f"\n🎉 Advanced demo completed successfully!")
    print(f"📁 Processed data saved to: {storage_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())