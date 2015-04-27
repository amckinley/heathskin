import os
from collections import defaultdict

from flask import render_template, session, request, \
    jsonify, abort, make_response, redirect
from flask.ext.security import login_required, auth_token_required
from flask.ext.login import current_user
from werkzeug import secure_filename

from heathskin.frontend import app, db
from heathskin.models import Deck, Card, CardDeckAssociation, GameHistory
from heathskin.game_universe import GameUniverse
from heathskin import card_database, utils, deck


logger = app.logger


@app.route('/deck_list')
def deck_list_unfiltered():
    return deck_list("")


@app.route('/deck_list/<string:filter_string>')
@login_required
def deck_list(filter_string):

    card_db = card_database.CardDatabase.get_database()
    universe = GameUniverse.get_universe()
    game_state = universe.get_latest_game_state_for_user(current_user.get_id())

    if not game_state:
        return "no game states found for user id {}".format(
            current_user.get_id())

    # XXX hard coding deck number 1
    d = Deck.query.filter_by(id=current_user.get_id()).first()

    to_return = "deck: " + d.name + " " + d.user.email
    played_cards = game_state.get_played_cards(player="FRIENDLY")
    print (game_state.get_entity_counts_by_zone())

    for c in d.cards:
        card = card_db.get_card_by_id(c.card.blizz_id)
        number_in_deck = c.count

        show_card = True

        if (len(filter_string) > 0):
            show_card = False
            if ('mechanics' in card):
                for m in card['mechanics']:
                    if m.lower() == filter_string.lower():
                        show_card = True

        for entity in played_cards:
            if entity.card_id == card['id']:
                #print ("entity.card_id= " + entity.card_id + "  " + card['id'])
                number_in_deck -= 1
                if number_in_deck < 1:
                    show_card = False

        if show_card:
            to_return += "<br>" + card['name'] + " (" + str(number_in_deck) + ")"
            if 'mechanics' in card:
                for m in card['mechanics']:
                    to_return += " (" + m + ")"
            to_return += "</br>"
    return to_return

@app.route('/entity_dump')
@login_required
def entity_dump():
    u = GameUniverse.get_universe()
    game_state = u.get_latest_game_state_for_user(current_user.get_id())
    if not game_state:
        return "no game state found for user {}".format(current_user.get_id())
    return str(set([e.card_id for e in game_state.entities.values()]))

@app.route('/')
def index():

    return render_template('temphome.html')


# @app.route('/')
# @login_required
# def index():
#     decknames = [d.name for d in current_user.decks]
#     print decknames
#     return render_template('index.html', decknames=decknames)


@app.route('/uploadform')
@login_required
def upload_form():
    return render_template('deck_upload.html')


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    if not file:
        abort(505)

    # card_db = card_database.CardDatabase.get_database()
    player_deck = deck.deck_from_file(file)
    filename = secure_filename(file.filename)
    deck_name = os.path.basename(filename).split(".")[0]
    d = Deck(user_id=current_user.get_id(), name=deck_name)

    card_counts = defaultdict(int)
    ids_to_objs = {}
    for b_id in player_deck.blizz_ids:
        card_obj = Card.query.filter_by(blizz_id=b_id).first()
        card_counts[card_obj.blizz_id] += 1
        ids_to_objs[card_obj.blizz_id] = card_obj

    for blizz_id, cnt in card_counts.items():
        card_obj = ids_to_objs[blizz_id]
        cda = CardDeckAssociation(card=card_obj, deck=d, count=cnt)
        db.session.add(cda)

    db.session.add(d)
    db.session.commit()

    return redirect("/")


@app.route("/current_hand")
@login_required
def deck_tracker():
    return render_template( 'cur_hand.html')

@app.route("/get_named_cards")
@login_required
def get_names():
    card_db = card_database.CardDatabase.get_database()
    universe = GameUniverse.get_universe()

    game_state = universe.get_latest_game_state_for_user(current_user.get_id())
    if not game_state:
        return "no game states found for user id {}".format(
            current_user.get_id())

    our_hero = game_state.entities[4]
    enemy_hero = game_state.entities[36]

    return str([our_hero.name, enemy_hero.name])

    card_names = [card_db.get_card_by_id(e.card_id)['name']
        for e in game_state.entities if e.card_id]

    return str(card_names)


@app.route("/deck_maker")
@login_required
def deck_maker_init():
    card_db = card_database.CardDatabase.get_database()
    possible_names = card_db.get_all_valid_names()
    # possible_ids = card_db.cards_by_ids()

    if "building_deck" not in session:
        session['building_deck'] = []

    selected_names = session['building_deck']
    selected_ids = []
    for card in selected_names:
        search_list = (card_db.search(name=card))[0]
        selected_ids.append(search_list['id'])
    print "selected_ids: ", selected_ids


    # return render_template("deck_maker.html", validcards=possible_names)
    return render_template(
        "deck_maker.html",
        validcards=possible_names,
        pickedcards=selected_ids)


@app.route("/deck_maker", methods=['POST'])
@login_required
def deck_maker():
    card = request.form['text']
    print "text: ", card

    card_db = card_database.CardDatabase.get_database()
    possible_names = card_db.get_all_valid_names()

    if "building_deck" not in session:
        session['building_deck'] = []

    building_deck = session['building_deck']

    if card in possible_names and card not in building_deck and len(building_deck) < 30:
        building_deck.append(card)
        print "building_deck: ", building_deck
        print "len(building_deck): ", len(building_deck)
        return redirect("/deck_maker")
    else:
        return "Invalid State"


@app.route("/universe_dump")
def universe_dump():
    universe = GameUniverse.get_universe()
    return str(universe.get_session_dump())


@app.route('/upload_lines', methods=['POST'])
@auth_token_required
def upload_lines():
    if 'session_start_time' not in session:
        logger.error("user tried to upload line without session")
        abort(400)

    GameUniverse.lock_universe()
    # this is where we actually update the game with the incoming log line
    universe = GameUniverse.get_universe()

    results = request.get_json()
    if "log_lines" in results:
        log_lines = results["log_lines"]
    else:
        logger.error("tried to upload without the right json")
        abort(400)

    for l in log_lines:
        universe.feed_line(
            user_id=current_user.get_id(),
            session_start=session['session_start_time'],
            log_line=l)

    GameUniverse.unlock_universe()

    logger.debug(
        "got %d log lines from user %s",
        len(log_lines), current_user.get_id())
    return ''


@app.route('/start_session', methods=['POST'])
@auth_token_required
def start_session():
    session['session_start_time'] = utils.get_datetime_as_iso8601()
    # magical persistence cookie
    resp = make_response("")
    # resp.set_cookie('FOO', get_server_for_user(current_user.get_id()))

    logger.info("starting session for user %s", current_user.get_id())
    return resp


@app.route('/api/help', methods=['GET'])
def help():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)


@auth_token_required
@app.route('/history')
def history():
    universe = GameUniverse.get_universe()
    return render_template('history.html', history=GameHistory.query)
