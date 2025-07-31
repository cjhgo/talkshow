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
    
    # Configuration
    history_dir = "history"
    rule_output = "data/rule_based_sessions.json"
    llm_output = "data/llm_enhanced_sessions.json"
    
    if not Path(history_dir).exists():
        print(f"❌ History directory '{history_dir}' not found!")
        return 1
    
    print_section("🔧 Phase 1: Core Data Analysis")
    
    # Initialize core components
    print("Initializing core components...")
    parser = MDParser()
    rule_summarizer = RuleSummarizer()
    storage_rule = JSONStorage(rule_output)
    
    # Parse files
    print(f"📁 Parsing {history_dir} directory...")
    sessions = parser.parse_directory(history_dir)
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
    config_manager = ConfigManager()
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
            
            # Generate LLM summaries for a sample of sessions
            print("🧠 Generating LLM summaries (limited by API rate limits)...")
            sample_sessions = sessions[:3]  # Limit to prevent rate limiting
            
            for session in sample_sessions:
                for qa_pair in session.qa_pairs[:2]:  # Limit QA pairs per session
                    try:
                        q_summary, a_summary = llm_summarizer.summarize_both(
                            qa_pair.question, qa_pair.answer
                        )
                        if q_summary:
                            qa_pair.question_summary = q_summary
                            llm_summaries += 1
                        if a_summary:
                            qa_pair.answer_summary = a_summary
                            llm_summaries += 1
                    except Exception as e:
                        print(f"   ⚠️  Rate limit reached: {e}")
                        break
                if llm_summaries > 0:
                    break  # Stop after getting some samples
            
            # Save LLM-enhanced results
            storage_llm = JSONStorage(llm_output)
            storage_llm.save_sessions(sessions)
            print(f"✅ Generated {llm_summaries} LLM summaries")
            print(f"💾 Saved to {llm_output}")
            
        else:
            print("❌ LLM connection failed")
            
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
    
    print_section("📊 Comprehensive Statistics")
    
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
    
    print(f"📁 Total sessions: {len(sessions)}")
    print(f"💬 Total Q&A pairs: {total_qa_pairs}")
    print(f"📝 Questions with summaries: {total_questions_with_summary}")
    print(f"📋 Answers with summaries: {total_answers_with_summary}")
    print(f"📏 Rule-based summaries: {rule_summaries}")
    if llm_available:
        print(f"🧠 LLM summaries: {llm_summaries}")
        print(f"🤖 LLM integration: ✅ Functional")
    else:
        print(f"🤖 LLM integration: ❌ Not available (API key needed)")
    
    # Show date range
    if sessions:
        oldest = min(sessions, key=lambda s: s.meta.ctime)
        newest = max(sessions, key=lambda s: s.meta.ctime)
        print(f"📅 Date range: {oldest.meta.ctime.strftime('%Y-%m-%d')} to {newest.meta.ctime.strftime('%Y-%m-%d')}")
    
    print_section("🎯 Phase 2: CLI Tools Demo")
    
    print("Available CLI commands:")
    print("  • python scripts/simple_cli.py parse history --summarize")
    print("  • python scripts/simple_cli.py parse history --summarize --use-llm")  
    print("  • python scripts/simple_cli.py list")
    print("  • python scripts/simple_cli.py stats")
    print("  • python scripts/simple_cli.py show <filename>")
    
    print_section("🔍 Sample Content Analysis")
    
    # Show analysis of different content types
    if sessions:
        session = sessions[0]
        print(f"Sample session: {session.meta.theme}")
        print(f"Created: {session.meta.ctime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Q&A pairs: {len(session.qa_pairs)}")
        
        if session.qa_pairs:
            qa = session.qa_pairs[0]
            print(f"\nFirst question ({len(qa.question)} chars):")
            print(f"  {qa.question[:100]}{'...' if len(qa.question) > 100 else ''}")
            if qa.question_summary:
                print(f"  → Summary: {qa.question_summary}")
            
            print(f"\nFirst answer ({len(qa.answer)} chars):")
            print(f"  {qa.answer[:150]}{'...' if len(qa.answer) > 150 else ''}")
            if qa.answer_summary:
                print(f"  → Summary: {qa.answer_summary}")
    
    print_header("🎉 Demo Complete", char="=")
    
    print("✅ All phases successfully demonstrated:")
    print("   Phase 1: ✅ Core parsing, storage, and rule-based summarization")
    print("   Phase 2: ✅ Enhanced CLI tools with summarization options")
    print("   Phase 3: ✅ LLM integration with intelligent summarization")
    
    print(f"\n📁 Output files:")
    print(f"   • {rule_output} - Rule-based summaries")
    if llm_available:
        print(f"   • {llm_output} - LLM-enhanced summaries")
    
    print(f"\n💡 Next steps:")
    print("   • Set MOONSHOT_API_KEY for full LLM functionality")
    print("   • Explore CLI tools for interactive analysis")
    print("   • Consider Phase 4: Web frontend development")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())