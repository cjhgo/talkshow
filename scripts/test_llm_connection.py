#!/usr/bin/env python3
"""
Test script to debug LLM connection issues.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to path so we can import talkshow
sys.path.insert(0, str(Path(__file__).parent.parent))

from talkshow import ConfigManager, LLMSummarizer


def main():
    """Test LLM connection with debugging."""
    print("🧪 Testing LLM Connection")
    print("=" * 40)
    
    # Set API key
    api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # os.environ["LLM_MODEL"] = "moonshot/kimi-k2-0711-preview"
    os.environ["MOONSHOT_API_KEY"] = api_key
    print(f"✓ API Key set: {api_key[:10]}...")
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Get current LLM config
    llm_config = config_manager.get("summarizer.llm", {})
    
    print("\n📋 LLM Configuration:")
    for key, value in llm_config.items():
        if key == 'api_key':
            print(f"  {key}: {value[:10]}...{value[-4:] if value else 'None'}")
        else:
            print(f"  {key}: {value}")
    
    # Check if LLM is enabled
    llm_enabled = config_manager.get("summarizer.llm.enabled", False)
    print(f"  enabled: {llm_enabled}")
    
    # Initialize LLM summarizer
    try:
        print("\n🤖 Initializing LLM Summarizer...")
        llm_summarizer = LLMSummarizer(config_manager)
        print("✓ LLM Summarizer initialized")
        
        # Test connection
        print("\n🔗 Testing connection...")
        if llm_summarizer.test_connection():
            print("✓ Connection successful!")
            
            # Test summarization
            print("\n📝 Testing summarization...")
            test_text = """
越是亲密的人越不应该去伤害。对待亲密的人理应比对待外人更和善、更有耐心。
尤其是男女朋友/夫妻之间，双方本就不是必须在一起。每一次对对方的伤害都是在把对方推离自己。伤害到一定程度，对方就离开了。亲密关系也就毁灭了。
那么话说回来，我们当然希望亲密的人能够提供一些情绪价值，帮助我们消化负面情绪。题目中这位"女朋友"只是搞错了方法。
亲密关系中的人们应该在一个战壕里解决问题，而不是通过两军对垒的方式解决问题。
通过向男朋友发脾气的方式来疏解情绪，这就是两军对垒，用对抗的方式解决问题。
那么怎么用在一个战壕里、合作地解决问题呢？
就是直接提出来，我今天碰到了个什么事，心情特别差。和亲密的人一起吐槽今天惹自己生气的那个人（当然，男朋友一定要坚定地去吐槽，不要傻乎乎地去教导女朋友她应该怎么应对，即使要做，也要在她情绪平复之后做）。还可以一起做一点让自己放松开心的事情。
            """
            print(f"Original text ({len(test_text)} chars): {test_text}")
            
            summary = llm_summarizer._summarize_text(test_text, max_length=100)
            print(f"Summary: {summary}")
            
            if summary:
                print("✓ Summarization successful!")
            else:
                print("❌ Summarization failed - returned None")
                
        else:
            print("❌ Connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()