import reflex as rx
from ...models.user import AuthState

def signup_form() -> rx.Component:
    """Signup form component."""
    return rx.vstack(
        rx.heading("Create Account", size="3"),
        rx.cond(
            AuthState.success_message,
            rx.callout(
                AuthState.success_message,
                color_scheme="green",
                margin_bottom="4",
            ),
        ),
        rx.form(
            rx.vstack(
                rx.input(
                    placeholder="Username",
                    id="username",
                    required=True,
                ),
                rx.input(
                    placeholder="Email",
                    type="email",
                    id="email",
                    required=True,
                ),
                rx.input(
                    placeholder="Password",
                    type="password",
                    id="password",
                    required=True,
                ),
                rx.button(
                    "Sign up",
                    type="submit",
                    width="100%",
                    size="2",
                    is_loading=AuthState.processing,
                ),
                rx.link(
                    "Already have an account? Login",
                    href="/login",
                    color="blue.500",
                ),
                rx.cond(
                    AuthState.error,
                    rx.callout(
                        AuthState.error,
                        color_scheme="red",
                        margin_top="4",
                    ),
                ),
            ),
            on_submit=AuthState.handle_signup_form,
            width="100%",
            spacing="4",
        ),
        spacing="4",
        width="100%",
        max_width="400px",
        margin="auto",
        padding="4",
    )
