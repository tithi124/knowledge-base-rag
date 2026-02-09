import re

SMALLTALK_RE = re.compile(r"^(hi|hello|hey|yo)\b|how are you|what'?s up|good (morning|evening)", re.I)

def detect_intent(q: str) -> str:
    s = q.strip()
    if not s:
        return "empty"
    if len(s) <= 18 and SMALLTALK_RE.search(s):
        return "smalltalk"
    return "knowledge_query"

def should_search(intent: str) -> bool:
    return intent == "knowledge_query"
