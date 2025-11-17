"""
Configuration module for Multi-Agent System.

Loads and validates configuration from environment variables using Pydantic.
"""

import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: Literal["ollama", "openai"] = Field(
        default="ollama",
        description="LLM provider to use"
    )

    # Ollama settings
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL"
    )
    ollama_model: str = Field(
        default="llama3.2",
        description="Ollama model name"
    )

    # OpenAI settings
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model name"
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="OpenAI temperature parameter"
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v, info):
        """Validate OpenAI API key if provider is openai."""
        if info.data.get("provider") == "openai" and not v:
            raise ValueError("OpenAI API key is required when provider is 'openai'")
        return v


class AgentConfig(BaseModel):
    """Agent system configuration."""

    max_concurrent_agents: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of concurrent agents"
    )

    agent_timeout: int = Field(
        default=300,
        ge=10,
        description="Default timeout for agent operations (seconds)"
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed tasks"
    )


class MessageBusConfig(BaseModel):
    """Message bus configuration."""

    queue_type: Literal["memory", "redis"] = Field(
        default="memory",
        description="Message queue type"
    )

    # Redis settings
    redis_host: str = Field(
        default="localhost",
        description="Redis host"
    )
    redis_port: int = Field(
        default=6379,
        ge=1,
        le=65535,
        description="Redis port"
    )
    redis_db: int = Field(
        default=0,
        ge=0,
        description="Redis database number"
    )
    redis_password: Optional[str] = Field(
        default=None,
        description="Redis password"
    )


class SharedMemoryConfig(BaseModel):
    """Shared memory configuration."""

    enable_persistence: bool = Field(
        default=False,
        description="Enable shared memory persistence"
    )

    persistence_path: Path = Field(
        default=Path("./data/shared_memory.json"),
        description="Path for persistence file"
    )


class WorkflowConfig(BaseModel):
    """Workflow configuration."""

    workflows_dir: Path = Field(
        default=Path("./workflows"),
        description="Workflow directory"
    )

    workflow_timeout: int = Field(
        default=1800,
        ge=60,
        description="Workflow execution timeout (seconds)"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Log level"
    )

    log_format: Literal["json", "console"] = Field(
        default="console",
        description="Log format"
    )

    log_file: Optional[Path] = Field(
        default=None,
        description="Log file path (None for console only)"
    )

    colored_logs: bool = Field(
        default=True,
        description="Enable colored console logs"
    )


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""

    enable_metrics: bool = Field(
        default=False,
        description="Enable Prometheus metrics"
    )

    metrics_port: int = Field(
        default=9090,
        ge=1024,
        le=65535,
        description="Prometheus metrics port"
    )


class WebToolsConfig(BaseModel):
    """Web scraping tools configuration."""

    user_agent: str = Field(
        default="Mozilla/5.0 (compatible; MultiAgentSystem/1.0)",
        description="User agent for web requests"
    )

    request_timeout: int = Field(
        default=30,
        ge=5,
        description="Request timeout (seconds)"
    )

    max_web_sources: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of web sources per research"
    )

    search_engine: Literal["duckduckgo", "google"] = Field(
        default="duckduckgo",
        description="Default search engine"
    )

    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None

    rate_limit_rpm: int = Field(
        default=60,
        ge=1,
        description="Requests per minute"
    )

    request_delay: float = Field(
        default=1.0,
        ge=0.1,
        description="Delay between requests (seconds)"
    )


class DevelopmentConfig(BaseModel):
    """Development settings."""

    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    verbose: bool = Field(
        default=False,
        description="Enable verbose logging"
    )

    test_mode: bool = Field(
        default=False,
        description="Test mode (uses mock data)"
    )


class Config(BaseModel):
    """Main configuration class."""

    llm: LLMConfig
    agent: AgentConfig
    message_bus: MessageBusConfig
    shared_memory: SharedMemoryConfig
    workflow: WorkflowConfig
    logging: LoggingConfig
    monitoring: MonitoringConfig
    web_tools: WebToolsConfig
    development: DevelopmentConfig

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        return cls(
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "ollama"),
                ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                openai_model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
                openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            ),
            agent=AgentConfig(
                max_concurrent_agents=int(os.getenv("MAX_CONCURRENT_AGENTS", "5")),
                agent_timeout=int(os.getenv("AGENT_TIMEOUT", "300")),
                max_retries=int(os.getenv("MAX_RETRIES", "3")),
            ),
            message_bus=MessageBusConfig(
                queue_type=os.getenv("MESSAGE_QUEUE_TYPE", "memory"),
                redis_host=os.getenv("REDIS_HOST", "localhost"),
                redis_port=int(os.getenv("REDIS_PORT", "6379")),
                redis_db=int(os.getenv("REDIS_DB", "0")),
                redis_password=os.getenv("REDIS_PASSWORD"),
            ),
            shared_memory=SharedMemoryConfig(
                enable_persistence=os.getenv("ENABLE_PERSISTENCE", "false").lower() == "true",
                persistence_path=Path(os.getenv("PERSISTENCE_PATH", "./data/shared_memory.json")),
            ),
            workflow=WorkflowConfig(
                workflows_dir=Path(os.getenv("WORKFLOWS_DIR", "./workflows")),
                workflow_timeout=int(os.getenv("WORKFLOW_TIMEOUT", "1800")),
            ),
            logging=LoggingConfig(
                log_level=os.getenv("LOG_LEVEL", "INFO"),
                log_format=os.getenv("LOG_FORMAT", "console"),
                log_file=Path(os.getenv("LOG_FILE")) if os.getenv("LOG_FILE") else None,
                colored_logs=os.getenv("COLORED_LOGS", "true").lower() == "true",
            ),
            monitoring=MonitoringConfig(
                enable_metrics=os.getenv("ENABLE_METRICS", "false").lower() == "true",
                metrics_port=int(os.getenv("METRICS_PORT", "9090")),
            ),
            web_tools=WebToolsConfig(
                user_agent=os.getenv("USER_AGENT", "Mozilla/5.0 (compatible; MultiAgentSystem/1.0)"),
                request_timeout=int(os.getenv("WEB_REQUEST_TIMEOUT", "30")),
                max_web_sources=int(os.getenv("MAX_WEB_SOURCES", "10")),
                search_engine=os.getenv("SEARCH_ENGINE", "duckduckgo"),
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                google_cse_id=os.getenv("GOOGLE_CSE_ID"),
                rate_limit_rpm=int(os.getenv("RATE_LIMIT_RPM", "60")),
                request_delay=float(os.getenv("REQUEST_DELAY", "1.0")),
            ),
            development=DevelopmentConfig(
                debug=os.getenv("DEBUG", "false").lower() == "true",
                verbose=os.getenv("VERBOSE", "false").lower() == "true",
                test_mode=os.getenv("TEST_MODE", "false").lower() == "true",
            ),
        )


# Global configuration instance
config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance (singleton pattern)."""
    global config
    if config is None:
        config = Config.from_env()
    return config


def reload_config() -> Config:
    """Reload configuration from environment."""
    global config
    load_dotenv(override=True)
    config = Config.from_env()
    return config


# Convenience function to get config
def cfg() -> Config:
    """Shorthand for get_config()."""
    return get_config()
