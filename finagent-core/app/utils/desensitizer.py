import re
from typing import Optional


class Desensitizer:
    """金融级PII脱敏"""

    PATTERNS = {
        "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "ID_CARD": re.compile(r"\b\d{15}|\d{18}\b"),
        "PHONE": re.compile(r"\b1[3-9]\d{9}\b"),
        "BANK_ACCOUNT": re.compile(r"\b\d{16,19}\b"),
    }

    def redact(self, text: str) -> tuple[str, list[dict]]:
        """脱敏并返回替换记录"""
        replacements = []
        result = text

        for pii_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(result)
            for match in matches:
                masked = self._mask(pii_type, match)
                placeholder = f"[{pii_type}]"
                result = result.replace(match, placeholder, 1)
                replacements.append({
                    "type": pii_type,
                    "original": match,
                    "masked": masked,
                    "placeholder": placeholder,
                })

        return result, replacements

    def _mask(self, pii_type: str, value: str) -> str:
        if pii_type == "CREDIT_CARD":
            return f"{value[:4]}****{value[-4:]}"
        elif pii_type == "ID_CARD":
            return f"{value[:6]}******{value[-4:]}"
        elif pii_type == "PHONE":
            return f"{value[:3]}****{value[-4:]}"
        elif pii_type == "BANK_ACCOUNT":
            return f"****{value[-4:]}"
        return "***"