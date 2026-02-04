import os
from typing import Dict, Optional
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Browser, Page

load_dotenv()


class BrowserAuthService:
    def __init__(self):
        self.username = os.getenv('RC_USERNAME')
        self.password = os.getenv('RC_PASSWORD')
        self.browser_ws_endpoint = "http://localhost:9222"
        
    async def login_to_ringcentral(self) -> Dict[str, str]:
        """
        Log into RingCentral using browser automation via CDP on port 9222
        """
        if not self.username or not self.password:
            raise ValueError("RC_USERNAME and RC_PASSWORD must be set in .env file")
        
        async with async_playwright() as p:
            try:
                # Connect to browser on port 9222
                browser = await p.chromium.connect_over_cdp(self.browser_ws_endpoint)
                
                # Create new page or use existing context
                context = browser.contexts[0] if browser.contexts else await browser.new_context()
                page = await context.new_page()
                
                # Navigate to RingCentral login page
                await page.goto('https://login.ringcentral.com/', wait_until='networkidle')
                
                # Wait for the login form to be visible
                await page.wait_for_selector('input[type="email"]', state='visible', timeout=30000)
                
                # Fill in the email/username
                await page.fill('input[type="email"]', self.username)
                
                # Click next/continue button if exists, or proceed to password
                next_button = page.locator('button:has-text("Next"), button:has-text("Continue")')
                if await next_button.count() > 0:
                    await next_button.first.click()
                    await page.wait_for_timeout(1000)
                
                # Wait for password field and fill it
                await page.wait_for_selector('input[type="password"]', state='visible', timeout=30000)
                await page.fill('input[type="password"]', self.password)
                
                # Click sign in button
                sign_in_button = page.locator('button[type="submit"], button:has-text("Sign In"), button:has-text("Log In")')
                await sign_in_button.first.click()
                
                # Wait for successful login - adjust the URL pattern based on actual redirect
                try:
                    await page.wait_for_url('**/app/**', timeout=60000)
                    login_success = True
                    message = "Successfully logged into RingCentral"
                except Exception as e:
                    # Check if we're on a different success page
                    current_url = page.url
                    if 'login' not in current_url.lower():
                        login_success = True
                        message = f"Login appears successful. Current URL: {current_url}"
                    else:
                        login_success = False
                        message = f"Login may have failed. Current URL: {current_url}"
                
                # Keep the page open - don't close browser since we're connected via CDP
                return {
                    "status": "success" if login_success else "failed",
                    "message": message,
                    "url": page.url,
                    "username": self.username
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Login failed: {str(e)}",
                    "username": self.username
                }
