# login.py
import reflex as rx
from ..components.auth.login_form import login_form

def login() -> rx.Component:
    return login_form()