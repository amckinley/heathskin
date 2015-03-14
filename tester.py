# import json
import random

from flask import Flask, Response, request, url_for, render_template

from heathskin import card_database
import heathskin

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

# @app.route('/random_card.json')
# def card_handler():
#     card_db = card_database.CardDatabase.get_database()
#     hand = random.sample(card_db.search(health=2), 5)
#     return Response(json.dumps(hand), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

@app.route('/random_card_image') # dev sandboxing
def imgur():
    card_db = card_database.CardDatabase.get_database()
    hand = random.sample(card_db.search(health=2), 5)
    temp = ''
    for card in hand:
        temp += (str(make_image_url(id=card['id'])) + ' ')
    return temp

@app.route('/images_from_hand')
def display_hand():
    card_db = card_database.CardDatabase.get_database()
    hand = random.sample(card_db.search(health=2), 20)
    filenames = []
    cardnames = []
    for card in hand:
        filenames.append('card_images/banners/' + card['id'] + '_banner.png')
        cardnames.append(card['name'])
    return render_template('template.html',
                            filenames=filenames,
                            cardnames=cardnames)


if __name__ == '__main__':
    app.debug = True
    app.run(port=3000)
