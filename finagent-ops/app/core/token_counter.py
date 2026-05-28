import tiktoken

def count_tokens(text: str, encoding) -> int:
    """Count tokens in text using given encoding"""
    return len(encoding.encode(text))

def count_tokens_from_text(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens from text string"""
    encoding = tiktoken.get_encoding(encoding_name)
    return count_tokens(text, encoding)

def get_encoding(encoding_name: str = "cl100k_base"):
    """Get tiktoken encoding"""
    return tiktoken.get_encoding(encoding_name)