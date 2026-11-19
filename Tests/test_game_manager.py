from Managers.GameManager import GameManager
from Classes.Materials import Materials
from Classes.TradeOffer import TradeOffer
from Classes.Constants import *
from Classes.DevelopmentCards import DevelopmentCard
from Classes.Hand import Hand


class TestGameManager:
    game_manager = GameManager(for_test='test_específico')

    def test_reset_values(self):
        self.game_manager.already_played_development_card = True
        self.game_manager.last_dice_roll = 4
        self.game_manager.largest_army = 5
        self.game_manager.largest_army_player = {"name": "<NAME>"}
        self.game_manager.longest_road = {"name": "<NAME>"}
        self.game_manager.board.build_town(0, 0)
        self.game_manager.board.build_city(0, 0)
        self.game_manager.board.build_town(2, 7)
        self.game_manager.development_cards_deck.draw_card()
        self.game_manager.set_turn(2)
        self.game_manager.set_whose_turn_is_it(3)
        self.game_manager.set_phase(1)
        self.game_manager.set_round(10)
        self.game_manager.agent_manager.players[0]['victory_points'] = 5

        self.game_manager.reset_game_values()

        assert self.game_manager.already_played_development_card is False
        assert self.game_manager.last_dice_roll == 0
        assert self.game_manager.largest_army_player == {} and self.game_manager.largest_army == 2
        assert self.game_manager.longest_road == {'longest_road': 4, 'player': -1}
        assert (self.game_manager.board.nodes[0]['player'] == -1 and
                self.game_manager.board.nodes[0]['has_city'] is False)
        assert (self.game_manager.board.nodes[0]['player'] == -1 and
                self.game_manager.board.nodes[0]['has_city'] is False)
        assert (self.game_manager.board.nodes[2]['player'] == -1 and
                self.game_manager.board.nodes[7]['has_city'] is False)
        assert (self.game_manager.development_cards_deck.deck != [] and
                self.game_manager.development_cards_deck.current_index == 0)
        assert (self.game_manager.turn_manager.turn == 0 and self.game_manager.turn_manager.whose_turn_is_it == 0 and
                self.game_manager.turn_manager.phase == 0 and self.game_manager.turn_manager.round == 0)
        assert self.game_manager.agent_manager.players[0]['victory_points'] == 0

    def test_give_resources(self):
        self.game_manager.reset_game_values()

        self.game_manager.last_dice_roll = 11
        # Añadimos pueblos al J0
        self.game_manager.board.nodes[20]['player'] = 0  # Un pueblo adyacente
        self.game_manager.board.nodes[13]['player'] = 0  # Un pueblo no adyacente
        self.game_manager.board.nodes[33]['player'] = 0
        self.game_manager.board.build_city(0, 33)  # Una ciudad adyacente

        # Añadimos pueblos al J2
        self.game_manager.board.nodes[10]['player'] = 2  # Un pueblo adyacente
        self.game_manager.board.nodes[39]['player'] = 2  # Un pueblo no adyacente
        self.game_manager.board.nodes[0]['player'] = 2
        self.game_manager.board.build_city(2, 0)  # Una ciudad adyacente

        self.game_manager.give_resources()

        # Comprobamos los del J0
        assert self.game_manager.agent_manager.players[0]['player'].hand.resources.cereal == 3
        assert self.game_manager.agent_manager.players[0]['resources'].resources.cereal == 3

        assert self.game_manager.agent_manager.players[0]['player'].hand.resources.mineral == 0
        assert self.game_manager.agent_manager.players[0]['resources'].resources.mineral == 0

        assert self.game_manager.agent_manager.players[0]['player'].hand.resources.clay == 0
        assert self.game_manager.agent_manager.players[0]['resources'].resources.clay == 0

        assert self.game_manager.agent_manager.players[0]['player'].hand.resources.wood == 0
        assert self.game_manager.agent_manager.players[0]['resources'].resources.wood == 0

        assert self.game_manager.agent_manager.players[0]['player'].hand.resources.wool == 0
        assert self.game_manager.agent_manager.players[0]['resources'].resources.wool == 0

        # Comprobamos los del J2
        assert self.game_manager.agent_manager.players[2]['player'].hand.resources.cereal == 0
        assert self.game_manager.agent_manager.players[2]['resources'].resources.cereal == 0

        assert self.game_manager.agent_manager.players[2]['player'].hand.resources.mineral == 0
        assert self.game_manager.agent_manager.players[2]['resources'].resources.mineral == 0

        assert self.game_manager.agent_manager.players[2]['player'].hand.resources.clay == 0
        assert self.game_manager.agent_manager.players[2]['resources'].resources.clay == 0

        assert self.game_manager.agent_manager.players[2]['player'].hand.resources.wood == 3
        assert self.game_manager.agent_manager.players[2]['resources'].resources.wood == 3

        assert self.game_manager.agent_manager.players[2]['player'].hand.resources.wool == 0
        assert self.game_manager.agent_manager.players[2]['resources'].resources.wool == 0

    def test_give_resources_after_initial_placement(self):
        # Tras la colocación inicial 'hand' y 'resources' son el mismo objeto: no se puede dar el material dos veces
        self.game_manager.reset_game_values()
        player = self.game_manager.agent_manager.players[0]
        player['player'].on_game_start = lambda board: (13, 14)
        self.game_manager.on_game_start_build_towns_and_roads(0)
        assert player['player'].hand is player['resources']

        cereal = player['resources'].resources.cereal
        self.game_manager.last_dice_roll = 9  # El nodo 13 es adyacente a un cereal con un 9
        self.game_manager.give_resources()

        assert player['resources'].resources.cereal == cereal + 1
        assert player['player'].hand.resources.cereal == cereal + 1

    def test_send_trade_to_everyone(self):
        self.game_manager.reset_game_values()
        trade = TradeOffer(Materials(1, 0, 0, 0, 0), Materials(0, 0, 1, 0, 1))

        answer_object = self.game_manager.send_trade_to_everyone(trade)

        # Todos aceptan, pero ninguno puede completrlo dado que no tienen materiales
        assert len(answer_object) == 3
        for player in range(3):
            assert answer_object[player][0]['completed'] is False
            assert answer_object[player][0]['response'] is True

        self.game_manager._give_all_resources()

        answer_object = self.game_manager.send_trade_to_everyone(trade)

        assert len(answer_object) == 1
        assert answer_object[0][0]['completed'] is True
        assert answer_object[0][0]['response'] is True

    def test__on_tradeoffer_response(self):
        self.game_manager.reset_game_values()

        giver = self.game_manager.agent_manager.players[0]
        receiver = self.game_manager.agent_manager.players[1]
        trade_offer = TradeOffer(Materials(1, 0, 0, 0, 0), Materials(0, 0, 1, 0, 1))

        response_obj = self.game_manager._on_tradeoffer_response(giver, receiver, 0, trade_offer)

        assert response_obj['response'] is True

        response_obj = self.game_manager._on_tradeoffer_response(giver, receiver, 3, trade_offer)

        assert response_obj['response'] is False

    def test__trade_with_player(self):
        self.game_manager.reset_game_values()

        self.game_manager._give_all_resources()

        response = self.game_manager._trade_with_player()

        assert response is False

        trade_offer = TradeOffer(gives=Materials(1, 0, 0, 0, 0), receives=Materials(0, 0, 1, 1, 0))
        giver = self.game_manager.agent_manager.players[0]
        receiver = self.game_manager.agent_manager.players[2]

        response = self.game_manager._trade_with_player(trade_offer, giver, receiver)

        assert response is True
        assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 26
        assert self.game_manager.agent_manager.players[2]['resources'].get_total() == 24

    def test_build_road(self):
        self.game_manager.reset_game_values()

        # No tenemos materiales suficientes así que no hará nada
        assert self.game_manager.build_road(0, 0, 1)['response'] is False

        self.game_manager.agent_manager.players[0]['resources'].add_material([MaterialConstants.CLAY,
                                                                              MaterialConstants.WOOD
                                                                              ], 1)
        # No tenemos poblado así que no hará nada
        assert self.game_manager.build_road(0, 0, 1)['response'] is False

        self.game_manager.board.nodes[0]['player'] = 0

        assert self.game_manager.build_road(0, 0, 1)['response'] is True
        assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 0

    def test_build_town(self):
        self.game_manager.reset_game_values()

        # No tenemos materiales suficientes así que no hará nada
        assert self.game_manager.build_town(0, 0)['response'] is False

        self.game_manager.agent_manager.players[0]['resources'].add_material([MaterialConstants.CEREAL,
                                                                              MaterialConstants.CLAY,
                                                                              MaterialConstants.WOOD,
                                                                              MaterialConstants.WOOL
                                                                              ], 1)
        # No tenemos carretera así que no hará nada
        assert self.game_manager.build_town(0, 0)['response'] is False

        self.game_manager.board.nodes[0]['roads'].append({'player_id': 0, 'node_id': 1})

        assert self.game_manager.build_town(0, 0)['response'] is True
        assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 0

    def test_build_city(self):
        self.game_manager.reset_game_values()

        # No tenemos materiales suficientes así que no hará nada
        assert self.game_manager.build_city(0, 0)['response'] is False

        self.game_manager.agent_manager.players[0]['resources'].add_material([MaterialConstants.CEREAL,
                                                                              MaterialConstants.MINERAL
                                                                              ], 3)
        # No tenemos poblado así que no hará nada
        assert self.game_manager.build_city(0, 0)['response'] is False

        self.game_manager.board.nodes[0]['player'] = 0

        assert self.game_manager.build_city(0, 0)['response'] is True
        assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 1

    def test_build_development_card(self):
        self.game_manager.reset_game_values()

        # No tenemos materiales suficientes así que no hará nada
        assert self.game_manager.build_development_card(0)['response'] is False

        self.game_manager.agent_manager.players[0]['resources'].add_material([MaterialConstants.CEREAL,
                                                                              MaterialConstants.MINERAL,
                                                                              MaterialConstants.WOOL
                                                                              ], 1)

        assert self.game_manager.build_development_card(0)['response'] is True
        assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 0

        self.game_manager.development_cards_deck.current_index = 25
        # No quedan más cartas que robar
        assert self.game_manager.build_development_card(0)['response'] is False

    def test_move_thief(self):
        self.game_manager.reset_game_values()

        self.game_manager.board.nodes[0]['player'] = 0
        self.game_manager.board.nodes[32]['player'] = 3

        self.game_manager.agent_manager.players[3]['resources'].add_material([MaterialConstants.CEREAL,
                                                                              MaterialConstants.MINERAL,
                                                                              MaterialConstants.WOOL
                                                                              ], 1)
        self.game_manager.move_thief(9, 3)
        assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 1
        assert self.game_manager.agent_manager.players[3]['resources'].get_total() == 2

    def test__steal_from_player(self):
        self.game_manager.reset_game_values()
        self.game_manager.agent_manager.actual_player = 0

        self.game_manager._give_all_resources()

        material = self.game_manager._steal_from_player(1)

        assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 26
        assert self.game_manager.agent_manager.players[1]['resources'].get_total() == 24
        assert self.game_manager.agent_manager.players[0]['resources'].get_from_id(material) == 6
        assert self.game_manager.agent_manager.players[1]['resources'].get_from_id(material) == 4

    def test_on_game_start_build_towns_and_roads(self):
        self.game_manager.reset_game_values()

        valid_nodes = self.game_manager.board.valid_starting_nodes()

        node, road = self.game_manager.on_game_start_build_towns_and_roads(0)

        assert node in valid_nodes
        assert road in self.game_manager.board.nodes[node]['adjacent']

    def test_longest_road(self):
        self.game_manager.reset_game_values()
        longest_road = {'longest_road': 4, 'player': -1}

        for case in range(4):
            if case == 0:  # Caso 1: Aún no hay nadie con 5 o más caminos
                self.game_manager.board.nodes[0]['player'] = 0
                self.game_manager.board.build_road(0, 0, 1)
                self.game_manager.board.build_road(0, 1, 2)
                self.game_manager.board.build_road(0, 0, 8)

            if case == 1:  # Caso 2: Hay un jugador con 5 o más caminos
                self.game_manager.board.build_road(0, 8, 9)
                self.game_manager.board.build_road(0, 9, 10)

            if case == 2:  # Caso 3: Otro jugador tiene igual cantidad de caminos que el que poseía el camino más largo
                self.game_manager.board.nodes[17]['player'] = 1
                self.game_manager.board.build_road(1, 17, 18)
                self.game_manager.board.build_road(1, 18, 19)
                self.game_manager.board.build_road(1, 19, 20)
                self.game_manager.board.build_road(1, 20, 31)
                self.game_manager.board.build_road(1, 31, 32)

            if case == 3:  # Caso 4: Otro jugador tiene más caminos que el que poseía el camino más largo
                self.game_manager.board.build_road(1, 32, 33)
                self.game_manager.board.build_road(1, 33, 34)
                self.game_manager.board.build_road(1, 34, 35)

            for node in self.game_manager.board.nodes:
                longest_road_obj = self.game_manager.longest_road_calculator(node, 1, longest_road, -1, [node['id']])

                if longest_road_obj['longest_road'] >= longest_road['longest_road']:
                    longest_road = longest_road_obj

            if case == 0:  # Caso 1: Aún no hay nadie con 5 o más caminos
                assert longest_road == {'longest_road': 4, 'player': -1}

            if case == 1:  # Caso 2: Hay un jugador con 5 o más caminos
                assert longest_road == {'longest_road': 5, 'player': 0}

            if case == 2:  # Caso 3: Otro jugador alcanza la misma cantidad de caminos que el que tiene la carretera
                assert longest_road == {'longest_road': 5, 'player': 0}

            if case == 3:  # Caso 4: Otro jugador tiene más caminos que el que poseía el camino más largo
                assert longest_road == {'longest_road': 8, 'player': 1}
        return

    def test_play_development_card(self):
        done_0 = True
        done_1 = True
        done_1_1 = True
        done_2 = True
        done_2_2 = False
        done_2_2_1 = True
        done_2_3 = False
        done_2_4 = False
        winner = False

        while done_0 or done_1 or done_2:
            self.game_manager.reset_game_values()

            self.game_manager.board.nodes[24]['player'] = 0
            self.game_manager.board.nodes[19]['player'] = 1
            self.game_manager.board.nodes[42]['player'] = 2
            self.game_manager.board.nodes[0]['player'] = 3
            for player in range(3):
                self.game_manager.agent_manager.players[player]['resources'].add_material([MaterialConstants.CEREAL,
                                                                                           MaterialConstants.MINERAL,
                                                                                           MaterialConstants.CLAY,
                                                                                           MaterialConstants.WOOL,
                                                                                           MaterialConstants.WOOD
                                                                                           ], 1)

            self.game_manager.agent_manager.players[3]['resources'].add_material([MaterialConstants.CEREAL,
                                                                                  MaterialConstants.MINERAL,
                                                                                  MaterialConstants.WOOL,
                                                                                  ], 1)
            self.game_manager.build_development_card(3)
            card = self.game_manager.agent_manager.players[3]['development_cards'].hand[
                len(self.game_manager.agent_manager.players[3]['development_cards'].hand) - 1]

            if card.type == DevelopmentCardConstants.KNIGHT and done_0:
                card, winner = self.game_manager.play_development_card(3, card, winner)

                assert winner is False
                assert self.game_manager.agent_manager.players[3]['knights'] == 1
                done_0 = False

            elif card.type == DevelopmentCardConstants.VICTORY_POINT and done_1:
                if done_1_1:
                    self.game_manager.agent_manager.players[3]['victory_points'] = 9
                    card, winner = self.game_manager.play_development_card(3, card, winner)

                    assert winner is True
                    assert card['played_card'] == 'victory_point'

                    winner = False
                    done_1_1 = False

                else:
                    card, winner = self.game_manager.play_development_card(3, card, winner)

                    assert winner is False
                    assert card['played_card'] == 'failed_victory_point'
                    done_1 = False

            elif card.type == DevelopmentCardConstants.PROGRESS_CARD and done_2:

                if card.effect == DevelopmentCardConstants.MONOPOLY_EFFECT and not done_2_4:
                    card, winner = self.game_manager.play_development_card(3, card, winner)

                    assert winner is False
                    assert card['played_card'] == 'monopoly'
                    assert self.game_manager.agent_manager.players[3]['resources'].get_total() == 3
                    assert self.game_manager.agent_manager.players[1]['resources'].get_from_id(
                        card['material_chosen']) == 0
                    done_2_4 = True

                elif card.effect == DevelopmentCardConstants.ROAD_BUILDING_EFFECT and not done_2_2:
                    if done_2_2_1:
                        card_bad, winner = self.game_manager.play_development_card(3, card, winner)

                        assert winner is False
                        assert card_bad['roads'] is None
                        done_2_2_1 = False
                    else:
                        self.game_manager.on_game_start_build_towns_and_roads(3)
                        card, winner = self.game_manager.play_development_card(3, card, winner)

                        assert winner is False
                        assert card['played_card'] == 'road_building'

                        done_2_2 = True

                elif card.effect == DevelopmentCardConstants.YEAR_OF_PLENTY_EFFECT and not done_2_3:
                    card, winner = self.game_manager.play_development_card(3, card, winner)

                    assert winner is False
                    assert card['played_card'] == 'year_of_plenty'
                    assert self.game_manager.agent_manager.players[3]['resources'].get_total() == 2
                    done_2_3 = True

                elif done_2_4 and done_2_3 and done_2_2:
                    done_2 = False

    def test_check_if_thief_is_called(self):
        self.game_manager.reset_game_values()

        self.game_manager.last_dice_roll = 7
        self.game_manager.agent_manager.actual_player = 2
        for player in range(4):
            self.game_manager.on_game_start_build_towns_and_roads(player)

            self.game_manager.agent_manager.players[player]['resources'] = Hand()
            self.game_manager.agent_manager.players[player]['player'].hand = (
                self.game_manager.agent_manager.players)[player]['resources']

        for player in range(4):
            self.game_manager.agent_manager.players[player]['resources'].add_material([MaterialConstants.CEREAL,
                                                                                       MaterialConstants.MINERAL,
                                                                                       MaterialConstants.CLAY,
                                                                                       MaterialConstants.WOOL,
                                                                                       MaterialConstants.WOOD
                                                                                       ], player)
            self.game_manager.agent_manager.players[0]['resources'].add_material(MaterialConstants.CEREAL, 1)

            self.game_manager.agent_manager.players[player]['player'].hand = (
                self.game_manager.agent_manager.players)[player]['resources']

        start_turn_object = {}
        start_turn_object = self.game_manager.check_if_thief_is_called(start_turn_object, 2)

        assert start_turn_object['past_thief_terrain'] != start_turn_object['thief_terrain']

        if start_turn_object['robbed_player'] == 0:  # Si le ha robado al J0
            assert self.game_manager.agent_manager.players[0]['resources'].get_total() == (4 - 1)
            assert self.game_manager.agent_manager.players[1]['resources'].get_total() == 5
            assert self.game_manager.agent_manager.players[3]['resources'].get_total() == 7
        elif start_turn_object['robbed_player'] == 1:  # Si le ha robado al J1
            assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 4
            assert self.game_manager.agent_manager.players[1]['resources'].get_total() == (5 - 1)
            assert self.game_manager.agent_manager.players[3]['resources'].get_total() == 7
        elif start_turn_object['robbed_player'] == 3:  # Si le ha robado al J3
            assert self.game_manager.agent_manager.players[0]['resources'].get_total() == 4
            assert self.game_manager.agent_manager.players[1]['resources'].get_total() == 5
            assert self.game_manager.agent_manager.players[3]['resources'].get_total() == (7 - 1)

        assert self.game_manager.agent_manager.players[2]['resources'].get_total() == (5 + 1)

    def test_on_commerce_response(self):
        self.game_manager.reset_game_values()
        # No hay respuesta del comerciante
        commerce_phase_object = {}
        commerce_response = None
        depth = 1
        player = 0
        winner = False

        commerce_phase_object, winner = self.game_manager.on_commerce_response(commerce_phase_object, commerce_response,
                                                                               depth, player, winner)

        assert winner is False
        assert commerce_phase_object['trade_offer'] == 'None'

        self.game_manager.reset_game_values()
        # Nadie tiene materiales para intercambiar, haciendo el intercambio inviable
        commerce_phase_object = {}
        commerce_response = TradeOffer(Materials(1, 0, 0, 0, 0), Materials(0, 0, 1, 0, 1))
        depth = 1
        player = 0
        winner = False

        commerce_phase_object, winner = self.game_manager.on_commerce_response(commerce_phase_object, commerce_response,
                                                                               depth, player, winner)

        assert winner is False
        assert commerce_phase_object['harbor_trade'] is False
        assert commerce_phase_object['inviable'] is True

        self.game_manager.reset_game_values()
        # Todos tienen materiales para intercambiar completando el intercambio
        commerce_phase_object = {}
        commerce_response = TradeOffer(Materials(1, 0, 0, 0, 0), Materials(0, 0, 1, 0, 1))
        depth = 1
        player = 0
        winner = False
        self.game_manager._give_all_resources()

        commerce_phase_object, winner = self.game_manager.on_commerce_response(commerce_phase_object, commerce_response,
                                                                               depth, player, winner)

        assert winner is False
        assert commerce_phase_object['harbor_trade'] is False
        assert commerce_phase_object['answers'][0][0]['completed'] is True

        self.game_manager.reset_game_values()
        # Si la profundidad de los intercambios es mucha se cancelan todos los intercambios
        commerce_phase_object = {}
        commerce_response = TradeOffer(Materials(1, 0, 0, 0, 0), Materials(0, 0, 1, 0, 1))
        depth = 3
        player = 0
        winner = False

        commerce_phase_object, winner = self.game_manager.on_commerce_response(commerce_phase_object, commerce_response,
                                                                               depth, player, winner)

        assert winner is False
        assert commerce_phase_object['trade_offer'] == 'None'

        self.game_manager.reset_game_values()
        # Intercambio con un puerto
        commerce_phase_object = {}
        commerce_response = {'gives': MaterialConstants.CEREAL, 'receives': MaterialConstants.MINERAL}
        depth = 1
        player = 0
        winner = False
        self.game_manager._give_all_resources()

        commerce_phase_object, winner = self.game_manager.on_commerce_response(commerce_phase_object, commerce_response,
                                                                               depth, player, winner)

        assert winner is False
        assert commerce_phase_object['harbor_trade'] is True
        assert commerce_phase_object['answer']['cereal'] == '1'
        assert commerce_phase_object['answer']['mineral'] == '6'

        self.game_manager.reset_game_values()
        # Uso de una carta de desarrollo
        commerce_phase_object = {}
        commerce_response = DevelopmentCard(2, DevelopmentCardConstants.KNIGHT, DevelopmentCardConstants.KNIGHT_EFFECT)
        self.game_manager.agent_manager.players[0]['development_cards'].add_card(commerce_response)
        self.game_manager.agent_manager.players[0]['player'].development_cards_hand.hand = \
            self.game_manager.agent_manager.players[0]['development_cards'].hand
        depth = 1
        player = 0
        winner = False

        commerce_phase_object, winner = self.game_manager.on_commerce_response(commerce_phase_object, commerce_response,
                                                                               depth, player, winner)

        assert winner is False
        assert commerce_phase_object['harbor_trade'] is False
        assert commerce_phase_object['trade_offer'] == 'played_card'

        self.game_manager.reset_game_values()
        # Uso de una carta de desarrollo para ganar la partida
        commerce_phase_object = {}
        self.game_manager.agent_manager.players[0]['victory_points'] = 9
        self.game_manager.agent_manager.players[0]['hidden_victory_points'] = 1
        commerce_response = DevelopmentCard(17, DevelopmentCardConstants.VICTORY_POINT,
                                            DevelopmentCardConstants.VICTORY_POINT_EFFECT)
        self.game_manager.agent_manager.players[0]['development_cards'].add_card(commerce_response)
        self.game_manager.agent_manager.players[0]['player'].development_cards_hand.hand = \
            self.game_manager.agent_manager.players[0]['development_cards'].hand
        depth = 1
        player = 0
        winner = False

        commerce_phase_object, winner = self.game_manager.on_commerce_response(commerce_phase_object, commerce_response,
                                                                               depth, player, winner)

        assert winner is True
        assert commerce_phase_object['harbor_trade'] is False
        assert commerce_phase_object['trade_offer'] == 'played_card'

    def test_build_phase_object(self):
        self.game_manager.reset_game_values()
        # No hay respuesta del constructor
        build_phase_object = {}
        build_response = None
        player = 0
        winner = False

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is False
        assert build_phase_object['building'] == 'None'

        self.game_manager.reset_game_values()
        # Intento de construir sin materiales
        build_phase_object = {}
        build_response = {'building': BuildConstants.TOWN, 'node_id': 5}
        player = 0
        winner = False

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is False
        assert build_phase_object['finished'] is False

        self.game_manager.reset_game_values()
        # Intento de construir un pueblo con materiales y carretera
        build_phase_object = {}
        build_response = {'building': BuildConstants.TOWN, 'node_id': 0}
        player = 0
        winner = False
        self.game_manager._give_all_resources()
        self.game_manager.board.nodes[0]['roads'].append({'player_id': 0, 'node_id': 1})

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is False
        assert self.game_manager.agent_manager.players[0]['victory_points'] == 1
        assert build_phase_object['building'] == 'town'
        assert build_phase_object['finished'] is True

        # Intento de construir una ciudad sobre el pueblo de antes con materiales
        build_phase_object = {}
        build_response = {'building': BuildConstants.CITY, 'node_id': 0}

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is False
        assert self.game_manager.agent_manager.players[0]['victory_points'] == 2
        assert build_phase_object['building'] == 'city'
        assert build_phase_object['finished'] is True

        # Intento de construir una carretera en la situación de antes con materiales
        build_phase_object = {}
        build_response = {'building': BuildConstants.ROAD, 'node_id': 0, 'road_to': 8}

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is False
        assert self.game_manager.agent_manager.players[0]['victory_points'] == 2
        assert build_phase_object['building'] == 'road'
        assert build_phase_object['finished'] is True

        self.game_manager.reset_game_values()
        # Intento de construir una carta de desarrollo
        build_phase_object = {}
        build_response = {'building': BuildConstants.CARD}
        player = 0
        winner = False
        self.game_manager._give_all_resources()

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is False
        assert build_phase_object['building'] == 'card'
        assert build_phase_object['finished'] is True

        self.game_manager.reset_game_values()
        # Uso de una carta de desarrollo
        build_phase_object = {}
        build_response = DevelopmentCard(2, DevelopmentCardConstants.KNIGHT, DevelopmentCardConstants.KNIGHT_EFFECT)
        self.game_manager.agent_manager.players[0]['development_cards'].add_card(build_response)
        self.game_manager.agent_manager.players[0]['player'].development_cards_hand.hand = \
            self.game_manager.agent_manager.players[0]['development_cards'].hand
        player = 0
        winner = False

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is False
        assert build_phase_object['building'] == 'played_card'

        self.game_manager.reset_game_values()
        # Uso de una carta de desarrollo para ganar la partida
        build_phase_object = {}
        self.game_manager.agent_manager.players[0]['victory_points'] = 9
        self.game_manager.agent_manager.players[0]['hidden_victory_points'] = 1
        build_response = DevelopmentCard(17, DevelopmentCardConstants.VICTORY_POINT,
                                         DevelopmentCardConstants.VICTORY_POINT_EFFECT)
        self.game_manager.agent_manager.players[0]['development_cards'].add_card(build_response)
        self.game_manager.agent_manager.players[0]['player'].development_cards_hand.hand = \
            self.game_manager.agent_manager.players[0]['development_cards'].hand
        player = 0
        winner = False

        build_phase_object, winner = self.game_manager.build_phase_object(build_phase_object, build_response, player,
                                                                          winner)

        assert winner is True
        assert build_phase_object['building'] == 'played_card'


if __name__ == '__main__':
    test = TestGameManager()
    test.test_reset_values()
    test.test_give_resources()
    test.test_send_trade_to_everyone()
    test.test__on_tradeoffer_response()
    test.test__trade_with_player()
    test.test_build_town()
    test.test_build_city()
    test.test_build_road()
    test.test_build_development_card()
    test.test_move_thief()
    test.test__steal_from_player()
    test.test_on_game_start_build_towns_and_roads()
    test.test_longest_road()
    test.test_play_development_card()
    test.test_check_if_thief_is_called()
    test.test_on_commerce_response()
    test.test_build_phase_object()
