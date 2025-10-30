# -------------------------------------------------------------
# Text utilities for normalization, hashing, and quality metrics.
# -------------------------------------------------------------
import re, hashlib

def normalize_text(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def type_token_ratio(s: str) -> float:
    toks = re.findall(r"\w+", s.lower())
    if not toks:
        return 0.0
    return len(set(toks)) / len(toks)
