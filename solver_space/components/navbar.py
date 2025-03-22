import reflex as rx
from ..models.user import AuthState

def navbar() -> rx.Component:
    """Navigation bar component."""
    return rx.hstack(
        rx.heading("Solver Space", size="3"),
        rx.spacer(),
        rx.cond(
            AuthState.user,
            rx.hstack(
                rx.text(f"Welcome, {AuthState.user.username}"),
                rx.button(
                    "Logout",
                    on_click=AuthState.logout,
                    variant="ghost",
                ),
            ),
            rx.hstack(
                rx.link(
                    "Login",
                    href="/login",
                    padding="2",
                ),
                rx.link(
                    "Sign Up",
                    href="/signup",
                    padding="2",
                ),
            ),
        ),
        width="100%",
        padding="4",
        border_bottom="1px solid #eaeaea",
    )
