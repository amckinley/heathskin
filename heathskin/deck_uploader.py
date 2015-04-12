import os
from flask import Flask, request, redirect, url_for, render_template, abort
from werkzeug import secure_filename

import deck
import card_database

app = Flask(__name__)

# def deck_from_file(path):
#     with open(path) as f:
#         card_names = [n.rstrip() for n in f.readlines()]

    # return Deck(card_names)

@app.route('/')
def index():
    return render_template('deck_upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        player_deck = deck.deck_from_file(file)
    else:
        abort(505)
    print_deck = []
    for card in player_deck:
        print_deck.append(card_database.get_card_by_id(card)['name'])
    return str(print_deck)
    return "whoops"
    # return player_deck

# def text_to_deck(text_deck):
#     print text_deck
#     player_deck = []
#     # for card in text_deck:
#     player_deck.append(deck.Deck(text_deck))
#     return player_deck


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=4000,
        debug=True
    )
