"""LLM-based text summarization using LiteLLM."""

import os
from typing import Optional, Dict, Any
import litellm
from litellm import completion

from ..config.config_manager import ConfigManager


class LLMSummarizer:
    """LLM-based text summarizer using various LLM providers."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize LLM summarizer.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config_manager = config_manager or ConfigManager()
        self.llm_config = self.config_manager.get_llm_config()
        
        # Validate configuration
        if not self.llm_config.get('api_key'):
            raise ValueError(
                "LLM API key not found. Please set MOONSHOT_API_KEY environment variable "
                "or configure api_key in config file."
            )
    
    def summarize_question(self, question: str) -> Optional[str]:
        """Summarize a question using LLM.
        
        Args:
            question: The question text to summarize
            
        Returns:
            Summarized question or None if summarization fails
        """
        if not question or len(question) <= 20:
            return None
        
        prompt = self._create_question_prompt(question)
        return self._call_llm(prompt, max_tokens=30)
    
    def summarize_answer(self, answer: str) -> Optional[str]:
        """Summarize an answer using LLM.
        
        Args:
            answer: The answer text to summarize
            
        Returns:
            Summarized answer or None if summarization fails
        """
        if not answer or len(answer.strip()) <= 80:
            return None
        
        prompt = self._create_answer_prompt(answer)
        return self._call_llm(prompt, max_tokens=100)
    
    def summarize_both(self, question: str, answer: str) -> tuple:
        """Summarize both question and answer.
        
        Args:
            question: The question text
            answer: The answer text
            
        Returns:
            tuple: (question_summary, answer_summary)
        """
        question_summary = self.summarize_question(question)
        answer_summary = self.summarize_answer(answer)
        return question_summary, answer_summary
    
    def _create_question_prompt(self, question: str) -> str:
        """Create prompt for question summarization."""
        return f"""请将以下问题简化为不超过20个字符的核心要点，保持原意：

问题：{question}

简化后的问题（不超过20字符）："""
    
    def _create_answer_prompt(self, answer: str) -> str:
        """Create prompt for answer summarization."""
        return f"""请将以下回答总结为不超过80个字符的要点，突出关键信息和解决方案
                (如果内容超过100个字符,总结则不要少于 20个字符)：

回答：{answer}

总结（不超过80字符）："""
    
    def _call_llm(self, prompt: str, max_tokens: int = 150) -> Optional[str]:
        """Call LLM API with the given prompt.
        
        Args:
            prompt: The prompt to send to LLM
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response text or None if call fails
        """
        try:
            messages = [{"content": prompt, "role": "user"}]
            
            response = completion(
                model=self.llm_config.get('model', 'moonshot/kimi-k2-0711-preview'),
                messages=messages,
                api_base=self.llm_config.get('api_base', 'https://api.moonshot.cn/v1'),
                api_key=self.llm_config['api_key'],
                max_tokens=min(max_tokens, self.llm_config.get('max_tokens', 150)),
                temperature=self.llm_config.get('temperature', 0.3)
            )

            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM summarization failed: {e}")
            return None
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get information about LLM usage configuration."""
        return {
            'provider': self.llm_config.get('provider', 'unknown'),
            'model': self.llm_config.get('model', 'unknown'),
            'api_base': self.llm_config.get('api_base', 'unknown'),
            'max_tokens': self.llm_config.get('max_tokens', 150),
            'temperature': self.llm_config.get('temperature', 0.3),
            'api_key_configured': bool(self.llm_config.get('api_key'))
        }
    
    def test_connection(self) -> bool:
        """Test LLM connection with a simple prompt.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_prompt = "请回答：你好"
            response = self._call_llm(test_prompt, max_tokens=20)
            return response is not None and len(response.strip()) > 0
        except Exception:
            return False