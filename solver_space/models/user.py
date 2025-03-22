from typing import Optional
from datetime import datetime
import reflex as rx
from pydantic import BaseModel
from ..services.supabase import supabase
from gotrue.errors import AuthWeakPasswordError

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
            # Check username availability
            existing_profile = supabase.table('profiles').select('username').eq('username', username).execute()
            if existing_profile.data:
                self.error = "Username already taken"
                return self.show_notification("Username already taken", "error")

            # Create auth user
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            
            if not auth_response.user:
                self.error = "Signup failed"
                return self.show_notification("Signup failed", "error")
            
            try:
                # Create profile
                profile_response = await supabase.table('profiles').insert({
                    'id': auth_response.user.id,
                    'username': username,
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
                    username=username,
                    created_at=auth_response.user.created_at,
                )
                
                # Show success message and redirect
                return [
                    self.show_notification(f"Welcome {username}!", "success"),
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
        except Exception as e:
            error_str = str(e)
            if "User already registered" in error_str:
                self.error = "Email already registered"
                return [
                    self.show_notification("Email already registered. Please login.", "info"),
                    rx.redirect('/login')
                ]
            else:
                print(f"Signup error: {e}")  # Log the actual error
                self.error = "An error occurred. Please try again."
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
