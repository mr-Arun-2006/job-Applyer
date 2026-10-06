from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from playwright.sync_api import Page


@dataclass
class FormAction:
    field: str
    value: str
    status: str


class FormAgent:
    """Fill ordinary fields; human handles CAPTCHA/MFA/anti-bot controls."""

    BLOCKED_NAMES: ClassVar[frozenset[str]] = frozenset(
        {"captcha", "recaptcha", "hcaptcha", "mfa", "otp", "verification"}
    )

    def fill_text_fields(self, page: Page, answers: dict[str, str]) -> list[FormAction]:
        actions: list[FormAction] = []
        for field, value in answers.items():
            if field.lower() in self.BLOCKED_NAMES:
                actions.append(FormAction(field, "", "NEEDS_HUMAN_INPUT"))
                continue
            locator = page.locator(f'[name="{field}"]')
            if locator.count() == 0:
                actions.append(FormAction(field, "", "NOT_FOUND"))
                continue
            locator.first.fill(value)
            actions.append(FormAction(field, value, "FILLED"))
        return actions

    def require_confirmation_before_submit(self) -> bool:
        return True
