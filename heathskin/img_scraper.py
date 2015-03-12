import requests
import shutil
from heathskin import card_database

def main():
    #           http://wow.zamimg.com/images/hearthstone/cards/enus/original/EX1_066.png
    url_base = "http://wow.zamimg.com/images/hearthstone/cards/enus/original/{}.png"
    # gold card url
    gold_url_base = "http://wow.zamimg.com/images/hearthstone/cards/enus/animated/{}_premium.gif"
    # card_id = "EX1_066_premium"


    card_db = card_database.CardDatabase.get_database()
    collectible_card_names = [c['id'] for c in card_db.all_collectible_cards]
    for card_id in collectible_card_names:
        file_name = "data/card_images/{}.png".format(card_id)
        gold_file_name = "data/card_images/{}_premium.gif".format(card_id)
        res = requests.get(url_base.format(card_id), stream=True)

        if res.status_code == 200:
            print "file_name: ", file_name
            with open(file_name, 'wb') as f:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, f)

        res = requests.get(gold_url_base.format(card_id), stream=True)
        if res.status_code == 200:
            print "gold_file_name: ", gold_file_name
            with open(gold_file_name, 'wb') as f:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, f)



        else:
            print res.status_code
            return
if __name__ == '__main__':
    main()
