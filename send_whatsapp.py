# send_whatsapp.py
"""
Light-weight WhatsApp-Web sender.
Works by opening https://web.whatsapp.com and re-using the logged-in session
stored in `whatsapp_state.json`.

⚠️  Notes
• Keep sending volume modest (<100 msgs/hr) and add small random delays;
  heavy automation can trigger rate-limits or a temporary ban.
• The target phone number **must** be on WhatsApp.
• Phone number format: E.164 without "whatsapp:" prefix (e.g. "+919876543210").
"""

from pathlib import Path
from urllib.parse import quote_plus
from time import sleep
from random import uniform

from playwright.sync_api import sync_playwright

STORAGE_STATE = "whatsapp_state.json"


def _ensure_logged_in(context):
    """
    If this is the very first run (no cookie file yet), open WA Web
    and wait for the user to scan the QR code once.
    """
    page = context.new_page()
    page.goto("https://web.whatsapp.com", wait_until="networkidle")

    # If already logged in the search box is present.
    try:
        page.wait_for_selector('div[title="Search input textbox"]', timeout=8000)
        page.close()
        return
    except:
        print("🚪  First-time login – scan the QR code in the opened browser window.")
        # Wait until login completes (search box visible)
        page.wait_for_selector('div[title="Search input textbox"]', timeout=0)
        print("✅  WhatsApp session saved.")
        # Persist cookies/storage for next runs
        context.storage_state(path=STORAGE_STATE)
        page.close()


def send_whatsapp_message(phone_number: str, message: str) -> bool:
    """
    Opens https://web.whatsapp.com/send?phone=<num>&text=<msg>,
    waits for chat to load, then presses Enter to send.
    Returns True on success, False otherwise.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=50)

            # Re-use previous session if it exists
            if Path(STORAGE_STATE).exists():
                context = browser.new_context(storage_state=STORAGE_STATE)
            else:
                context = browser.new_context()

            _ensure_logged_in(context)

            page = context.new_page()

            url = (
                f"https://web.whatsapp.com/send?"
                f"phone={phone_number.lstrip('+')}"
                f"&text={quote_plus(message)}"
                "&app_absent=0"
            )
            page.goto(url, wait_until="networkidle")

            # Wait for the message box to show up
            page.wait_for_selector('div[data-testid="conversation-panel-messages"]', timeout=20000)

            # Press Enter to actually send the pre-filled text
            page.keyboard.press("Enter")

            # Small human-like delay, then close everything
            sleep(uniform(1.5, 2.5))
            context.storage_state(path=STORAGE_STATE)  # refresh cookies
            browser.close()

        print(f"✅  WhatsApp message sent to {phone_number}")
        return True

    except Exception as e:
        print(f"❌  Failed to send WhatsApp message to {phone_number}: {e}")
        return False
