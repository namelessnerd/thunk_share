import tiktoken


def get_token_count(prompt_text: str, model: str) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(prompt_text))
