#!/usr/local/autopkg/python
#
# Copyright 2025 Swiss federal institute of technology (ETHZ).
#
# Created by Nick Heim (heim)@ethz.ch) on 2026-08-02.
#
# Downloads the installers for Irfanview with PlayWright
#
# Output needs work.
#
# 20260804 Nick Heim: Initial release.

import re
import asyncio
import html

from autopkglib import Processor, ProcessorError

from playwright.async_api import async_playwright

__all__ = ["IrfanViewDownloader"]

class IrfanViewDownloader(Processor):
    """Uses Playwright to fetch and render a JavaScript-heavy URL, then performs a regex search."""

    input_variables = {
        "url": {"description": "URL to fetch and render", "required": True},
        "result_output_var_name": {
            "description": (
                "The name of the output variable that will hold the match. "
                "Defaults to 'match'."
            ),
            "required": False,
            "default": "match",
        },
        "main_file": {"required": True, "description": "main file to download."},
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

    async def fetch_page_content(self, url: str, main_file: str, wait_until: str, timeout: int) -> str:
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
                    "Referer": "www.irfanview.info",
                }
            )

            page = await context.new_page()

            page.set_default_navigation_timeout(10000)
            await page.goto(url, wait_until="domcontentloaded")

            try:
                await page.wait_for_load_state("load", timeout=10000)
            except:
                pass

            async with page.expect_download() as download_info:
                await page.locator(f"xpath=//a[contains(@href,'{main_file}')]").first.click()
            
            await page.wait_for_timeout(15000)

            download = await download_info.value

            # Save the file to the desired path
            await download.save_as(self.env["file_path"])
        
            await browser.close()

    def main(self) -> None:
        url = self.env.get("url", "https://www.irfanview.info")
        wait_until = self.env.get("wait_until", "load")
        timeout = int(self.env.get("timeout", 10000))
        output_var_name = self.env.get("result_output_var_name", "match")
        file_path = self.env["file_path"]
        main_file = self.env["main_file"]

        try:
            content = asyncio.run(
                self.fetch_page_content(url, main_file, wait_until=wait_until, timeout=timeout)
            )
        except Exception as e:
            raise ProcessorError(f"Playwright error while loading {url}: {e}")

if __name__ == "__main__":
    processor = IrfanViewDownloader()
    processor.execute_shell()
