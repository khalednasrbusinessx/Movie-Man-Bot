from playwright.sync_api import sync_playwright
import requests
import os
import json
import time
import re


BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


WATCHLIST_FILE = "watchlist.json"
OFFSET_FILE = "telegram_offset.txt"


# ==========================
# WATCHLIST
# ==========================

def load_watchlist():

    with open(WATCHLIST_FILE, "r") as file:
        return json.load(file)



def save_watchlist(movies):

    with open(WATCHLIST_FILE, "w") as file:
        json.dump(
            movies,
            file,
            indent=4
        )


# ==========================
# TEXT CLEANING
# ==========================

def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9 ]",
        " ",
        text
    )

    return text



def movie_found(movie, text):

    movie = clean_text(movie)
    text = clean_text(text)

    return movie in text



# ==========================
# TELEGRAM
# ==========================

def send_message(text):

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )



# ==========================
# TELEGRAM COMMANDS
# ==========================

def get_offset():

    try:

        with open(OFFSET_FILE,"r") as file:
            return int(file.read())

    except:

        return 0



def save_offset(offset):

    with open(OFFSET_FILE,"w") as file:
        file.write(
            str(offset)
        )



def check_commands():

    offset = get_offset()


    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/getUpdates"
        f"?offset={offset+1}"
    )


    data = requests.get(url).json()


    movies = load_watchlist()


    for update in data["result"]:


        message = update.get(
            "message",
            {}
        )


        text = message.get(
            "text",
            ""
        )


        if text.startswith("/add"):

            movie = text.replace(
                "/add",
                ""
            ).strip()


            if movie:

                if movie not in movies:

                    movies.append(movie)

                    save_watchlist(
                        movies
                    )


                    send_message(
                        "✅ Added:\n"
                        + movie
                    )



        elif text.startswith("/stop"):

            movie = text.replace(
                "/stop",
                ""
            ).strip()


            movies = [
                m for m in movies
                if m.lower() != movie.lower()
            ]


            save_watchlist(
                movies
            )


            send_message(
                "🛑 Removed:\n"
                + movie
            )



        elif text.startswith("/list"):

            send_message(
                "🎬 Watchlist:\n\n"
                +
                "\n".join(movies)
            )



        elif text.startswith("/help"):

            send_message(
                "Commands:\n\n"
                "/add Movie Name\n"
                "/stop Movie Name\n"
                "/list"
            )



        save_offset(
            update["update_id"]
        )



# ==========================
# VOX
# ==========================

def check_vox():

    print("Checking VOX")


    movies = load_watchlist()


    url = (
        "https://egy.voxcinemas.com/"
        "api/tracking/ga4/"
        "view_item_list"
        "?identifier=ns&zone=3"
    )


    text = requests.get(url).text


    found = []


    for movie in movies:

        if movie_found(
            movie,
            text
        ):

            found.append(movie)



    if found:

        send_message(
            "🎬 VOX Egypt\n\n"
            +
            "\n".join(found)
        )



# ==========================
# SCENE
# ==========================

def check_scene():

    print("Checking Scene")


    movies = load_watchlist()


    url = (
        "https://district5.scenecinemas.com/home"
    )


    with sync_playwright() as p:


        browser = p.chromium.launch(
            headless=True
        )


        page = browser.new_page()


        page.goto(
            url,
            timeout=60000
        )


        time.sleep(5)


        text = page.content()


        browser.close()



    found=[]


    for movie in movies:

        if movie_found(
            movie,
            text
        ):

            found.append(movie)



    if found:

        send_message(
            "🎬 Scene District 5\n\n"
            +
            "\n".join(found)
        )



# ==========================
# START
# ==========================

check_commands()

check_vox()

check_scene()
