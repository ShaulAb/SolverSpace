from typing import Optional, Dict, List, TypedDict
from datetime import datetime
import reflex as rx
from pydantic import BaseModel
from ..services.supabase import supabase
from gotrue.errors import AuthWeakPasswordError
from ..utils.validators import UsernameValidator
import re
from ..utils.validation_types import ValidationCheck, ValidationState, PasswordValidationState, FormValidationState

class User(BaseModel):
    """User model for authentication."""
    id: str
    email: str
    username: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthState(rx.State):
    """Authentication state."""
    user: Optional[User] = None
    processing: bool = False
    error: Optional[str] = None
    success_message: Optional[str] = None
    temp_email: Optional[str] = None  # Store email temporarily for verification
    temp_username: Optional[str] = None  # Store username temporarily for verification
    
    # Form field states
    email: str = ""
    username: str = ""
    password: str = ""
    
    # Field touch states
    email_touched: bool = False
    username_touched: bool = False
    password_touched: bool = False
    
    # Validation caches
    _username_cache: Dict[str, ValidationState] = {}
    _password_cache: Dict[str, PasswordValidationState] = {}
    
    # Email validation regex
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    def _get_password_checks(self, password: str) -> List[ValidationCheck]:
        """Get password requirement checks.
        
        Args:
            password: The password to validate
            
        Returns:
            List of check results with pass/fail status and messages
        """
        return [
            {"passed": any(c.islower() for c in password), "message": "One lowercase letter"},
            {"passed": any(c.isupper() for c in password), "message": "One uppercase letter"},
            {"passed": any(c.isdigit() for c in password), "message": "One number"},
            {"passed": any(not c.isalnum() for c in password), "message": "One special character"},
            {"passed": len(password) >= 8, "message": "Minimum 8 characters"},
        ]
    
    def _validate_username(self, username: str) -> ValidationState:
        """Validate username with caching.
        
        Args:
            username: The username to validate
            
        Returns:
            Dict containing validation result and message
        """
        if username in self._username_cache:
            return self._username_cache[username]
            
        validator = UsernameValidator()
        is_valid, error_message = validator.validate(username)
        result: ValidationState = {"valid": is_valid, "message": error_message}
        
        # Cache only if username is long enough to avoid cache pollution
        if len(username) > 2:
            self._username_cache[username] = result
            # Limit cache size to prevent memory issues
            if len(self._username_cache) > 1000:
                self._username_cache.pop(next(iter(self._username_cache)))
        return result
    
    def _validate_password(self, password: str) -> PasswordValidationState:
        """Validate password with caching and progressive feedback.
        
        Args:
            password: The password to validate
            
        Returns:
            Dict containing validation result, message, and requirement checks
        """
        if password in self._password_cache:
            return self._password_cache[password]
            
        checks = self._get_password_checks(password)
        all_passed = all(check["passed"] for check in checks)
        
        result: PasswordValidationState = {
            "valid": all_passed,
            "message": "" if all_passed else "Password requirements not met",
            "checks": checks,
            "show_requirements": len(password) > 0
        }
        
        # Cache only if password is long enough
        if len(password) > 4:
            self._password_cache[password] = result
            # Limit cache size
            if len(self._password_cache) > 1000:
                self._password_cache.pop(next(iter(self._password_cache)))
        return result
    
    @rx.var
    def form_validation_state(self) -> FormValidationState:
        """Combined form validation state for all fields."""
        empty_password_state: PasswordValidationState = {
            "valid": True,
            "message": "",
            "checks": [],
            "show_requirements": False
        }
        empty_validation_state: ValidationState = {"valid": True, "message": ""}
        
        return {
            "username": self._validate_username(self.username) if self.username_touched else empty_validation_state,
            "password": self._validate_password(self.password) if self.password_touched else empty_password_state,
            "email": self.email_validation_state
        }
    
    @rx.var
    def email_validation_state(self) -> ValidationState:
        """Validate email format and return validation state."""
        if not self.email_touched:
            return {"valid": True, "message": ""}
        if not self.email:
            return {"valid": False, "message": "Email is required"}
        if not re.match(self.EMAIL_REGEX, self.email):
            return {"valid": False, "message": "Please enter a valid email address"}
        return {"valid": True, "message": ""}
    
    def handle_email_change(self, value: str):
        """Handle email input changes."""
        self.email = value
        self.email_touched = True
        self.error = None
    
    def handle_username_change(self, value: str):
        """Handle username input changes."""
        self.username = value
        self.username_touched = True
        self.error = None
    
    def handle_password_change(self, value: str):
        """Handle password input changes."""
        self.password = value
        self.password_touched = True
        self.error = None
    
    def _format_password_requirements(self, error_message: str) -> str:
        """Format password requirements into bullet points."""
        requirements = error_message.split(". ")
        return "Password requirements:\n" + "\n".join(f"• {req}" for req in requirements)

    def show_notification(self, message: str, status: str = "info"):
        """Show a toast notification using Reflex's built-in presets.
        
        Args:
            message: The message to display
            status: One of "success", "error", "warning", "info"
        """
        match status:
            case "success":
                return rx.toast.success(message, duration=5000, position="top-center")
            case "error":
                return rx.toast.error(message, duration=5000, position="top-center")
            case "warning":
                return rx.toast.warning(message, duration=5000, position="top-center")
            case "info":
                return rx.toast.info(message, duration=5000, position="top-center")
            case _:
                return rx.toast.info(message, duration=5000, position="top-center")

    def on_load(self):
        """Check if user is already logged in on page load."""
        try:
            # Get session from Supabase
            session = supabase.auth.get_session()
            if session:
                self.user = User(
                    id=session.user.id,
                    email=session.user.email,
                    created_at=session.user.created_at,
                )
                # Fetch additional user data from profiles table
                profile = supabase.table('profiles').select('*').eq('id', session.user.id).single().execute()
                if profile.data:
                    self.user.username = profile.data.get('username')
        except Exception:
            self.user = None

    async def _login(self, email: str, password: str):
        """Handle login."""
        self.processing = True
        self.error = None
        try:
            # Sign in and get session data
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Get user data from the session
            user_data = auth_response.user
            if not user_data:
                self.error = "Invalid email or password"
                return self.show_notification("Invalid email or password", "error")
            
            # Create base user object
            self.user = User(
                id=user_data.id,
                email=user_data.email,
                created_at=user_data.created_at,
            )
            
            try:
                # Fetch profile data
                profile = supabase.table('profiles').select('*').eq('id', user_data.id).single().execute()
                if profile and profile.data:
                    self.user.username = profile.data.get('username')
                else:
                    # Handle case where profile doesn't exist
                    self.user.username = email.split('@')[0]  # Use email prefix as fallback username
                    # Create profile if it doesn't exist
                    await supabase.table('profiles').insert({
                        'id': user_data.id,
                        'username': self.user.username,
                    }).execute()
            except Exception as profile_error:
                # Log profile error but don't fail login
                print(f"Error fetching profile: {profile_error}")
                self.user.username = email.split('@')[0]  # Use email prefix as fallback
            
            # Show welcome message and redirect
            welcome_name = self.user.username or "back"
            return [
                self.show_notification(f"Welcome {welcome_name}!", "success"),
                rx.redirect('/')
            ]
        except Exception as e:
            self.error = "Invalid email or password"
            return self.show_notification("Invalid email or password", "error")
        finally:
            self.processing = False

    async def _signup(self, email: str, password: str, username: str):
        """Handle signup."""
        self.processing = True
        self.error = None
        try:
            # Validate username
            username_validator = UsernameValidator()
            is_valid, error_message = username_validator.validate(username)
            if not is_valid:
                self.error = error_message
                return self.show_notification(error_message, "error")

            # Check username availability
            existing_profile = supabase.table('profiles').select('username').eq('username', username).execute()
            if existing_profile.data:
                self.error = "Username already taken"
                return self.show_notification("Username already taken", "error")

            # Create auth user
            try:
                auth_response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                })
            except Exception as e:
                error_str = str(e)
                if "invalid format" in error_str.lower():
                    self.error = "Please enter a valid email address"
                    return self.show_notification(self.error, "error")
                elif "User already registered" in error_str:
                    self.error = "Email already registered"
                    return [
                        self.show_notification("Email already registered. Please login.", "info"),
                        rx.redirect('/login')
                    ]
                else:
                    print(f"Signup error: {e}")  # Log the actual error
                    self.error = "An error occurred. Please try again."
                    return self.show_notification(self.error, "error")
            
            if not auth_response.user:
                self.error = "Signup failed"
                return self.show_notification("Signup failed", "error")
            
            try:
                # Create profile with sanitized username
                sanitized_username = username_validator.sanitize(username)
                profile_response = await supabase.table('profiles').insert({
                    'id': auth_response.user.id,
                    'username': sanitized_username,
                }).execute()

                if not profile_response.data:
                    # If profile creation fails, we should still log the user in
                    print("Profile creation failed, but user was created")
            except Exception as profile_error:
                # Log the profile error but continue with login
                print(f"Profile creation error: {profile_error}")
            
            # Log the user in immediately after signup
            try:
                login_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                # Set user data
                self.user = User(
                    id=auth_response.user.id,
                    email=auth_response.user.email,
                    username=sanitized_username,
                    created_at=auth_response.user.created_at,
                )
                
                # Show success message and redirect
                return [
                    self.show_notification(f"Welcome {sanitized_username}!", "success"),
                    rx.redirect('/')
                ]
            except Exception as login_error:
                print(f"Auto-login error: {login_error}")
                return [
                    self.show_notification("Account created! Please log in.", "success"),
                    rx.redirect('/login')
                ]
            
        except AuthWeakPasswordError as e:
            print(f"Password validation error: {e.message}")  # Log the raw error
            self.error = self._format_password_requirements(e.message)
            return self.show_notification(self.error, "error")
        finally:
            self.processing = False

    async def verify_otp(self, token: str):
        """Verify OTP token."""
        if not self.temp_email or not self.temp_username:
            return [
                self.show_notification("Please sign up again", "error"),
                rx.redirect('/signup')
            ]

        self.processing = True
        self.error = None
        try:
            # Verify OTP
            response = supabase.auth.verify_otp({
                "email": self.temp_email,
                "token": token,
                "type": "email"
            })
            
            if response.user:
                # Create profile after verification
                await supabase.table('profiles').insert({
                    'id': response.user.id,
                    'username': self.temp_username,
                }).execute()
                
                # Clear temporary data
                self.temp_email = None
                self.temp_username = None
                
                return [
                    self.show_notification("Email verified successfully!", "success"),
                    rx.redirect('/login')
                ]
        except Exception as e:
            self.error = "Invalid or expired code"
            return self.show_notification(self.error, "error")
        finally:
            self.processing = False
    
    async def resend_otp(self):
        """Resend OTP code."""
        if not self.temp_email:
            return [
                self.show_notification("Please sign up again", "error"),
                rx.redirect('/signup')
            ]
        
        try:
            await supabase.auth.resend_signup_otp({
                "email": self.temp_email,
            })
            return self.show_notification("New code sent to your email", "success")
        except Exception as e:
            return self.show_notification("Error sending code", "error")

    async def logout(self):
        """Handle logout."""
        try:
            supabase.auth.sign_out()
            self.user = None
            return [
                self.show_notification("Logged out successfully", "info"),
                rx.redirect('/login')
            ]
        except Exception as e:
            self.error = str(e)
            return self.show_notification(str(e), "error")

    async def handle_login_form(self, form_data: dict):
        """Handle login form submission."""
        try:
            return await self._login(
                email=form_data.get("email", ""),
                password=form_data.get("password", "")
            )
        except KeyError:
            self.error = "Please fill in all required fields"
            return self.show_notification("Please fill in all required fields", "error")

    async def handle_signup_form(self, form_data: dict):
        """Handle signup form submission."""
        try:
            # Set all fields as touched
            self.email_touched = True
            self.username_touched = True
            self.password_touched = True
            
            # Validate all fields
            validation_state = self.form_validation_state
            
            # Check email format
            if not validation_state["email"]["valid"]:
                self.error = validation_state["email"]["message"]
                return self.show_notification(self.error, "error")
            
            # Check username
            if not validation_state["username"]["valid"]:
                self.error = validation_state["username"]["message"]
                return self.show_notification(self.error, "error")
            
            # Check password
            if not validation_state["password"]["valid"]:
                self.error = "Password does not meet requirements"
                return self.show_notification(self.error, "error")
            
            # Proceed with signup
            return await self._signup(
                email=form_data.get("email", ""),
                password=form_data.get("password", ""),
                username=form_data.get("username", "")
            )
        except KeyError:
            self.error = "Please fill in all required fields"
            return self.show_notification("Please fill in all required fields", "error")

    async def handle_verify_form(self, form_data: dict):
        """Handle verification form submission."""
        try:
            return await self.verify_otp(form_data.get("token", ""))
        except KeyError:
            self.error = "Please enter the verification code"
            return self.show_notification("Please enter the verification code", "error")
