"""PII (Personally Identifiable Information) redaction functions."""

import re
from typing import Dict, List, Tuple


# PII patterns: (regex pattern, type name, replacement mask)
PII_PATTERNS: List[Tuple[str, str, str]] = [
    (r"1[3-9]\d{9}", "PHONE", "[PHONE_001]"),
    (r"6[0-9]{14,16}", "CARD", "[CARD_001]"),
    (r"\d{17}[\dXx]", "ID", "[ID_001]"),
]


def _mask_phone(text: str, match: re.Match) -> str:
    """Mask phone number showing first 3 and last 4 digits."""
    phone = match.group()
    if len(phone) == 11:
        return f"{phone[:3]}****{phone[-4:]}"
    return "[PHONE_001]"


def _mask_card(text: str, match: re.Match) -> str:
    """Mask card number showing first 4 and last 4 digits.

    The regex may match only part of the full card number (e.g., 17 digits
    from a 19-digit number due to overlap with ID pattern). In such cases,
    we search for the full card number in the text and mask all 16+ digits.
    """
    card = match.group()
    # Check if there are more digits of this card number in the text
    # after the matched portion (for overlapping cases like 6222021234567890123)
    card_start = match.start()
    card_end = match.end()

    # Look ahead to find if there are more card digits immediately after
    # the matched portion that belong to this card
    remaining_text = text[card_end:]
    full_card_digits = ""
    if remaining_text and remaining_text[0].isdigit():
        # Collect all consecutive digits after the match
        for ch in remaining_text:
            if ch.isdigit():
                full_card_digits += ch
            else:
                break

    if full_card_digits:
        # Found additional digits - combine them with matched portion
        # to get the full card number, keeping first 4 + last 4 of full card
        full_card = card + full_card_digits
        if len(full_card) >= 8:
            return f"{full_card[:4]}****{full_card[-4:]}"

    # Standard case: mask the matched portion
    if len(card) >= 8:
        return f"{card[:4]}****{card[-4:]}"
    return "[CARD_001]"


def _mask_id(text: str, match: re.Match) -> str:
    """Mask ID number showing first 6 and last 4 digits."""
    id_num = match.group()
    if len(id_num) >= 10:
        return f"{id_num[:6]}****{id_num[-4:]}"
    return "[ID_001]"


def redact_pii(text: str) -> str:
    """
    Redact PII (Personally Identifiable Information) from text.

    Uses regex to find and mask PII patterns:
    - Phone numbers: 1[3-9]\\d{9} → 138****5678
    - Card numbers: 6[0-9]{14,16} → 6222****7890
    - ID numbers: \\d{17}[\\dXx] → 110101****1234

    Args:
        text: Input text that may contain PII

    Returns:
        Text with PII patterns replaced with masked versions
    """
    result = text

    # Process in order that avoids regex overlap issues:
    # ID (18 digits) must be processed before phone (11 digits) to avoid
    # phone pattern consuming part of an ID number

    # Mask ID numbers first
    id_pattern = PII_PATTERNS[2][0]
    result = re.sub(id_pattern, lambda m: _mask_id(result, m), result)

    # Mask card numbers second
    card_pattern = PII_PATTERNS[1][0]
    result = re.sub(card_pattern, lambda m: _mask_card(result, m), result)

    # Mask phone numbers last
    phone_pattern = PII_PATTERNS[0][0]
    result = re.sub(phone_pattern, lambda m: _mask_phone(result, m), result)

    return result


def check_pii_present(text: str) -> Dict[str, bool]:
    """
    Check which types of PII are present in the text.

    Args:
        text: Input text to check for PII

    Returns:
        Dict with keys "PHONE", "CARD", "ID" indicating which PII types are present
    """
    return {
        "PHONE": bool(re.search(PII_PATTERNS[0][0], text)),
        "CARD": bool(re.search(PII_PATTERNS[1][0], text)),
        "ID": bool(re.search(PII_PATTERNS[2][0], text)),
    }