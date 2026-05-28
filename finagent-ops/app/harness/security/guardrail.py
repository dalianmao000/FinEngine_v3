import re
from dataclasses import dataclass
from typing import List

@dataclass
class GuardrailResult:
    is_blocked: bool
    detected_types: List[str]
    sanitized_content: str

class Guardrail:
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{4}[-.]?\d{4}\b'
    CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    ID_PATTERN = r'\b\d{15}|\d{17}[\dx]\b'

    def check_content(self, content: str) -> GuardrailResult:
        detected = []
        sanitized = content

        if re.search(self.PHONE_PATTERN, content):
            detected.append("phone_number")
            sanitized = re.sub(self.PHONE_PATTERN, "[PHONE_MASKED]", sanitized)

        if re.search(self.CARD_PATTERN, content):
            detected.append("card_number")
            sanitized = re.sub(self.CARD_PATTERN, "[CARD_MASKED]", sanitized)

        if re.search(self.ID_PATTERN, content):
            detected.append("id_number")
            sanitized = re.sub(self.ID_PATTERN, "[ID_MASKED]", sanitized)

        return GuardrailResult(
            is_blocked=len(detected) > 0,
            detected_types=detected,
            sanitized_content=sanitized,
        )