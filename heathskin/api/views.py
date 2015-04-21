from heathskin.game_universe import GameUniverse
from heathskin import card_database
from heathskin.models import GameHistory
from heathskin.frontend import app
from flask.ext.login import current_user
from flask import jsonify

@app.route("/api/zone/<string:zone>/")
def get_entities_by_zone(zone):
    zone = zone.replace("_", " ")
    GameUniverse.lock_universe()
    universe = GameUniverse.get_universe()
    card_db = card_database.CardDatabase.get_database()
    game_state = universe.get_latest_game_state_for_user(current_user.get_id())
    if game_state:
        entities = game_state.entities
    else:
        entities = {}
    GameUniverse.unlock_universe()
    return jsonify ({"entities": [card_db.get_card_by_id(e.card_id)
        for e in entities.values() if e.get_tag('ZONE') == zone and e.card_id]})

@app.route("/api/current_hand")
def get_current_hand():
    return jsonify({"cards": _get_hand()})

@app.route("/api/history")
def game_history():
    return jsonify({"data": [{
          "user_id": result.user_id,
          "opponent": result.opponent,
          "hero": result.hero,
          "turns": result.turns,
          "p1_won": result.won,
          "player1": result.player1,
          "player2": result.player2,
        } for result in GameHistory.query.all()]})

def _get_hand():
    GameUniverse.lock_universe()
    universe = GameUniverse.get_universe()
    card_db = card_database.CardDatabase.get_database()

    game_state = universe.get_latest_game_state_for_user(current_user.get_id())
    if game_state:
        hand = game_state.get_friendly_hand()
    else:
        hand = []

    hand_ids = [card_db.get_card_by_id(e.card_id) for e in hand if e.card_id]
    GameUniverse.unlock_universe()

    return hand_ids
