"""Configuration management for auto-commiter.

Handles API key loading and environment configuration.
"""

import os
from pathlib import Path
from dotenv import load_dotenv, set_key, find_dotenv

# Load environment variables from .env files
load_dotenv()


def get_openai_api_key() -> str:
    """Get OpenAI API key from environment or prompt user.
    
    Checks in order:
    1. OPENAI_API_KEY environment variable
    2. .env file in current directory
    3. Prompts user to enter key
    
    Returns:
        The API key string
        
    Raises:
        ValueError: If no API key provided
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key.strip()

    # Try to find in home directory
    home_env = Path.home() / ".autocommit" / ".env"
    if home_env.exists():
        from dotenv import dotenv_values
        values = dotenv_values(home_env)
        if "OPENAI_API_KEY" in values:
            return values["OPENAI_API_KEY"].strip()

    # Prompt user for API key
    print("\n" + "=" * 50)
    print("OpenAI API Key Required")
    print("=" * 50)
    print("\nThe OpenAI model requires an API key.")
    print("Get one at: https://platform.openai.com/api-keys\n")
    
    api_key = input("Enter your OpenAI API key (or 'q' to cancel): ").strip()
    
    if not api_key or api_key.lower() == "q":
        raise ValueError("No API key provided. Use --model rule-based for offline mode.")

    # Save the key
    env_path = find_dotenv()
    if not env_path:
        # Create in home directory
        home_dir = Path.home() / ".autocommit"
        home_dir.mkdir(parents=True, exist_ok=True)
        env_path = home_dir / ".env"
        env_path.write_text(f"OPENAI_API_KEY={api_key}\n")
    else:
        set_key(env_path, "OPENAI_API_KEY", api_key)

    print("✅ API key saved for future use.\n")
    return api_key


def get_default_style() -> str:
    """Get default commit style from environment.
    
    Returns:
        The style string (defaults to 'conventional')
    """
    style = os.getenv("DEFAULT_STYLE")
    if style:
        return style.strip()
    return "conventional"


# Note: We no longer auto-call get_openai_api_key() at import time
# This allows the tool to work without an API key when using rule-based model
