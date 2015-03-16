# import json
import random

from flask import Flask, Response, request, url_for, render_template

from heathskin import card_database, game_state, tail_thread

app = Flask(__name__, static_url_path='', static_folder='../public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))

# @app.route('/random_card.json')
# def card_handler():
#     card_db = card_database.CardDatabase.get_database()
#     hand = random.sample(card_db.search(health=2), 5)
#     return Response(json.dumps(hand), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

# @app.route('/random_card_image') # dev sandboxing; also broken
# def imgur():
#     card_db = card_database.CardDatabase.get_database()
#     hand = random.sample(card_db.search(health=2), 5)
#     temp = ''
#     for card in hand:
#         temp += (str(make_image_url(id=card['id'])) + ' ')
#     return temp


app_state = {}
@app.route('/update_state',  methods=['GET', 'POST'])
def update_state():
    global app_state
    content = request.json
    for k, v in content.items():
        if k in app_state:
            print "updating app_state: key={}, old={}, new={}".format(k, app_state[k], v)
        else:
            print "adding new app_state: key={} value={}".format(k, v)

        app_state[k] = v

    return ""

@app.route("/balls")
def balls():
    global app_state
    hand = {}
    print "app_state: ", app_state
    # return ""
    for card in app_state['friendly_hand']:
        hand[card] = {'name': card,
                      'imgurl': ('card_images/banners/' + card + '_banner.png')}
    print "hand dict: ", hand
    print "dict len: ", len(hand)
    return render_template('jquerytest.html',
                            cards=hand,
                            handsize=len(hand))
    # return "friendly hand: {}".format(app_state['friendly_hand'])

@app.route('/jque')
def jquerytest():
    card_db = card_database.CardDatabase.get_database()
    dev_hand = random.sample(card_db.search(health=2), 20)
    hand = {}
    for card in dev_hand:
        hand[card['name']] = {'name': card['name'],
                              'imgurl': ('card_images/banners/' + card['id'] + '_banner.png'),
                              'cost': card['cost']}
    print "hand: ", hand
    for card in hand:
        print "\n" + card
        print "hand[card]: ", hand[card]
        print "hand[card]['name']: ", hand[card]['name']
    return render_template('jquerytest.html',
                            cards=hand)

@app.route('/images_from_hand')
def display_hand():
    card_db = card_database.CardDatabase.get_database()
    dev_hand = random.sample(card_db.search(health=2), 20)
    hand = {}
    for card in dev_hand:
        hand[card['name']] = {'name': card['name'],
                              'imgurl': ('card_images/banners/' + card['id'] + '_banner.png')}
    print "hand: ", hand
    for card in hand:
        print "\n" + card
        print "hand[card]: ", hand[card]
        print "hand[card]['name']: ", hand[card]['name']
    return render_template('template.html',
                            cards=hand)

if __name__ == '__main__':
    app.debug = True
    app.run(port=3000)

# <!doctype html>
# <title>Heathskin</title>
# <ul class=deckcolumn>
# {% for name in filenames %}
#     <div><img src="{{name}}" height="20"></div>
# {% endfor %}
# {% for title in cardnames %}
#     <div>{{title}}</div>
# {% endfor %}
# </ul>

# {% for card in cards %}
#     <div>{{ card['name'] }}<img src="{{card['imgurl']}}" height="20"></div>
# {% endfor %}
