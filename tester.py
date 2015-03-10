import json
import random
from flask import Flask, Response, request

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

@app.route('/random_card.json')
def rand_card_handler():
    with open('data/AllSets.json', 'r') as file:
        card_data = json.loads(file.read())

    all_cards = []
    for set_name, card_set in card_data.items():
        for card in card_set:
            all_cards.append(card)

    card = random.sample(all_cards, 5)
    return Response(json.dumps(card), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

if __name__ == '__main__':
    app.debug = True
    app.run(port=3000)
