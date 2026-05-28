from typing import Any
import jsonschema


class SchemaValidator:
    """工具入参校验"""

    @staticmethod
    def validate(parameters: dict, schema: dict) -> tuple[bool, str]:
        try:
            jsonschema.validate(instance=parameters, schema=schema)
            return True, ""
        except jsonschema.ValidationError as e:
            return False, str(e.message)
        except jsonschema.SchemaError as e:
            return False, f"Invalid schema: {e.message}"