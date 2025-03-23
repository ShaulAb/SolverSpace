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
                rx.text(
                    rx.cond(
                        AuthState.user.username,
                        f"Welcome, {AuthState.user.username}",
                        "Welcome, User"
                    ),
                    color="white",
                    font_weight="medium",
                ),
                rx.button(
                    "Logout",
                    on_click=AuthState.logout,
                    variant="ghost",
                    color="white",
                    _hover={"bg": "whiteAlpha.200"},
                ),
                spacing="4",
            ),
            rx.hstack(
                rx.link(
                    "Login",
                    href="/login",
                    padding="2",
                    color="white",
                    _hover={"text_decoration": "none", "color": "blue.200"},
                ),
                rx.link(
                    "Sign Up",
                    href="/signup",
                    padding="2",
                    color="white",
                    _hover={"text_decoration": "none", "color": "blue.200"},
                ),
                spacing="2",
            ),
        ),
        width="100%",
        padding="4",
        bg="blackAlpha.400",
        border_bottom="1px solid whiteAlpha.300",
    )
