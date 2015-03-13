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

@app.route('/card_images/<card_id>')
def make_image_url(id):
    return url_for('make_image_url', card_id=id) + '.png'

@app.route('/random_card_image.json')
def imgur():
    card_db = card_database.CardDatabase.get_database()
    hand = random.sample(card_db.search(health=2), 5)
    temp = ''
    for card in hand:
        temp += (str(make_image_url(id=card['id'])) + ' ')
    # print temp
    return temp


if __name__ == '__main__':
    app.debug = True
    app.run(port=3000)
