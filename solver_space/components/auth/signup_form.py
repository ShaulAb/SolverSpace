"""Signup form component with real-time validation."""
import reflex as rx
from ...models.user import AuthState
from .password_requirements import password_requirements
from ...utils.validation_types import FormValidationState

def signup_form() -> rx.Component:
    """Enhanced signup form with real-time validation."""
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
                # Username input with validation
                rx.input(
                    placeholder="Username",
                    id="username",
                    name="username",
                    value=AuthState.username,
                    on_change=AuthState.handle_username_change,
                    required=True,
                    border_color=rx.cond(
                        AuthState.form_validation_state.to(FormValidationState)["username"]["valid"],
                        "inherit",
                        "red.500"
                    ),
                ),
                rx.cond(
                    ~AuthState.form_validation_state.to(FormValidationState)["username"]["valid"] & AuthState.username_touched,
                    rx.text(
                        AuthState.form_validation_state.to(FormValidationState)["username"]["message"],
                        color="red.500",
                        font_size="sm",
                        margin_top="-2",
                    ),
                ),
                
                # Email input with validation
                rx.input(
                    placeholder="Email",
                    type="email",
                    id="email",
                    name="email",
                    value=AuthState.email,
                    on_change=AuthState.handle_email_change,
                    required=True,
                    border_color=rx.cond(
                        AuthState.form_validation_state.to(FormValidationState)["email"]["valid"],
                        "inherit",
                        "red.500"
                    ),
                ),
                rx.cond(
                    ~AuthState.form_validation_state.to(FormValidationState)["email"]["valid"] & AuthState.email_touched,
                    rx.text(
                        AuthState.form_validation_state.to(FormValidationState)["email"]["message"],
                        color="red.500",
                        font_size="sm",
                        margin_top="-2",
                    ),
                ),
                
                # Password input with validation
                rx.input(
                    placeholder="Password",
                    type="password",
                    id="password",
                    name="password",
                    value=AuthState.password,
                    on_change=AuthState.handle_password_change,
                    required=True,
                    border_color=rx.cond(
                        AuthState.form_validation_state.to(FormValidationState)["password"]["valid"],
                        "inherit",
                        "red.500"
                    ),
                ),
                rx.cond(
                    AuthState.form_validation_state.to(FormValidationState)["password"]["show_requirements"],
                    password_requirements(AuthState.form_validation_state.to(FormValidationState)["password"]["checks"]),
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
