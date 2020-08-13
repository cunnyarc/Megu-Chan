try:
    from requests_html import HTMLSession
except ImportError:
    print("==============================================")
    print("Please download requests-html for this to work!")
    print("https://pypi.org/project/requests-html/")
import requests

'''
Author : Glitchy-Chan
'''


class TWDE:
    def __init__(self):
        self.web = HTMLSession()
        self.source = self.web.get("https://www.thiswaifudoesnotexist.net/")

    def get_link(self):
        self.source.html.render()
        waifu = self.source.html.xpath('/html/body/div[1]/div/div[1]/img')
        self.web.close()

        return f"http://{str(waifu)[23:-3]}"

    def get_image(self, location):
        self.source.html.render()
        waifu = self.source.html.xpath('/html/body/div[1]/div/div[1]/img')
        image = f"http://{str(waifu)[23:-3]}"

        r = requests.get(image)

        with open(f"./{location}/{str(waifu)[53:-3]}", 'wb') as im:
            for chunk in r:
                im.write(chunk)

        self.web.close()
