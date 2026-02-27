import hashlib
from typing import Optional


def generate_fingerprint(ip_address: str, user_agent: str, accept_language: str = "") -> str:
    """
    Generate a consistent but anonymous fingerprint hash for tracking users.
    Combines: IP address, user-agent, and accept-language headers.
    
    Args:
        ip_address: Client's IP address
        user_agent: Client's user-agent string
        accept_language: Client's accept-language header
        
    Returns:
        SHA256 hash of the combined data
    """
    fingerprint_str = f"{ip_address}:{user_agent}:{accept_language}"
    return hashlib.sha256(fingerprint_str.encode()).hexdigest()
