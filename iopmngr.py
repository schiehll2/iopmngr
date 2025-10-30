# iopmngr.py
# Automated RPA for clock-in/out using Playwright
# Author: Carlos Junior
# Repo: iopmngr

import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# Load environment variables
load_dotenv()

USERNAME = os.getenv("PONTO_USERNAME")
PASSWORD = os.getenv("PONTO_PASSWORD")
BASE_URL = os.getenv("PONTO_BASE_URL")  # e.g. "https://meu-ponto.com/login"
ACTION = os.getenv("PONTO_ACTION", "in")  # default "in" (entrada)

if not USERNAME or not PASSWORD or not BASE_URL:
    raise SystemExit("Missing required env vars: PONTO_USERNAME, PONTO_PASSWORD, PONTO_BASE_URL")

def main():
    print(f"[iopmngr] Starting RPA action '{ACTION}' for {USERNAME}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()

        try:
            # Go to login page
            page.goto(BASE_URL, wait_until="networkidle")

            # --- Adjust selectors below according to your system ---
            page.fill('input[name="username"]', USERNAME)
            page.fill('input[name="password"]', PASSWORD)
            page.click('button[type="submit"]')

            # Wait for main page or dashboard
            page.wait_for_load_state("networkidle")

            # Optional navigation to punch page
            # page.goto("https://meu-ponto.com/bater-ponto")

            # Choose button selector (edit as needed)
            punch_selector = (
                'button#punch-in' if ACTION == "in" else 'button#punch-out'
            )

            page.wait_for_selector(punch_selector, timeout=8000)
            page.click(punch_selector)

            # Wait and take screenshot
            page.wait_for_timeout(1500)
            screenshot_name = f"screenshot_{ACTION}.png"
            page.screenshot(path=screenshot_name)
            print(f"[iopmngr] Screenshot saved: {screenshot_name}")

            print(f"[iopmngr] Ponto '{ACTION}' completed successfully ✅")

        except PWTimeout as e:
            print("[iopmngr] Timeout while waiting for element.", e)
            page.screenshot(path="error_timeout.png")
        except Exception as e:
            print("[iopmngr] Unexpected error:", e)
            page.screenshot(path="error_unexpected.png")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    main()
