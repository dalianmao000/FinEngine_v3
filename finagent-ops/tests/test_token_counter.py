import tiktoken
from app.core.token_counter import count_tokens, count_tokens_from_text

def test_count_tokens_with_encoding():
    encoding = tiktoken.get_encoding("cl100k_base")
    text = "Hello, world!"
    tokens = count_tokens(text, encoding)
    assert tokens > 0

def test_count_tokens_from_text():
    count = count_tokens_from_text("Hello, world!")
    assert count > 0