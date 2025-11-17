"""
LLM module for Multi-Agent System.

Provides unified interface for different LLM providers:
- Ollama (local models)
- OpenAI (GPT models)
- Groq (fast inference)
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with messages."""
        pass


class OllamaLLM(BaseLLM):
    """Ollama LLM implementation."""

    def __init__(self, base_url: str, model: str):
        """
        Initialize Ollama LLM.

        Args:
            base_url: Ollama server URL
            model: Model name (e.g., "llama3.2:1b")
        """
        self.base_url = base_url
        self.model = model

        try:
            import ollama
            self.client = ollama.Client(host=base_url)
            logger.info(f"Ollama client initialized: {model} @ {base_url}")
        except ImportError:
            raise ImportError("ollama package not installed. Run: pip install ollama")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                **kwargs
            )
            return response['response']
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with messages."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise


class OpenAILLM(BaseLLM):
    """OpenAI LLM implementation."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        """
        Initialize OpenAI LLM.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., "gpt-4-turbo-preview")
            temperature: Sampling temperature
        """
        self.model = model
        self.temperature = temperature

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            logger.info(f"OpenAI client initialized: {model}")
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        return self.chat([{"role": "user", "content": prompt}], **kwargs)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with messages."""
        try:
            temperature = kwargs.pop('temperature', self.temperature)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise


class GroqLLM(BaseLLM):
    """Groq LLM implementation."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.7):
        """
        Initialize Groq LLM.

        Args:
            api_key: Groq API key
            model: Model name (e.g., "llama-3.1-70b-versatile")
            temperature: Sampling temperature
        """
        self.model = model
        self.temperature = temperature

        try:
            from groq import Groq
            self.client = Groq(api_key=api_key)
            logger.info(f"Groq client initialized: {model}")
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        return self.chat([{"role": "user", "content": prompt}], **kwargs)

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion with messages."""
        try:
            temperature = kwargs.pop('temperature', self.temperature)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            raise


class LLMFactory:
    """Factory for creating LLM instances."""

    @staticmethod
    def create_llm(config) -> BaseLLM:
        """
        Create LLM instance based on configuration.

        Args:
            config: Config object with LLM settings

        Returns:
            BaseLLM instance

        Raises:
            ValueError: If provider is not supported
        """
        provider = config.llm.provider

        if provider == "ollama":
            return OllamaLLM(
                base_url=config.llm.ollama_base_url,
                model=config.llm.ollama_model
            )
        elif provider == "openai":
            return OpenAILLM(
                api_key=config.llm.openai_api_key,
                model=config.llm.openai_model,
                temperature=config.llm.openai_temperature
            )
        elif provider == "groq":
            return GroqLLM(
                api_key=config.llm.groq_api_key,
                model=config.llm.groq_model,
                temperature=config.llm.groq_temperature
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")


# Global LLM instance (singleton pattern)
_llm_instance: Optional[BaseLLM] = None


def get_llm(config=None) -> BaseLLM:
    """
    Get global LLM instance.

    Args:
        config: Config object (required for first call)

    Returns:
        BaseLLM instance

    Raises:
        RuntimeError: If config is not provided on first call
    """
    global _llm_instance

    if _llm_instance is None:
        if config is None:
            raise RuntimeError("Config must be provided for first LLM initialization")
        _llm_instance = LLMFactory.create_llm(config)

    return _llm_instance


def reset_llm():
    """Reset global LLM instance (useful for testing)."""
    global _llm_instance
    _llm_instance = None
