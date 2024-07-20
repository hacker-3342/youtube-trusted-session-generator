import asyncio
from nodriver import start, cdp, loop
import time
import json
import sys

async def main():
    tab_url = 'https://www.google.com/search?q=me+at+the+zoo&tbm=vid&source=lnms&hl=en&lr=lang_us'
    print("[INFO] launching browser.")
    browser = await start(headless=False)
    tab = browser.main_tab
    page = await browser.get(tab_url)
    accept_terms = await tab.find("Accept all")
    await accept_terms.click()
    print("[INFO] accepting cookies.")
    page = await browser.get(tab_url)
    await tab.wait(cdp.network.RequestWillBeSent)
    iframe = await tab.select("iframe")
    iframe_tab: uc.Tab = next(
        filter(
            lambda x: str(x.target.target_id) == str(iframe.frame_id), browser.targets
        )
    )
    print("[INFO] finding youtube iframe.")
    iframe_tab.websocket_url = iframe_tab.websocket_url.replace("iframe", "page")
    iframe_tab.add_handler(cdp.network.RequestWillBeSent, send_handler)
    await iframe_tab.wait(cdp.network.RequestWillBeSent)
    button_play = await tab.select("div[data-url]")
    await button_play.click()
    print("[INFO] click on first youtube video.")
    await iframe_tab.wait(cdp.network.RequestWillBeSent)
    print("[INFO] waiting additional 30 seconds for slower connections.")
    await tab.sleep(30)

async def send_handler(event: cdp.network.RequestWillBeSent):
    if "/youtubei/v1/player" in event.request.url:
        post_data = event.request.post_data
        post_data_json = json.loads(post_data)
        print("visitor_data: " + post_data_json["context"]["client"]["visitorData"])
        print("po_token: " + post_data_json["serviceIntegrityDimensions"]["poToken"])
        sys.exit(0)
    return

if __name__ == '__main__':

    loop().run_until_complete(main())