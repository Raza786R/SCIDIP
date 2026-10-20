import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://accubate.fitt-iitd.in/ext/form/23761/1/apply", wait_until="networkidle")
        
        # Wait a bit extra just in case it takes time to render the form
        await page.wait_for_timeout(3000)
        
        # Extract text content from the body
        content = await page.locator("body").inner_text()
        
        with open(r"c:\Users\MOHAMMED AHMED RAZA\Desktop\STUDY\SAFRAN_CHALLENGE_2026\IIT_DELHI_SCIDIP\IIT_DELHI_SCIDIP_FORM_EXTRACT.txt", "w", encoding="utf-8") as f:
            f.write(content)
            
        await browser.close()

asyncio.run(main())
