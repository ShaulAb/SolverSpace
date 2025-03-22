from typing import Optional
from datetime import datetime
import reflex as rx
from pydantic import BaseModel
from ..services.supabase import supabase

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
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            user_data = auth_response.user
            if not user_data:
                self.error = "Invalid email or password"
                return
                
            self.user = User(
                id=user_data.id,
                email=user_data.email,
                created_at=user_data.created_at,
            )
            # Fetch profile data
            profile = supabase.table('profiles').select('*').eq('id', user_data.id).single().execute()
            if profile.data:
                self.user.username = profile.data.get('username')
            return rx.redirect('/')
        except Exception as e:
            self.error = "Invalid email or password"
        finally:
            self.processing = False

    async def _signup(self, email: str, password: str, username: str):
        """Handle signup."""
        self.processing = True
        self.error = None
        try:
            # Check if username is available
            existing_profile = supabase.table('profiles').select('username').eq('username', username).execute()
            if existing_profile.data:
                self.error = "Username already taken"
                return

            # Create auth user
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            user_data = auth_response.user

            # Create profile
            supabase.table('profiles').insert({
                'id': user_data.id,
                'username': username,
            }).execute()

            self.user = User(
                id=user_data.id,
                email=user_data.email,
                username=username,
                created_at=user_data.created_at,
            )
            return rx.redirect('/')
        except Exception as e:
            self.error = str(e)
        finally:
            self.processing = False

    async def logout(self):
        """Handle logout."""
        try:
            supabase.auth.sign_out()
            self.user = None
            return rx.redirect('/login')
        except Exception as e:
            self.error = str(e)

    async def handle_login_form(self, form_data: dict):
        """Handle login form submission."""
        try:
            return await self._login(
                email=form_data.get("email", ""),
                password=form_data.get("password", "")
            )
        except KeyError:
            self.error = "Please fill in all required fields"

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
