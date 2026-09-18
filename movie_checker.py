from playwright.sync_api import sync_playwright
import requests
import os
import time


BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


movies_to_watch = [
    "Dune",
    "Doomsday",
    "Avengers"
]


def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


def check_site(cinema, url):

    print("Checking:", cinema)

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-http2"
            ]
        )

        page = browser.new_page(
            user_agent=
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120 Safari/537.36"
        )


        try:

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )


        except Exception as e:

            print(
                "Could not open",
                cinema,
                e
            )

            browser.close()
            return


        time.sleep(5)


        content = page.content().lower()

        print(content[:2000])


        found = []


        for movie in movies_to_watch:

            if movie.lower() in content:

                found.append(movie)



        browser.close()



        if found:

            message = (
                "🎬 Movie Alert!\n\n"
                f"Cinema: {cinema}\n\n"
                +
                "\n".join(found)
                +
                "\n\n"
                +
                url
            )

            send_message(message)



check_site(
    "VOX Egypt",
    "https://egy.voxcinemas.com/movies/whatson"
)


check_site(
    "Scene District 5",
    "https://district5.scenecinemas.com/home"
)
