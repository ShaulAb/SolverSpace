"""Type definitions for form validation."""
from typing import List, TypedDict

class ValidationCheck(TypedDict):
    """Type for a single validation check."""
    passed: bool
    message: str

class ValidationState(TypedDict):
    """Type for field validation state."""
    valid: bool
    message: str

class PasswordValidationState(ValidationState):
    """Type for password validation state."""
    checks: List[ValidationCheck]
    show_requirements: bool

class FormValidationState(TypedDict):
    """Type for complete form validation state."""
    username: ValidationState
    password: PasswordValidationState
    email: ValidationState 