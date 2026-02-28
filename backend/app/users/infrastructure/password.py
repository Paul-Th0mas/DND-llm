"""
Password hashing and verification using bcrypt.

This module lives in the infrastructure layer because bcrypt is an external
library — a dependency detail that the domain layer must not know about.
The domain stores hashed_password as a plain str; this module is what
produces and checks those strings.
"""

import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(plain: str) -> str:
    """Returns a bcrypt hash of the given plaintext password."""
    logger.debug("hash_password: hashing password")
    hashed: bytes = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Returns True if the plaintext matches the stored bcrypt hash."""
    logger.debug("verify_password: checking password")
    return bool(bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8")))
