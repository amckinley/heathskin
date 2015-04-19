from flask import Flask, request, render_template, abort

import deck

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('deck_upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        player_deck = deck.deck_from_file(file)
    else:
        abort(505)
    print_deck = deck.Deck.get_card_names(player_deck)
    card_names = []
    for card in print_deck:
        card_names.append(card['name'])
    return str(card_names)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=4000,
        debug=True
    )
