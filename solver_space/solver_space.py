"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from .pages.index import index
from .pages.login import login
from .pages.signup import signup
from .components.navbar import navbar


class State(rx.State):
    """The app state."""
    pass


# Create app instance
app = rx.App()

# Define base layout
def base_layout(content: rx.Component) -> rx.Component:
    """Base layout for all pages."""
    return rx.vstack(
        navbar(),
        content,
        min_height="100vh",
        spacing="0",
    )

# Create wrapped page components
def wrapped_index():
    return base_layout(index())

def wrapped_login():
    return base_layout(login())

def wrapped_signup():
    return base_layout(signup())

# Add pages
app.add_page(
    wrapped_index,
    route="/",
    title="Solver Space - Home",
)

app.add_page(
    wrapped_login,
    route="/login",
    title="Login - Solver Space",
)

app.add_page(
    wrapped_signup,
    route="/signup",
    title="Sign Up - Solver Space",
)
