


# def deck_from_path(path):
#     with open(path) as f:
#         # card_names = [n.rstrip() for n in f.readlines()]

#         return deck_from_file(f)


# def deck_from_file(deck_file):
#     card_db = card_database.CardDatabase.get_database()
#     card_list = list()
#     for n in deck_file:
#         card_name = n.rstrip()
#         res = card_db.search(name=card_name)
#         if len(res) == 1:
#             card_list.append(res[0]['id'])
#         else:
#             raise Exception(
#                 "couldnt find card with name '{}'. len(res) = {}".format(
#                     card_name, len(res)))

#     return Deck(card_list)

