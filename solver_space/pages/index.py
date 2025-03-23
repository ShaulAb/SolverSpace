"""Index page."""
import reflex as rx
from ..models.user import AuthState

def index() -> rx.Component:
    """Index page component."""
    return rx.vstack(
        rx.heading(
            f"Welcome to Solver Space, {AuthState.user.username}!",
            size="3",
            class_name="welcome-message",
        ),
        rx.text(
            "Start exploring competitions or submit your solutions.",
            color="gray.400",
        ),
        rx.hstack(
            rx.link(
                rx.button(
                    rx.icon("trophy", size=24),
                    "Browse Competitions",
                    variant="outline",
                ),
                href="/competitions",
            ),
            rx.link(
                rx.button(
                    rx.icon("code", size=24),
                    "Submit Solutions",
                    variant="outline",
                ),
                href="/submit",
            ),
            spacing="4",
        ),
        width="100%",
        max_width="800px",
        spacing="6",
        py="8",
    )
