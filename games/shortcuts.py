from itertools import zip_longest

from games.example_data import *


class TestHelpers:
    def _create_game(self, player_client):
        """Shortcut to create game using given APIClient"""
        return player_client.post(
            '/api/games/', {},
        ).json()['id']

    def _game_ops(self, game_id, player_client, game_ops='join'):
        """
        Performs easy game operation with empty POST
        :param game_id: id of the game
        :param player_client: user's APIClient to perform the operation
        :param game_ops: str - name of the operation
        :return: Response from the APIClient
        """
        return player_client.post(
            '/api/games/{}/{}/'.format(game_id, game_ops), {}
        )

    def _create_working_game(self, owner_client=None, guest_client=None):
        """
        Creates working game using the API - create, join and start
        :param owner_client: APIClient for owner of the game - defaults to
                             player_1
        :param guest_client: APIClient for owner of the game - defaults to
                             player_2
        :return: created game id
        """
        game_id = self._create_game(owner_client or self.player_1_client)
        self._game_ops(game_id, guest_client or self.player_2_client)
        self._game_ops(game_id, owner_client or self.player_1_client, 'start')

        return game_id

    def _first_player(self, response_dict, owner_id=None):
        """
        Returns flag / token of player who should make the move first
        :param response_dict: dict - parsed json from the response
        :param owner_id: id of the owner of the game (defaults to player_1 id)
        :return: OWNER or GUEST
        """
        return OWNER if next(
            filter(lambda x: x['first'], response_dict['players'])
        )['user'] == (owner_id or self.player_1.id) else GUEST

    def _make_moves(self, game_id, order, moves, mapping=None):
        """
        Proceeds with all given moves for players.
        :param game_id: id of the game
        :param order: order of moves - tuple with OWNER and GUEST
        :param moves: tuple of lists of moves, in same order as in the `order`
                      tuple
        :param mapping: mapping of OWNER and GUEST to proper APIClients -
                        defaults to OWNER for player_1 and GUEST for player_2
        :return: last received response from APIClient
        """
        for this_turn_moves in zip_longest(*moves):
            for player, move in zip(order, this_turn_moves):
                if move is None:  # second player makes one move less
                    break

                x, y = move
                response = (mapping or self.default_game_mapping)[player].post(
                    '/api/games/{}/moves/'.format(game_id),
                    {'x': x, 'y': y},
                )
                self.assertEqual(response.status_code, 200)
        return response

    def _players_order(self, response_dict, owner_id=None):
        """
        Returns tuple for moves order in game
        :param response_dict: dict - parsed json from API response
        :param owner_id: id of the game owner - defaults to player_1
        :return: tuple with players' order
        """
        if self._first_player(response_dict, owner_id) == OWNER:
            return OWNER, GUEST
        else:
            return GUEST, OWNER

    def _validate_me(self, player_client, won=0, draws=0, won_by_surrender=0,
                     lost=0, surrendered=0):
        """
        Validates if endpoint `api/user/me/` returns proper data
        :param player_client: APIClient of given player
        :param won: expected number of games won
        :param draws: expected number of draws
        :param won_by_surrender: expected number of games won by opponent's
                                 surrender
        :param lost: expected number of games lost
        :param surrendered: expected number of games surrendered
        """
        response = player_client.get(
            '/api/user/me/'
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.json()
        self.assertEqual(response_json['won'], won)
        self.assertEqual(response_json['draws'], draws)
        self.assertEqual(response_json['won_by_surrender'], won_by_surrender)
        self.assertEqual(response_json['lost'], lost)
        self.assertEqual(response_json['surrendered'], surrendered)
