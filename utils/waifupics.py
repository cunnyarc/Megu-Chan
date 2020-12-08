import requests

waifu = "https://waifu.pics/api"


def imgSFW(endpoint: str):
    sfw = {
        "waifu": "/sfw/waifu",
        "neko": "/sfw/neko",
        "shinobu": "/sfw/shinobu",
        "megumin": "/sfw/megumin",
        "bully": "/sfw/bully",
        "cuddle": "/sfw/cuddle",
        "cry": "/sfw/cry",
        "hug": "/sfw/hug",
        "kiss": "/sfw/kiss",
        "lick": "/sfw/lick",
        "pat": "/sfw/pat",
        "smug": "/sfw/smug",
        "smile": "/sfw/smile",
        "wave": "/sfw/wave",
        "highfive": "/sfw/highfive",
        "handhold": "/sfw/handhold",
        "nom": "/sfw/nom",
        "bite": "/sfw/bite",
        "glomp": "/sfw/glomp",
        "kill": "/sfw/kill",
        "slap": "/sfw/slap",
        "happy": "/sfw/happy",
        "wink": "/sfw/wink",
        "poke": "/sfw/poke",
        "dance": "/sfw/dance",
        "cringe": "/sfw/cringe",
        "blush": "/sfw/blush"
    }

    if endpoint is None:
        print("Oi! You have to define a valid argument \n "
              f"Arguements:{sfw}")

    if endpoint not in sfw:
        print("Oi! That argument does not exist \n"
              f"Arguements:{sfw}")

    try:
        r = requests.get(f"{waifu}/{sfw[endpoint]}").json()

    except Exception as e:
        print(e)

    return r['url']


def imgNSFW(endpoint: str):
    nsfw = {
        "waifu": "/nsfw/waifu",
        "neko": "/nsfw/neko",
        "trap": "/nsfw/trap",
        "blowjob": "/nsfw/blowjob"
    }

    if endpoint is None:
        print("Oi! You have to define a valid argument \n"
              f"Arguements:{nsfw}")

    if endpoint not in nsfw:
        print("Oi! That argument does not exist \n"
              f"Arguements:{nsfw}")

    try:
        r = requests.get(f"{waifu}/{nsfw[endpoint]}").json()

    except Exception as e:
        print(e)

    return r['url']
