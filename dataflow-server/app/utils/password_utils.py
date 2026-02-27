"""Password hashing and verification utilities"""

import hashlib

try:
    from bcrypt import hashpw, gensalt, checkpw
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt (if available) or PBKDF2.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    if BCRYPT_AVAILABLE:
        # Use bcrypt for production-grade hashing
        salt = gensalt(rounds=12)
        hashed = hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    else:
        # Fallback to PBKDF2 if bcrypt is not available
        salt = hashlib.sha256(password.encode()).hexdigest()
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return f"pbkdf2_sha256$100000${salt}${pwd_hash.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    if BCRYPT_AVAILABLE:
        # Use bcrypt for verification
        return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    else:
        # Fallback to PBKDF2 verification
        if hashed_password.startswith('pbkdf2_sha256$'):
            _, iterations, salt, pwd_hash = hashed_password.split('$')
            new_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                int(iterations)
            )
            return new_hash.hex() == pwd_hash
        return False
