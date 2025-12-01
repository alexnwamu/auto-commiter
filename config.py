import os
from dotenv import load_dotenv, set_key, find_dotenv

load_dotenv()


def get_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key.strip()

    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        raise ValueError("No API key provided. Cannot continue.")

    env_path = find_dotenv()
    if not env_path:
        env_path = ".env"
        with open(env_path, "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
    else:
        set_key(env_path, "OPENAI_API_KEY", api_key)

    print("API key saved for future use.")
    return api_key


def get_default_style() -> str:
    style = os.getenv("DEFAULT_STYLE")
    if style:
        return style.strip()
    style = input("Enter your default style: ").strip()
    if not style:
        raise ValueError("No style provided. Cannot continue.")
    env_path = find_dotenv()
    if not env_path:
        env_path = ".env"
        with open(env_path, "w") as f:
            f.write(f"DEFAULT_STYLE={style}\n")
    else:
        set_key(env_path, "DEFAULT_STYLE", style)
    print("Style saved for future use.")
    return style


OPENAI_API_KEY = get_openai_api_key()
