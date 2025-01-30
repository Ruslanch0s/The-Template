import asyncio
import botright


async def main():
    botright_client = await botright.Botright()
    browser = await botright_client.new_browser()
    page = await browser.new_page()

    await page.goto("http://playwright.dev")
    print(await page.title())

    await botright_client.close()

if __name__ == "__main__":
    asyncio.run(main())