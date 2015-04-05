from os import path
from urlparse import urlparse
import argparse
import shutil
import logging

import requests
from requests.exceptions import ConnectionError

from heathskin import card_database


log_fmt = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"

logging.basicConfig(format=log_fmt)
logger = logging.getLogger()

# BRM_001 mistyped on server, is solemn-vigil1, should be solemn-vigil
def replacer(text):
    rep = {" ": "-", "\'": "", ":": "", "!": "", ".": ""}
    if "Stranglethorn" in text: # misspelled on scraped server
        text = text.replace(text, "strangelthorn-tiger") # mandatory to catch by toe
    for i, j in rep.iteritems():
        text = text.replace(i, j).lower()
    return text

def fetch_file(src_url, dest_path, dry_run=False):
    short_src_name = urlparse(src_url).path
    short_dest_name = path.basename(dest_path)
    logger.debug("fetching from: %s *** writing to: %s", short_src_name, short_dest_name)
    if path.exists(dest_path):
        logger.debug("path already exists, not fetching")
        return True
    if dry_run:
        logger.info("Not fetching %s for dry_run", src_url)
        return True
    try:
        res = requests.get(src_url, stream=True)
    except ConnectionError:
        logger.exception("Error while fetching file %s", src_url)
        return False

    if res.status_code == 200:
        logger.info("fetch successful: %s", dest_path)
        with open(dest_path, "wb") as f:
            res.raw.decode_content = True
            shutil.copyfileobj(res.raw, f)

    else:
        logger.info("status code: %s *** %s not found", res.status_code, dest_path)

    return res.status_code == 200


def scraper(parent_folder="01", year="4", card_list=None, dry_run=False):
    banner_url_base = "http://www.hearthstonetopdecks.com/wp-content/uploads/201{}/{}/sm-card-{}.png"
    card_url_base = "http://www.hearthstonetopdecks.com/wp-content/uploads/201{}/{}/{}.png"
    # log = ([u'voljin', u'GVG_014'], [u'warbot', u'GVG_051'], [u'wee-spellstopper', u'GVG_122'], [u'whirling-zap-o-matic', u'GVG_037'])
    log = []

    for card in card_list:
        card_target_path = "data/card_images/{}.png".format(card[1])
        banner_target_path = "data/card_images/banners/{}_banner.png".format(card[1])
        card_url = card_url_base.format(year, parent_folder, card[0])
        banner_url = banner_url_base.format(year, parent_folder, card[0])

        res = fetch_file(card_url, card_target_path, dry_run=dry_run)
        not_found = False
        if not res:
            not_found = True

        res = fetch_file(banner_url, banner_target_path, dry_run=dry_run)
        if not res:
            not_found = True

        if not_found:
            log.append(card)

    if len(log) > 0 and int(parent_folder) < 12:
        logger.info("******* parent_folder %s Complete *******", parent_folder)
        logger.info("Number of files remaining: %d", (len(log) / 2))
        scraper(parent_folder=str((int(parent_folder)+1)).zfill(2), card_list=log, dry_run=dry_run)

    if len(log) > 0 and int(parent_folder) == 12 and year == "4":
        logger.info("******* year 201%s Complete *******", year)
        logger.info("Number of files remaining: %d", (len(log) / 2))
        scraper(year="5", card_list=log, dry_run=dry_run)

    logger.info("Not Found: %s", log)

def main(args):
    if args.debug:
        logger.level = logging.DEBUG
    else:
        logger.level = logging.INFO

    # stop spam from requests module
    logging.getLogger("requests").setLevel(logging.WARNING)

    card_db = card_database.CardDatabase.get_database()
    collectible_card_names = card_db.search(collectible=True)
    get_scraped = []
    for card_name in collectible_card_names:
        card_name['name'] = replacer(card_name['name'])
        get_scraped.append([card_name['name'], card_name['id']])
    try:
        scraper("03", year=args.year, card_list=get_scraped, dry_run=args.dry_run)
    except KeyboardInterrupt:
        logger.error("Got SIGINT, shutting down")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='scrap some skins')
    parser.add_argument('--dry-run', default=False, action="store_true")
    parser.add_argument('--debug', default=False, action='store_true')
    parser.add_argument('--year', default="4")
    args = parser.parse_args()

    main(args)

