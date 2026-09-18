from playwright.sync_api import sync_playwright
import requests
import os
import time


# ==========================
# SETTINGS
# ==========================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


movies_to_watch = [
    "Dune",
    "Doomsday",
    "Avengers"
]


# ==========================
# TELEGRAM
# ==========================

def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )


# ==========================
# VOX CHECKER
# ==========================

def check_vox():

    print("Checking VOX Egypt")

    url = (
        "https://egy.voxcinemas.com/"
        "api/tracking/ga4/view_item_list"
        "?identifier=ns&zone=3"
    )


    try:

        response = requests.get(
            url,
            timeout=30
        )


        data = response.text.lower()


        found = []


        for movie in movies_to_watch:

            if movie.lower() in data:

                found.append(movie)



        if found:

            message = (
                "🎬 Movie Alert!\n\n"
                "Cinema: VOX Egypt\n\n"
                +
                "\n".join(found)
                +
                "\n\n"
                "https://egy.voxcinemas.com/movies/whatson"
            )

            send_message(message)



    except Exception as e:

        print(
            "VOX error:",
            e
        )



# ==========================
# DISTRICT 5 CHECKER
# ==========================

def check_scene():

    print("Checking Scene District 5")


    url = (
        "https://district5.scenecinemas.com/home"
    )


    try:

        with sync_playwright() as p:


            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled"
                ]
            )


            page = browser.new_page()


            page.goto(
                url,
                wait_until="domcontentloaded",
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
                    "Cinema: Scene District 5\n\n"
                    +
                    "\n".join(found)
                    +
                    "\n\n"
                    + url
                )


                send_message(message)



    except Exception as e:


        print(
            "Scene error:",
            e
        )



# ==========================
# RUN CHECK
# ==========================

check_vox()

check_scene()
