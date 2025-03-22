# signup.py
import reflex as rx
from ..components.auth.signup_form import signup_form

def signup() -> rx.Component:
    return signup_form()
