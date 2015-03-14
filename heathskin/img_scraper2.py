import requests
import shutil

from heathskin import card_database


def replacer(text):
    rep = {" ": "-", "\'": "", ":": "", "!": "", ".": ""}
    if "Stranglethorn" in text: # misspelled on scraped server
        text = text.replace(text, "strangelthorn-tiger") # mandatory to catch by toe
    for i, j in rep.iteritems():
        text = text.replace(i, j).lower()
    return text

def main(parent_folder="03", card_list=None):
    banner_url_base = "http://www.hearthstonetopdecks.com/wp-content/uploads/2014/{}/sm-card-{}.png"
    # log = ([u'voljin', u'GVG_014'], [u'warbot', u'GVG_051'], [u'wee-spellstopper', u'GVG_122'], [u'whirling-zap-o-matic', u'GVG_037'])
    log = []

    for card in card_list:
        # print card
        target_path = "data/card_images/banners/{}_banner.png".format(card[1])
        res = requests.get(banner_url_base.format(parent_folder, card[0]), stream=True)
        # print banner_url_base.format(parent_folder, card[0])

        if res.status_code == 200:
            print "success: ", card[1] + "  *  " + card[0]
            with open(target_path, "wb") as f:
                res.raw.decode_content = True
                shutil.copyfileobj(res.raw, f)

        if res.status_code != 200:
            log.append(card)
            print "" + str(res.status_code) + " Not Found" + "  *  " + \
            card[0] + "  *  " + card[1]

    print log
    with open("data/scraper_log.txt", "w") as f:
        for item in log:
            f.write(str(item))


    if len(log) > 0 and int(parent_folder) < 12:
        print "******* parent_folder " + parent_folder + " Complete *******"
        print "Number of files remaining: ", (len(log) / 2)
        main(str((int(parent_folder)+1)).zfill(2), log)

    print "Not Found: ", log


if __name__ == '__main__':
    card_db = card_database.CardDatabase.get_database()
    collectible_card_names = card_db.search(collectible=True)
    get_scraped = []
    for card_name in collectible_card_names:
        card_name['name'] = replacer(card_name['name'])
        get_scraped.append([card_name['name'], card_name['id']])
    main("03", get_scraped)
