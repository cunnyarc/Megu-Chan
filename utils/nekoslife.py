import requests

import errors

neko = "https://nekos.life/api/v2"


def imgSFW(enpoint: str):
    sfw = {
        "tickle": "/img/tickle",
        "slap": "/img/slap",
        "poke": "/img/poke",
        "pat": "/img/pat",
        "neko": "/img/neko",
        "meow": "/img/meow",
        "lizard": "/img/lizard",
        "kiss": "/img/kiss",
        "hug": "/img/hug",
        "foxGirl": "/img/fox_girl",
        "feed": "/img/feed",
        "cuddle": "/img/cuddle",
        "nekoGif": "/img/ngif",
        "kemonomimi": "/img/kemonomimi",
        "holo": "/img/holo",
        "smug": "/img/smug",
        "baka": "/img/baka",
        "woof": "/img/woof",
        "wallpaper": "/img/wallpaper",
        "goose": "/img/goose",
        "gecg": "/img/gecg",
        "avatar": "/img/avatar",
        "waifu": "/img/waifu"
    }
    if enpoint is None:
        raise errors.EmptyArgument("Nyaa! You have to define a valid argument \n "
                                   f"Arguements:{sfw}")

    if enpoint not in sfw:
        raise errors.InvalidArgument("Nyaa! That argument does not exist \n"
                                     f"Arguements:{sfw}")

    try:
        r = requests.get(f'{neko}/{sfw[enpoint]}').json()

    except Exception as e:
        raise errors.NothingFound(e)

    return r['url']


def imgNSFW(enpoint: str):
    nsfw = {
        "randomHentaiGif": "/img/Random_hentai_gif",
        "pussy": "/img/pussy",
        "nekoGif": "/img/nsfw_neko_gif",
        "neko": "/img/lewd",
        "lesbian": "/img/les",
        "kuni": "/img/kuni",
        "cumsluts": "/img/cum",
        "classic": "/img/classic",
        "boobs": "/img/boobs",
        "bJ": "/img/bj",
        "anal": "/img/anal",
        "avatar": "/img/nsfw_avatar",
        "yuri": "/img/yuri",
        "trap": "/img/trap",
        "tits": "/img/tits",
        "girlSoloGif": "/img/solog",
        "girlSolo": "/img/solo",
        "pussyWankGif": "/img/pwankg",
        "pussyArt": "/img/pussy_jpg",
        "kemonomimi": "/img/lewdkemo",
        "kitsune": "/img/lewdk",
        "keta": "/img/keta",
        "holo": "/img/hololewd",
        "holoEro": "/img/holoero",
        "hentai": "/img/hentai",
        "futanari": "/img/futanari",
        "femdom": "/img/femdom",
        "feetGif": "/img/feetg",
        "eroFeet": "/img/erofeet",
        "feet": "/img/feet",
        "ero": "/img/ero",
        "eroKitsune": "/img/erok",
        "eroKemonomimi": "/img/erokemo",
        "eroNeko": "/img/eron",
        "eroYuri": "/img/eroyuri",
        "cumArts": "/img/cum_jpg",
        "blowJob": "/img/blowjob",
        "spank": "/img/spank",
        "gasm": "/img/gasm"
    }

    if enpoint is None:
        raise errors.EmptyArgument("Nyaa! You have to define a valid argument \n "
                                   f"Arguements:{nsfw}")

    if enpoint not in nsfw:
        raise errors.InvalidArgument("Nyaa! That argument does not exist \n"
                                     f"Arguements:{nsfw}")

    try:
        r = requests.get(f'{neko}/{nsfw[enpoint]}').json()

    except Exception as e:
        raise errors.NothingFound(e)

    return r['url']


def eightball():
    r = requests.get(f'{neko}/8ball').json()
    return {"text": r['response'], "url": r['url']}


def owoify(text: str):
    if text is None:
        raise errors.EmptyArgument("Nyaa! You have to give me some text to owoify")

    try:
        r = requests.get(f'{neko}/owoify?text={text}').json()

    except Exception as e:
        raise errors.NothingFound(e)

    return r['owo']


def textcat():
    try:
        r = requests.get(f'{neko}/cat').json()
        return r['cat']
    except Exception as e:
        raise errors.NothingFound(e)


def why():
    try:
        r = requests.get(f'{neko}/why').json()
        return r['why']
    except Exception as e:
        raise errors.NothingFound(e)


def fact():
    try:
        r = requests.get(f'{neko}/fact').json()
        return r['fact']
    except Exception as e:
        raise errors.NothingFound(e)