import json
import random

from flask import Flask, Response, request, redirect, url_for

from heathskin import card_database

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/random_card.json')
def card_handler():
    card_db = card_database.CardDatabase.get_database()
    hand = random.sample(card_db.search(health=2), 5)
    return Response(json.dumps(hand), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

def make_image_url():
    # return redirect('/card_images/EX1_066.png')
    return url_for('/card_images', filename='EX1_066.png')

@app.route('/random_card_image.json')
def imgur():
    card_db = card_database.CardDatabase.get_database()
    hand = random.sample(card_db.search(health=2), 5)
    print url_for('card_handler', next='/')

    # return hand[0]['id']
    # return url_for('/card_images', filename=hand[0]['id'])
    # return url_for('card_images', filename='EX1_066.png')
    # for card in hand:
    # dest = url_for('/card_images', filename='EX1_066.png')

if __name__ == '__main__':
    app.debug = True
    app.run(port=3000)
