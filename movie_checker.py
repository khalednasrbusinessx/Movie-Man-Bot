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
            headless=True
        )

        page = browser.new_page()

        page.goto(
            url,
            wait_until="networkidle",
            timeout=60000
        )

        time.sleep(5)

        content = page.content().lower()

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
                + url
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
