"""Tests for LLM summarizer functionality."""

import os
import pytest
from unittest.mock import patch, MagicMock

from talkshow.summarizer.llm_summarizer import LLMSummarizer
from talkshow.config.config_manager import ConfigManager


class TestLLMSummarizer:
    """Test LLMSummarizer functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration manager."""
        config = {
            'summarizer': {
                'llm': {
                    'provider': 'moonshot',
                    'model': 'moonshot/kimi-k2-0711-preview',
                    'api_base': 'https://api.moonshot.cn/v1',
                    'max_tokens': 150,
                    'temperature': 0.3,
                    'api_key': 'test-api-key'
                }
            }
        }
        
        config_manager = MagicMock(spec=ConfigManager)
        config_manager.get_llm_config.return_value = config['summarizer']['llm']
        
        return config_manager
    
    @pytest.fixture
    def summarizer(self, mock_config):
        """Create LLMSummarizer instance with mock config."""
        return LLMSummarizer(config_manager=mock_config)
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        config_manager = MagicMock(spec=ConfigManager)
        config_manager.get_llm_config.return_value = {'model': 'test-model'}
        
        with pytest.raises(ValueError, match="LLM API key not found"):
            LLMSummarizer(config_manager=config_manager)
    
    def test_short_question_no_summary(self, summarizer):
        """Test that short questions don't get summarized."""
        short_question = "Hello"
        result = summarizer.summarize_question(short_question)
        assert result is None
    
    def test_short_answer_no_summary(self, summarizer):
        """Test that short answers don't get summarized."""
        short_answer = "Yes"
        result = summarizer.summarize_answer(short_answer)
        assert result is None
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_question_summarization_success(self, mock_completion, summarizer):
        """Test successful question summarization."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "如何实现功能？"
        mock_completion.return_value = mock_response
        
        long_question = "请问在Python中如何实现一个复杂的功能，需要考虑哪些方面的问题？"
        result = summarizer.summarize_question(long_question)
        
        assert result == "如何实现功能？"
        mock_completion.assert_called_once()
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_answer_summarization_success(self, mock_completion, summarizer):
        """Test successful answer summarization."""
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "需要考虑架构设计、错误处理、性能优化等方面。"
        mock_completion.return_value = mock_response
        
        long_answer = "实现复杂功能需要考虑很多方面，包括架构设计、错误处理、性能优化、可维护性等。具体来说，首先要进行需求分析，明确功能要求和技术约束，然后进行系统设计，包括模块划分和接口定义，接着是编码实现，需要遵循编程规范和最佳实践，最后是测试和部署，确保系统稳定运行。"
        result = summarizer.summarize_answer(long_answer)
        
        assert result == "需要考虑架构设计、错误处理、性能优化等方面。"
        mock_completion.assert_called_once()
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_llm_call_failure(self, mock_completion, summarizer):
        """Test LLM call failure handling."""
        # Mock LLM failure
        mock_completion.side_effect = Exception("API Error")
        
        long_question = "这是一个很长的问题，需要进行摘要处理"
        result = summarizer.summarize_question(long_question)
        
        assert result is None
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_summarize_both(self, mock_completion, summarizer):
        """Test summarizing both question and answer."""
        # Mock LLM responses
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "摘要内容"
        mock_completion.return_value = mock_response
        
        question = "这是一个需要摘要的长问题，包含很多细节信息"
        answer = "这是一个详细的回答，包含了多个方面的解释和说明，需要进行摘要处理以便更好地展示给用户。回答涵盖了技术实现细节、最佳实践建议、常见问题解决方案等内容，具有较高的参考价值。"
        
        q_summary, a_summary = summarizer.summarize_both(question, answer)
        
        assert q_summary == "摘要内容"
        assert a_summary == "摘要内容"
        assert mock_completion.call_count == 2
    
    def test_get_usage_info(self, summarizer):
        """Test getting usage information."""
        info = summarizer.get_usage_info()
        
        assert 'provider' in info
        assert 'model' in info
        assert 'api_base' in info
        assert 'max_tokens' in info
        assert 'temperature' in info
        assert 'api_key_configured' in info
        assert info['api_key_configured'] is True
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_connection_test_success(self, mock_completion, summarizer):
        """Test successful connection test."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "你好！"
        mock_completion.return_value = mock_response
        
        result = summarizer.test_connection()
        assert result is True
    
    @patch('talkshow.summarizer.llm_summarizer.completion')
    def test_connection_test_failure(self, mock_completion, summarizer):
        """Test failed connection test."""
        mock_completion.side_effect = Exception("Connection failed")
        
        result = summarizer.test_connection()
        assert result is False
    
    def test_create_prompts(self, summarizer):
        """Test prompt creation methods."""
        question = "测试问题"
        answer = "测试回答"
        
        q_prompt = summarizer._create_question_prompt(question)
        a_prompt = summarizer._create_answer_prompt(answer)
        
        assert "测试问题" in q_prompt
        assert "20个字符" in q_prompt
        assert "测试回答" in a_prompt
        assert "80个字符" in a_prompt