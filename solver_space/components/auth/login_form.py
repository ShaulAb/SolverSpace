import reflex as rx
from ...models.user import AuthState

def login_form() -> rx.Component:
    """Create a login form."""
    return rx.vstack(
        rx.heading("Login", size="3"),
        rx.form(
            rx.vstack(
                rx.input(
                    placeholder="Email",
                    id="email",
                    type="email",
                    required=True,
                ),
                rx.input(
                    placeholder="Password",
                    id="password",
                    type="password",
                    required=True,
                ),
                rx.button(
                    "Login",
                    type="submit",
                    width="100%",
                    is_loading=AuthState.processing,
                ),
                rx.link(
                    "Sign up",
                    href="/signup",
                    color="blue.500",
                    _hover={"text_decoration": "none"},
                ),
                spacing="4",
            ),
            on_submit=AuthState.handle_login_form,
        ),
        rx.cond(
            AuthState.error,
            rx.callout(
                AuthState.error,
                color_scheme="red",
                class_name="error-message",
            ),
        ),
        width="100%",
        max_width="400",
        spacing="4",
        py="4",
    )
