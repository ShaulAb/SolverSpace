"""Password requirements component."""
import reflex as rx
from typing import List
from ...utils.validation_types import ValidationCheck

def requirement_item(check: ValidationCheck) -> rx.Component:
    """Single requirement item with icon and text.
    
    Args:
        check: The validation check to display
        
    Returns:
        A component showing the requirement status
    """
    return rx.hstack(
        rx.icon(
            rx.cond(
                check["passed"],
                "check",
                "close"
            ),
            color=rx.cond(
                check["passed"],
                "green.500",
                "red.500"
            ),
            _hover={"cursor": "default"},
        ),
        rx.text(
            check["message"],
            color="gray.600",
            font_size="sm",
        ),
        spacing="2",
        align_items="center",
    )

def password_requirements(checks: List[ValidationCheck]) -> rx.Component:
    """Password requirements checklist component.
    
    Args:
        checks: List of requirement checks with pass/fail status
        
    Returns:
        A component displaying password requirements with visual feedback
    """
    return rx.vstack(
        rx.text(
            "Password requirements:",
            font_size="sm",
            color="gray.600",
            font_weight="medium",
        ),
        rx.vstack(
            rx.foreach(
                checks,
                requirement_item
            ),
            spacing="1",
            align_items="start",
            padding_left="2",
        ),
        spacing="2",
        align_items="start",
        background="gray.50",
        padding="3",
        border_radius="md",
    ) 