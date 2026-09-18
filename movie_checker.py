import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

movies_to_watch = [
    "Dune",
    "Doomsday"
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


def check_website(name, url):

    response = requests.get(url)

    text = response.text.lower()

    found = []

    for movie in movies_to_watch:
        if movie.lower() in text:
            found.append(movie)

    if found:
        message = (
            f"🎬 Movie Alert!\n\n"
            f"Cinema: {name}\n\n"
            +
            "\n".join(found)
            +
            f"\n\n{url}"
        )

        send_message(message)

send_message("🤖 Movie-Man Bot test message is working!")


check_website(
    "Scene District 5",
    "https://district5.scenecinemas.com/home"
)


check_website(
    "VOX Egypt",
    "https://egy.voxcinemas.com/movies/whatson"
)
