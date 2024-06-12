import asyncio
from pyppeteer import launch
import random
from tesseract import ocr_image
import csv


def remove_last_newline(text):
    if text.endswith("\n"):
        return text[:-1]
    return text


async def main():
    executable_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    browser = await launch(headless=False, executablePath=executable_path)
    page = await browser.newPage()

    await page.goto("https://appli.foncier.gouv.qc.ca/infolot/", timeout=50000)

    await page.waitForSelector("body")
    pages_before_click = len(await browser.pages())

    submit_button = await page.querySelector('input[value="Accéder à Infolot gratuit"]')
    await submit_button.click()

    while len(await browser.pages()) == pages_before_click:
        await asyncio.sleep(0.1)

    page = (await browser.pages())[-1]

    error_not_found = False
    while error_not_found == False:
        checkbox_input = await page.waitForSelector("#checkBoxLicense")
        await checkbox_input.click()

        await page.waitForSelector(".visualCaptcha-possibilities")
        visualCaptcha_imgs = await page.querySelectorAll(
            ".visualCaptcha-possibilities .img"
        )
        await visualCaptcha_imgs[3].click()

        device_imgs = await page.querySelectorAll(
            'div[title="Accéder à l\'application bureau"]'
        )
        await device_imgs[0].click()

        try:
            await page.waitForSelector(".fo_callout.fo_callout_error", timeout=10000)
        except asyncio.TimeoutError:
            error_not_found = True

    await page.waitForSelector("button.data-frame-button.tab-closed", timeout=50000)
    tab_open_btn = await page.querySelector("button.data-frame-button.tab-closed")

    await page.evaluate("element => element.scrollIntoView()", tab_open_btn)
    await page.evaluate("element => element.click()", tab_open_btn)
    
    with open("output.csv", "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "Lot Number",
                "Région administrative",
                "MRC",
                "Municipalité",
                "Com. métro.",
                "Arrondissement",
                "Circ. foncière",
            ]
        )

    for index in range(2):
        random_lot = random.randint(1000000, 10000000)
        try:
            await page.waitForSelector("#gcx_search")
            await page.evaluate('document.querySelector("#gcx_search").value = ""')
            await page.type("#gcx_search", str(random_lot))

            page.waitForSelector(".search-button")
            search_btn = await page.querySelector(".search-button")
            await page.evaluate("element => element.scrollIntoView()", search_btn)
            await page.evaluate("element => element.click()", search_btn)

            selector = "div.public_fixedDataTableCell_cellContent.text-cell"
            await page.waitForSelector(selector, timeout=100000)
            lot_line = await page.querySelector(selector)
            await lot_line.click()

            if index == 0:
                await page.waitForSelector("span.display-name")

                elements = await page.querySelectorAll("span.display-name")
                for element in elements:
                    text = await page.evaluate(
                        "(element) => element.textContent", element
                    )
                    if text.strip() == "Entités administratives":
                        await element.click()
                        break
                    
                await page.waitForSelector(f'input[aria-label="Municipalité"]')
                await page.click(f'input[aria-label="Municipalité"]')
                await asyncio.sleep(2)
                
            labels = [
                ("Région administrative"),
                ("MRC"),
                ("Municipalité"),
                ("Com. métro."),
                ("Arrondissement"),
                ("Circ. foncière"),
            ]
            

            result = []
            result.append(random_lot)
            for label in labels:
                await page.waitForSelector(f'input[aria-label="{label}"]')
                await page.click(f'input[aria-label="{label}"]')
                await asyncio.sleep(2)
                await page.waitForSelector("#map_12 img")

                img_src = await page.evaluate(
                    """(selector) => {
                    const img = document.querySelector(selector);
                    return img ? img.src : null;
                }""",
                    "#map_12 img",
                )
                text = ocr_image(img_src)
                result.append(remove_last_newline(text))

                await page.waitForSelector(f'input[aria-label="{label}"]')
                await page.click(f'input[aria-label="{label}"]')
                print(remove_last_newline(text))

            with open("output.csv", "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                print(result)
                writer.writerow(result)

        except:
            continue
    await browser.close()


asyncio.run(main())
