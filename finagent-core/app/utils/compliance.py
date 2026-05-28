class ComplianceChecker:
    """金融合规词库检查"""

    DEFAULT_BLOCK_WORDS = [
        "保证收益",
        "绝对安全",
        "稳赚不赔",
        "收益率",
        "年化收益",
        "本金无忧",
        "零风险",
    ]

    def __init__(self, block_words: list[str] = None):
        self.block_words = set(block_words or self.DEFAULT_BLOCK_WORDS)

    def check(self, text: str) -> tuple[bool, list[str]]:
        """检查文本是否包含合规词"""
        found = []
        for word in self.block_words:
            if word in text:
                found.append(word)
        return len(found) > 0, found

    def replace(self, text: str, replacement: str = "[合规提示]") -> str:
        """替换合规词为提示语"""
        result = text
        for word in self.block_words:
            result = result.replace(word, replacement)
        return result