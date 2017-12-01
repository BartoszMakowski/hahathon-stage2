from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

from games.example_data import *
from games.shortcuts import TestHelpers

User = get_user_model()


class GamesAPITestCase(APITestCase, TestHelpers):
    PLAYER_1 = dict(username='player_1', password='1234')
    PLAYER_2 = dict(username='player_2', password='2345')
    PLAYER_3 = dict(username='player_3', password='3456')

    def setUp(self):
        """
        setUp - create 3 users, APIClients for them, one APIClient for
        unauthenticated user; prepare default mapping from OWNER/GUEST to
        user APIClient
        """
        self.maxDiff = None
        self.player_1 = User.objects.create_user(**self.PLAYER_1)
        self.player_2 = User.objects.create_user(**self.PLAYER_2)
        self.player_3 = User.objects.create_user(**self.PLAYER_3)

        self.no_player_client = APIClient()

        self.player_1_client = APIClient()
        self.player_1_client.force_login(self.player_1)

        self.player_2_client = APIClient()
        self.player_2_client.force_login(self.player_2)

        self.player_3_client = APIClient()
        self.player_3_client.force_login(self.player_3)

        self.default_game_mapping = {
            OWNER: self.player_1_client,
            GUEST: self.player_2_client,
        }

    def test_no_games(self):
        """
         - rejects unauthenticated user
         - authenticated user receives empty list of games
        """
        response = self.no_player_client.get(
            '/api/games/'
        )
        self.assertEqual(response.status_code, 403)
        self.assertDictEqual(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'},
        )

        response = self.player_1_client.get(
            '/api/games/'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_game(self):
        """
         - user creates game with empty board
         - game without board is visible to other users
        """
        response = self.player_1_client.post(
            '/api/games/', {},
        )
        response_json = response.json()

        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response_json)

        created_game_id = response_json['id']
        expected_dict = base_game_dict(created_game_id, self.player_1)

        self.assertDictEqual(
            response.json(),
            expected_dict,
        )
        expected_dict.pop('board')

        response = self.player_2_client.get(
            '/api/games/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            [expected_dict],
        )

    def test_join_game(self):
        """
         - user successfully joins game
         - API returns proper data with 2 players in game
        """
        game_id = self._create_game(self.player_1_client)

        response = self.player_2_client.post(
            '/api/games/{}/join/'.format(game_id), {},
        )

        expected_dict = base_game_dict(game_id, self.player_1)
        expected_dict['players_count'] = 2
        expected_dict['players'].append(base_player_dict(game_id,
                                                         self.player_2, False))

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(),
                             {'success': True, 'game': expected_dict})

    def test_cannot_join_game(self):
        """
         - user who is already in game cannot join it again
         - only 2 players are accepted in game
        """
        game_id = self._create_game(self.player_1_client)

        # Try join own game
        response = self.player_1_client.post(
            '/api/games/{}/join/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), ERROR_ALREADY_JOINED)

        # Proper game join
        self.player_2_client.post(
            '/api/games/{}/join/'.format(game_id), {},
        )

        # Attempt to join a full game
        response = self.player_3_client.post(
            '/api/games/{}/join/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), ERROR_GAME_FULL)

    def test_leave_game(self):
        """
         - user cannot leave game he did not join
         - user can leave game before it starts
        """
        game_id = self._create_game(self.player_1_client)

        response = self.player_2_client.post(
            '/api/games/{}/leave/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), ERROR_NOT_IN_GAME)

        self.player_2_client.post(
            '/api/games/{}/join/'.format(game_id), {},
        )

        response = self.player_2_client.post(
            '/api/games/{}/leave/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'success': True})

    def test_rejoin_game(self):
        """
         - user can rejoin game he once left, if it is still available
        """
        game_id = self._create_game(self.player_1_client)
        self._game_ops(game_id, self.player_2_client, 'join')
        self._game_ops(game_id, self.player_2_client, 'leave')

        response = self.player_2_client.post(
            '/api/games/{}/join/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 200)

    def test_start_game_owner(self):
        """
         - game can be started by game owner
        """
        game_id = self._create_game(self.player_1_client)
        self._game_ops(game_id, self.player_2_client, 'join')

        response = self.player_1_client.post(
            '/api/games/{}/start/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 200)

        response = self.player_2_client.get(
            '/api/games/{}'.format(game_id),
        )

        self.assertEqual(response.status_code, 200)

        response_json = response.json()
        # Game has started
        self.assertTrue(response_json['started'])
        # One of the players is designated to make the first move
        self.assertTrue(
            any(filter(lambda p: p['first'], response_json['players']))
        )

    def test_start_game_guest(self):
        """
         - game can be started by guest
        """
        game_id = self._create_game(self.player_1_client)
        self._game_ops(game_id, self.player_2_client, 'join')

        response = self.player_2_client.post(
            '/api/games/{}/start/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 200)

        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.json()
        # Game has started
        self.assertTrue(response_json['started'])
        # One of the players is designated to make the first move
        self.assertTrue(
            any(filter(lambda p: p['first'], response_json['players']))
        )

    def test_cannot_leave_game(self):
        """
         - user cannot leave game once it is started
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        response = self.player_2_client.post(
            '/api/games/{}/leave/'.format(game_id), {},
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), ERROR_GAME_ACTIVE)

    def test_make_move(self):
        """
         - user can post move to game
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        should_be_first = self._first_player(response.json())

        response = (self.player_1_client if should_be_first == OWNER else
                    self.player_2_client).post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 0}
        )

        expected_dict = base_game_dict(game_id, self.player_1)
        expected_dict['players_count'] = 2
        expected_dict['players'].append(base_player_dict(game_id,
                                                         self.player_2, False))
        expected_dict['board'][0][0] = should_be_first
        expected_dict['started'] = True

        for player in expected_dict['players']:
            player['first'] = (player['owner'] and should_be_first == OWNER) or \
                              (not player['owner'] and should_be_first == GUEST)

        response_json = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['game'], expected_dict)

        self.assertEqual(
            response_json['move']['player'],
            (self.player_1 if should_be_first == OWNER else self.player_2).id,
        )
        self.assertEqual(response_json['move']['x'], 0)
        self.assertEqual(response_json['move']['y'], 0)

    def test_wrong_turn(self):
        """
         - user cannot make move if it is not his turn
         - user cannot make two moves in a row
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        order = self._players_order(response.json())

        response = self.default_game_mapping[order[1]].post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 0}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), ERROR_NOT_TURN)

        response = self.default_game_mapping[order[0]].post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 0}
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.json()
        self.assertEqual(
            response_json['move']['player'],
            (self.player_1 if order[0] == OWNER else self.player_2).id,
        )
        self.assertEqual(response_json['move']['x'], 0)
        self.assertEqual(response_json['move']['y'], 0)

        response = self.default_game_mapping[order[0]].post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 1}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), ERROR_NOT_TURN)

    def test_spot_taken(self):
        """
         - user cannot make move to the spot that is already taken
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        order = self._players_order(response.json())

        response = self.default_game_mapping[order[0]].post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 0}
        )
        self.assertEqual(response.status_code, 200)

        response = self.default_game_mapping[order[1]].post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 0}
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), ERROR_SPOT_TAKEN)

    def test_not_a_player(self):
        """
         - user who is not a member of the game cannot make move in a game
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        order = self._players_order(response.json())

        response = self.default_game_mapping[order[0]].post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 0}
        )
        self.assertEqual(response.status_code, 200)

        response = self.player_3_client.post(
            '/api/games/{}/moves/'.format(game_id),
            {'x': 0, 'y': 1}
        )
        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(response.json(), ERROR_NOT_IN_GAME)

    def test_surrender_game(self):
        """
         - user can surrender a game which he participate
         - surrendered game counts toward users' statistics
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        response = self.player_1_client.post(
            '/api/games/{}/surrender/'.format(game_id), {}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        response_json = response.json()
        self.assertTrue(response_json['finished'])
        self.assertTrue(response_json['surrendered'])

        for player in response_json['players']:
            if player['won']:
                self.assertEqual(player['user'], self.player_2.id)
            else:
                self.assertEqual(player['user'], self.player_1.id)

        self._validate_me(self.player_1_client, surrendered=1, lost=1)
        self._validate_me(self.player_2_client, won=1, won_by_surrender=1)

    def _test_win_game(self, variant):
        """
         - users can post moves to game
         - one of the users wins the game
         - state of the game is properly recognized
         - finised game counts toward users' statistics
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        # Check order of moves
        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        if self._first_player(response.json()) == OWNER:
            order = (OWNER, GUEST)
            winner, loser = self.player_1, self.player_2
        else:
            order = (GUEST, OWNER)
            winner, loser = self.player_2, self.player_1
        expected_board, moves = win_board(order[0], variant)

        # Fill board
        response = self._make_moves(game_id, order, moves)

        last_response_json = response.json()
        self.assertTrue(last_response_json['game']['finished'])
        self.assertFalse(last_response_json['game']['draw'])
        self.assertListEqual(last_response_json['game']['board'],
                             expected_board)
        for player in last_response_json['game']['players']:
            if player['won']:
                self.assertEqual(player['user'], winner.id)
            else:
                self.assertEqual(player['user'], loser.id)

        self._validate_me(self.default_game_mapping[order[0]], won=1)
        self._validate_me(self.default_game_mapping[order[1]], lost=1)

    def test_win_game_horizontal(self):
        self._test_win_game('horizontal')

    def test_win_game_vertical(self):
        self._test_win_game('vertical')

    def test_win_game_diagonal_1(self):
        self._test_win_game('diagonal_1')

    def test_win_game_diagonal_2(self):
        self._test_win_game('diagonal_2')

    def test_game_draw(self):
        """
        Assumption - we do not recognize state "no one can win" - draw is
        declared when we run out of space on the board
         - user can post moves to game
         - none of the users wins the game
         - state of the game is properly recognized
         - finised game counts toward users' statistics
        """
        game_id = self._create_working_game(self.player_1_client,
                                            self.player_2_client)

        # Check order of moves
        response = self.player_1_client.get(
            '/api/games/{}'.format(game_id),
        )
        self.assertEqual(response.status_code, 200)

        if self._first_player(response.json()) == OWNER:
            order = (OWNER, GUEST)
        else:
            order = (GUEST, OWNER)
        expected_board, moves = draw_board(order[0])

        # Fill board
        response = self._make_moves(game_id, order, moves)

        last_response_json = response.json()
        self.assertTrue(last_response_json['game']['finished'])
        self.assertTrue(last_response_json['game']['draw'])
        self.assertListEqual(last_response_json['game']['board'],
                             expected_board)
        self.assertTrue(
            all(map(lambda p: not p['won'],
                    last_response_json['game']['players']))
        )

        self._validate_me(self.default_game_mapping[order[0]], draws=1)
        self._validate_me(self.default_game_mapping[order[1]], draws=1)
