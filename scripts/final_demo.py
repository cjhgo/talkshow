#!/usr/bin/env python3
"""
Final comprehensive demo for TalkShow project.

This demo showcases all implemented features across Phase 1, 2, and 3:
- Phase 1: Core data analysis (parsing, storage, rule-based summarization)
- Phase 2: Enhanced CLI tools  
- Phase 3: LLM integration with intelligent summarization
"""

import sys
import os
from pathlib import Path

# Add the parent directory to path so we can import talkshow
sys.path.insert(0, str(Path(__file__).parent.parent))

from talkshow import (
    MDParser, JSONStorage, RuleSummarizer, LLMSummarizer, ConfigManager
)


def print_header(title, char="=", width=70):
    """Print a formatted header."""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")


def print_section(title, char="-", width=50):
    """Print a section header."""
    print(f"\n{title}")
    print(char * len(title))


def main():
    """Comprehensive demo of all TalkShow features."""
    print_header("🎭 TalkShow - Complete Feature Demo")
    print("A comprehensive demonstration of chat history analysis capabilities")
    print("Phases 1-3: Parsing → CLI Tools → LLM Integration")
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    history_dir = config_manager.get_history_dir()
    rule_output = config_manager.get_data_file_path()
    llm_output = config_manager.get_data_file_path()
    
    if not history_dir.exists():
        print(f"❌ History directory '{history_dir}' not found!")
        return 1
    
    print_section("🔧 Phase 1: Core Data Analysis")
    
    # Initialize core components
    print("Initializing core components...")
    parser = MDParser()
    rule_summarizer = RuleSummarizer()
    storage_rule = JSONStorage(str(rule_output))
    
    # Parse files
    print(f"📁 Parsing {history_dir} directory...")
    sessions = parser.parse_directory(str(history_dir))
    print(f"✅ Parsed {len(sessions)} chat sessions")
    
    # Generate rule-based summaries
    print("📝 Generating rule-based summaries...")
    rule_summaries = 0
    for session in sessions:
        for qa_pair in session.qa_pairs:
            q_summary, a_summary = rule_summarizer.summarize_both(
                qa_pair.question, qa_pair.answer
            )
            qa_pair.question_summary = q_summary
            qa_pair.answer_summary = a_summary
            if q_summary:
                rule_summaries += 1
            if a_summary:
                rule_summaries += 1
    
    # Save rule-based results
    storage_rule.save_sessions(sessions)
    print(f"✅ Generated {rule_summaries} rule-based summaries")
    print(f"💾 Saved to {rule_output}")
    
    print_section("🤖 Phase 3: LLM Integration")
    
    # Test LLM integration
    llm_available = False
    llm_summaries = 0
    
    try:
        llm_summarizer = LLMSummarizer(config_manager)
        llm_info = llm_summarizer.get_usage_info()
        
        print(f"Provider: {llm_info['provider']}")
        print(f"Model: {llm_info['model']}")
        print(f"API Key: {'✅ Configured' if llm_info['api_key_configured'] else '❌ Missing'}")
        
        if llm_info['api_key_configured'] and llm_summarizer.test_connection():
            print("✅ LLM connection successful!")
            llm_available = True
        else:
            print("❌ LLM connection failed or not configured")
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
    
    if llm_available:
        print("📝 Generating LLM-enhanced summaries...")
        storage_llm = JSONStorage(str(llm_output))
        
        # Create a copy of sessions for LLM processing
        llm_sessions = sessions.copy()
        
        for i, session in enumerate(llm_sessions):
            print(f"   Processing session {i+1}/{len(llm_sessions)}: {session.meta.theme[:50]}...")
            
            for qa_pair in session.qa_pairs:
                try:
                    q_summary, a_summary = llm_summarizer.summarize_both(
                        qa_pair.question, qa_pair.answer
                    )
                    qa_pair.question_summary = q_summary
                    qa_pair.answer_summary = a_summary
                    if q_summary:
                        llm_summaries += 1
                    if a_summary:
                        llm_summaries += 1
                except Exception as e:
                    print(f"      ⚠️  LLM summarization failed: {e}")
                    # Keep existing rule-based summaries
        
        # Save LLM-enhanced results
        storage_llm.save_sessions(llm_sessions)
        print(f"✅ Generated {llm_summaries} LLM-enhanced summaries")
        print(f"💾 Saved to {llm_output}")
    else:
        print("📏 Using rule-based summaries only")
        print("💡 Tip: Set MOONSHOT_API_KEY environment variable to enable LLM summaries")
    
    print_section("📊 Final Statistics")
    
    # Calculate comprehensive statistics
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
    if llm_available:
        print(f"LLM summaries: {llm_summaries}")
        llm_percentage = (llm_summaries / (rule_summaries + llm_summaries)) * 100 if (rule_summaries + llm_summaries) > 0 else 0
        print(f"LLM summary success rate: {llm_percentage:.1f}%")
    print(f"Questions with summaries: {total_questions_with_summary}")
    print(f"Answers with summaries: {total_answers_with_summary}")
    
    # Show storage info
    print(f"\n💾 Storage Information:")
    print("-" * 30)
    info = storage_rule.get_storage_info()
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
    
    print_header("🎉 Demo Completed Successfully!")
    print(f"📁 Rule-based data: {rule_output}")
    if llm_available:
        print(f"📁 LLM-enhanced data: {llm_output}")
    print("\n🚀 All TalkShow features demonstrated successfully!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())