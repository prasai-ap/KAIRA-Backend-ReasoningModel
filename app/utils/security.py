import hashlib

def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def verify_hash(raw_value: str, hashed_value: str) -> bool:
    return hash_value(raw_value) == hashed_value