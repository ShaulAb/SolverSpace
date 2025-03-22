import reflex as rx
from ...models.user import AuthState

def signup_form() -> rx.Component:
    """Signup form component."""
    return rx.vstack(
        rx.heading("Create Account", size="3"),
        rx.form(
            rx.vstack(
                rx.input(
                    placeholder="Username",
                    id="username",
                ),
                rx.input(
                    placeholder="Email",
                    type="email",
                    id="email",
                ),
                rx.input(
                    placeholder="Password",
                    type="password",
                    id="password",
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
                    rx.text(AuthState.error, color="red"),
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
