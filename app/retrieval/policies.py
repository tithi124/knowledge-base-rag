import re
from typing import Optional

# Very lightweight refusal policies for bonus points
PII_RE = re.compile(r"\b(ssn|social security|passport number|credit card|cvv|bank account)\b", re.I)
MEDICAL_RE = re.compile(r"\b(diagnose|treatment|prescription|symptoms)\b", re.I)
LEGAL_RE = re.compile(r"\b(legal advice|sue|lawsuit|contract|attorney)\b", re.I)

def policy_refusal_reason(question: str) -> Optional[str]:
    q = question.strip()
    if not q:
        return "Empty question."
    if PII_RE.search(q):
        return "Refusing request involving sensitive personal data (PII)."
    # For medical/legal, we don't fully refuse; we can allow but will disclaim in prompt.
    # If you want strict refusal, uncomment below lines.
    # if MEDICAL_RE.search(q):
    #     return "Refusing medical advice request."
    # if LEGAL_RE.search(q):
    #     return "Refusing legal advice request."
    return None
