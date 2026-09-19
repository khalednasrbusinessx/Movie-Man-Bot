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


def send_watchlist(movies):

    if movies:
        send_message(
            "🎬 Watchlist:\n\n" + "\n".join(movies)
        )
    else:
        send_message("🎬 Watchlist is empty")



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

    response = requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

    response.raise_for_status()



# ==========================
# TELEGRAM OFFSET
# ==========================

def get_offset():

    try:

        with open(OFFSET_FILE, "r") as file:
            return int(file.read())

    except:

        return 0



def save_offset(offset):

    with open(OFFSET_FILE, "w") as file:
        file.write(
            str(offset)
        )



# ==========================
# TELEGRAM COMMANDS
# ==========================

def check_commands():

    offset = get_offset()


    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/getUpdates"
        f"?offset={offset + 1}"
    )


    data = requests.get(url).json()


    movies = load_watchlist()


    highest_update_id = offset



    for update in data.get("result", []):


        update_id = update["update_id"]


        if update_id > highest_update_id:

            highest_update_id = update_id



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
                "",
                1
            ).strip()



            if movie:


                if movie not in movies:


                    movies.append(movie)


                    save_watchlist(
                        movies
                    )


                    send_watchlist(movies)



        elif text.startswith("/stop"):


            movie = text.replace(
                "/stop",
                "",
                1
            ).strip()



            new_movies = [
                m for m in movies
                if m.lower() != movie.lower()
            ]



            if len(new_movies) != len(movies):


                movies = new_movies


                save_watchlist(
                    movies
                )


                send_watchlist(movies)



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
                "/list\n"
                "/help"
            )



    save_offset(
        highest_update_id
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


    response = requests.get(
        url,
        timeout=30
    )


    text = response.text


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



    found = []



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

print("Checking Telegram commands")

check_commands()


print("Checking cinemas")

check_vox()

check_scene()


send_message("✅ Movie checker completed its scheduled run.")

print("Finished")
