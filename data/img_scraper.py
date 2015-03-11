import requests
import shutil

def main():
    url_base = "http://wow.zamimg.com/images/hearthstone/cards/enus/animated/{}_premium.gif"
    card_id = "EX1_067"
    file_name = "data/card_images/{}.gif".format(card_id)

    res = requests.get(url_base.format(card_id), stream=True)

    if res.status_code == 200:
        with open(file_name, 'wb') as f:
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, f)

if __name__ == '__main__':
    main()
