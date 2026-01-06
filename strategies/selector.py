# - Another function could select between different model classes
#   (OpenAIModel, HF local model, rule-based) based on the chosen


def select_style(style: str) -> str:
    style = style.lower()
    styles = [
        "conventional",
        "short",
        "verbose",
    ]
    if style in styles:
        return style
    else:
        raise ValueError(f"Invalid style: {style}")


def seelct_model(model: str) -> str:
    model = model.lower()
    models = [
        "openai",
        "huggingface",
    ]
    if model in models:
        return model
    else:
        raise ValueError(f"Invalid model: {model}")
