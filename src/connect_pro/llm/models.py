"""LLM model configurations for the application."""

from langchain_openai import ChatOpenAI

from connect_pro.config.settings import settings


def get_openai_llm(temperature: float = 0) -> ChatOpenAI:
    """
    Get configured OpenAI LLM instance.

    Args:
        temperature: Controls randomness in the output (0.0 to 1.0)

    Returns:
        Configured ChatOpenAI instance
    """
    return ChatOpenAI(model=settings.OPENAI_MODEL_NAME, temperature=temperature)
