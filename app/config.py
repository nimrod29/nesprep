"""Application settings."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from environment and .env."""

    DATABASE_URL: str = "sqlite:///./nesprep.db"

    # AWS Bedrock settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"

    WEBSOCKET_PORT: int = 9002

    # Output directory for generated Excel files
    OUTPUT_DIR: str = "./output"

    # Default template path (relative to project root)
    DEFAULT_TEMPLATE_PATH: str = "./templates/shift_template.xlsx"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def get_template_path(self) -> str:
        """Get the absolute path to the default template."""
        return os.path.abspath(self.DEFAULT_TEMPLATE_PATH)


settings = Settings()
