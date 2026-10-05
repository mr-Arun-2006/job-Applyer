from dataclasses import dataclass
from playwright.sync_api import Page


@dataclass
class FormAction:
    field: str
    value: str
    status: str


class FormAgent:
    """Fill ordinary fields; human handles CAPTCHA/MFA/anti-bot controls."""

    BLOCKED_NAMES = {"captcha", "recaptcha", "hcaptcha", "mfa", "otp", "verification"}

    def fill_text_fields(self, page: Page, answers: dict[str, str]) -> list[FormAction]:
        actions = []
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
