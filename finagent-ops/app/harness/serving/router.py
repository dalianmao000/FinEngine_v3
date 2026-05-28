from enum import Enum
from app.core.token_counter import count_tokens_from_text

class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Router:
    LOW_COMPLEXITY_THRESHOLD = 10
    HIGH_COMPLEXITY_THRESHOLD = 15

    def __init__(self):
        self.low_model = "qwen-7b"
        self.high_model = "qwen-72b"

    def classify_complexity(self, prompt: str) -> ComplexityLevel:
        """Classify prompt complexity based on token count and keywords"""
        token_count = count_tokens_from_text(prompt)

        if token_count < self.LOW_COMPLEXITY_THRESHOLD:
            return ComplexityLevel.LOW
        elif token_count > self.HIGH_COMPLEXITY_THRESHOLD:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.MEDIUM

    def route_model(self, complexity: ComplexityLevel) -> str:
        """Route to appropriate model based on complexity"""
        if complexity == ComplexityLevel.LOW:
            return self.low_model
        elif complexity == ComplexityLevel.MEDIUM:
            return self.low_model
        else:
            return self.high_model