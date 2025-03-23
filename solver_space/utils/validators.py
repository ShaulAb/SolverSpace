import re
import unicodedata
from typing import Tuple

class UsernameValidator:
    """Comprehensive username validator with security features.
    
    This validator ensures usernames:
    - Start with a letter
    - Contain only letters, numbers, and underscores
    - Are between 3-30 characters long
    - Are not reserved words
    
    Security is enforced through strict format validation:
    - Only ASCII letters allowed (no Unicode homographs)
    - No special characters or spaces
    - No mixed scripts
    """
    
    # Constants
    MIN_LENGTH = 3
    MAX_LENGTH = 30
    PATTERN = r'^[a-zA-Z][a-zA-Z0-9_]{2,29}$'
    
    # Error Messages
    ERROR_LENGTH = "Username must be between 3-30 characters"
    ERROR_FORMAT = "Username must start with a letter and contain only letters, numbers, and underscores"
    ERROR_RESERVED = "This username is reserved"
    
    def __init__(self):
        self.reserved_words = {
            'admin', 'administrator', 'root', 'sudo',
            'www', 'api', 'mail', 'smtp', 'support',
            'help', 'info', 'contact', 'login', 'logout',
            'signin', 'signup', 'register', 'password',
        }
    
    def validate(self, username: str) -> Tuple[bool, str]:
        """Validate a username against all security rules.
        
        Args:
            username: The username to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Empty/length check
        if not username or len(username) < self.MIN_LENGTH or len(username) > self.MAX_LENGTH:
            return False, self.ERROR_LENGTH
            
        # Normalize and check format (catches non-Latin chars)
        normalized = self._normalize_for_storage(username)
        if not re.match(self.PATTERN, normalized):
            return False, self.ERROR_FORMAT
            
        # Reserved words check
        if normalized.lower() in self.reserved_words:
            return False, self.ERROR_RESERVED
            
        return True, ""

    def sanitize(self, username: str) -> str:
        """Convert username to a safe format.
        
        Args:
            username: The username to sanitize
            
        Returns:
            str: A sanitized version of the username
        """
        if not username:
            return "u"
            
        # Normalize for storage
        username = self._normalize_for_storage(username)
        
        # Replace unsafe characters with underscores
        username = re.sub(r'[^a-zA-Z0-9_]', '_', username)
        
        # Ensure it starts with a letter
        if not username[0].isalpha():
            username = 'u' + username
        
        # Truncate if too long
        return username[:self.MAX_LENGTH]
        
    def _normalize_for_storage(self, username: str) -> str:
        """Normalize username for storage and comparison.
        
        Args:
            username: The username to normalize
            
        Returns:
            str: Normalized username
        """
        return unicodedata.normalize('NFKC', username) 