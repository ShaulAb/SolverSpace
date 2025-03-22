import reflex as rx
from ...models.user import AuthState

def login_form() -> rx.Component:
    """Login form component."""
    return rx.vstack(
        rx.heading("Login", size="3"),
        rx.form(
            rx.vstack(
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
                    "Login",
                    type="submit",
                    width="100%",
                    size="2",
                    is_loading=AuthState.processing,
                ),
                rx.button(
                    "Sign up",
                    variant="outline",
                    width="100%",
                    size="2",
                    on_click=rx.redirect("/signup"),
                ),
                rx.cond(
                    AuthState.error,
                    rx.text(AuthState.error, color="red"),
                ),
            ),
            on_submit=AuthState.handle_login_form,
            width="100%",
            spacing="4",
        ),
        spacing="4",
        width="100%",
        max_width="400px",
        margin="auto",
        padding="4",
    )
