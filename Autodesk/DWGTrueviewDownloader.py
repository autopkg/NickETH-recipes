#!/usr/local/autopkg/python
#
# Copyright 2025 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2025-12-10.
#
# Downloads the installer stub for DWG Trueview with PlayWright
#
# Output needs work.
# 20251210 Nick Heim: Initial release.
# 20260706 Nick Heim: Update Cookie- and Download-button selector.

import re
import asyncio
import html

from autopkglib import Processor, ProcessorError

from playwright.async_api import async_playwright

__all__ = ["DWGTrueviewDownloader"]

class DWGTrueviewDownloader(Processor):
    """Uses Playwright to fetch and render a JavaScript-heavy URL, then performs a regex search."""

    input_variables = {
        "url": {"description": "URL to fetch and render", "required": False},
        "result_output_var_name": {
            "description": (
                "The name of the output variable that will hold the match. "
                "Defaults to 'match'."
            ),
            "required": False,
            "default": "match",
        },
        "file_path": {"required": True, "description": "Path to a file to create."},
        "wait_until": {
            "description": (
                "Optional waitUntil option for Playwright (load, domcontentloaded, networkidle). Default: load"
            ),
            "required": False,
            "default": "load",
        },
        "timeout": {
            "description": "Optional timeout in milliseconds. Default: 30000",
            "required": False,
            "default": 30000,
        }
    }

    output_variables = {
        "result_output_var_name": {
            "description": "Matched value from the rendered page.",
        }
    }

    description = __doc__

    async def fetch_page_content(self, url: str, wait_until: str, timeout: int) -> str:
        """Use Playwright to render and extract HTML from the given URL."""
        async with async_playwright() as p:
            #browser = await p.chromium.launch(headless=True)
            browser = await p.chromium.launch(headless=False)

            context = await browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"),
                locale="en-US",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.autodesk.com/"
                }
            )
            page = await context.new_page()

            page.set_default_navigation_timeout(60000)
            await page.goto(url, wait_until="domcontentloaded")

            try:
                await page.wait_for_load_state("load", timeout=10000)
            except:
                pass

            # Close the region-Popup/Modal (find the dialog and click the button)
            try:
                # Get the "Stay" button
                modal = page.locator("div[role='dialog']")
                if await modal.locator("button:has-text('Stay')").count() > 0:
                    await modal.locator("button:has-text('Stay')").first.click()
            except:
                pass  # No dialog found

            # Close the cookie banner (find the dialog and click the button)
            try:
                # Get the "Decline" button
                # modal = page.locator("div[role='dialog']")
                # if await modal.locator("button:has-text('Decline')").count() > 0:
                    # await modal.locator("button:has-text('Decline')").first.click()
                # Wait for the cookie banner to appear
                await page.wait_for_selector('button[data-wat-val="decline all"]', timeout=10000)

                # Click the Decline button
                await page.click('button[data-wat-val="decline all"]')
            except:
                pass  # No dialog found

            await page.wait_for_timeout(2000)

            await page.locator("button svg[data-testid='KeyboardArrowDownIcon']").click()
            await page.wait_for_timeout(2000)

            async with page.expect_download() as download_info:
                #await page.locator("li.instant-access-mfe-MuiMenuItem-root", has_text="Download").click()
                await page.locator("li.MuiButtonBase-root.MuiMenuItem-root", has_text="Download").click()
        
            await page.wait_for_timeout(15000)

            download = await download_info.value

            # Save the file to the desired path
            await download.save_as(self.env["file_path"])
        
            await browser.close()

    def main(self) -> None:
        url = self.env.get("url", "https://www.autodesk.com/products/dwg-trueview/overview")
        wait_until = self.env.get("wait_until", "load")
        timeout = int(self.env.get("timeout", 30000))
        output_var_name = self.env.get("result_output_var_name", "match")
        file_path = self.env["file_path"]

        try:
            content = asyncio.run(
                self.fetch_page_content(url, wait_until=wait_until, timeout=timeout)
            )
        except Exception as e:
            raise ProcessorError(f"Playwright error while loading {url}: {e}")

if __name__ == "__main__":
    processor = DWGTrueviewDownloader()
    processor.execute_shell()
