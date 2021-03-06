from django.db import models
from django.db.models import Q
from django.utils import timezone
from user.models import UserProfile
import simplejson as json

GAME_END_STATUS = (
    ('n', 'normal'),
    ('s', 'surrendered'),
    ('d', 'draw')
)


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    players_count = models.IntegerField()
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    board = models.CharField(max_length=5000)
    game_end_status = models.CharField(choices=GAME_END_STATUS, max_length=1)

    # get board as list of lists
    def get_board(self):
        return json.loads(self.board)

    # save board (list of lists) as json string
    def set_board(self, board):
        self.board = json.dumps(board)

    # create board with null elements
    @classmethod
    def create_new_board(cls):
        new_board = []
        for i in range(15):
            new_board.append([None] * 15)
        return new_board

    # get all games awaiting start
    @classmethod
    def get_awaiting_games(cls):
        return Game.objects.filter(players_count=1).all()

    # get all games of the user
    @classmethod
    def get_user_games(cls, user):
        user_players = Player.objects.filter(user=user).all()
        return Game.objects.filter(
            id__in=[player.game.id for player in user_players]
        ).all()

    # get all finished games of the user
    @classmethod
    def get_user_finished_games(cls, user):
        return cls.get_user_games(user).filter(
            end_time__lt=timezone.now()
        ).all()

    # get all awaiting games
    @classmethod
    def get_user_awaiting_games(cls, user):
        user_players = Player.objects.filter(user=user).all()
        return [
            player.game
            for player in user_players
            if player.game.players_counter == 1
        ]

    # get user's statistics (number of wins, draws and losses)
    @classmethod
    def get_user_stats(cls, user):
        user_games = cls.get_user_finished_games(user)
        normal_finished_games = user_games.filter(game_end_status='n')
        draw_finished_games = user_games.filter(game_end_status='d')
        # surrendered_games = user_games.filter(game_end_status='s')
        user_players = Player.objects.filter(
            game__in=user_games,
            user=user
        ).all()

        won_players = user_players.filter(won=True).all()
        normal_won_players = won_players.filter(game__in=normal_finished_games)

        all_won_number = won_players.count()
        surrender_won_number = all_won_number - normal_won_players.count()

        lost_players = user_players\
            .filter(won=False)\
            .exclude(game__in=draw_finished_games).all()
        normal_lost_players = lost_players.filter(
            game__in=normal_finished_games
        )
        all_lost_number = lost_players.count()
        surrender_lost_number = all_lost_number - normal_lost_players.count()
        draw_number = draw_finished_games.count()

        player_stats = dict(
            username=user.username,
            won=all_won_number,
            lost=all_lost_number,
            won_by_surrender=surrender_won_number,
            draws=draw_number,
            surrendered=surrender_lost_number
        )
        return player_stats

    # check if one of the players won or board is full
    def check_game_end(self):
        winner = self.check_horizontal_win()
        if winner is False:
            winner = self.check_vertical_win()
            if winner is False:
                winner = self.check_l_diagonal_win()
                if winner is False:
                    winner = self.check_r_diagonal_win()
        if winner is not False:
            self.game_end_status = 'n'
            self.end()
            if winner == 'o':
                winner_player = Player.objects.filter(
                    game=self,
                    owner=True
                ).first()
            else:
                winner_player = Player.objects.filter(
                    game=self,
                    owner=False
                ).first()
            winner_player.won = True
            winner_player.save()

        if self.check_full_board():
            self.game_end_status = 'd'
            self.end()

    # check if board does not contain empty fields
    # (if there is no winner and board is full = draw)
    def check_full_board(self):
        board = self.get_board()
        for i in range(15):
            for j in range(15):
                if board[i][j] is None:
                    return False
        return True

    # find and return horizontal winner (False if there is no winner)
    def check_horizontal_win(self):
        end_line = 5
        board = self.get_board()
        for i in range(15):
            field_owner = board[i][0]
            counter = 0
            for j in range(15):
                if board[i][j] == field_owner:
                    counter += 1
                    if counter == end_line and field_owner is not None:
                        return field_owner
                else:
                    counter = 1
                    field_owner = board[i][j]
        return False

    # find and return vertical winner (False if there is no winner)
    def check_vertical_win(self):
        end_line = 5
        board = self.get_board()
        for i in range(15):
            field_owner = board[i][0]
            counter = 0
            for j in range(15):
                if board[j][i] == field_owner:
                    counter += 1
                    if counter == end_line and field_owner is not None:
                        return field_owner
                else:
                    counter = 1
                    field_owner = board[j][i]
        return False

    # find and return right-diagonal winner (False if there is no winner)
    def check_r_diagonal_win(self):
        end_line = 5
        board = self.get_board()
        for i in range(15):
            field_owner = board[i][0]
            counter = 0
            for j in range(15):
                if ((i + j) % 15 == 0):
                    counter = 0
                if board[(i + j) % 15][j] == field_owner:
                    counter += 1
                    if counter == end_line and field_owner is not None:
                        return field_owner
                else:
                    counter = 1
                    field_owner = board[(i + j) % 15][j]
        return False

    # find and return left-diagonal winner (False if there is no winner)
    def check_l_diagonal_win(self):
        end_line = 5
        board = self.get_board()
        for i in range(15):
            field_owner = board[i][0]
            counter = 0
            for j in range(15):
                if ((i - j) % 15 == 0):
                    counter = 0
                if board[(i - j) % 15][j] == field_owner:
                    counter += 1
                    if counter == end_line and field_owner is not None:
                        return field_owner
                else:
                    counter = 1
                    field_owner = board[(i - j) % 15][j]
        return False

    # start game
    def start(self):
        self.start_time = timezone.now()
        self.save()

    # end game
    def end(self):
        self.end_time = timezone.now()
        self.save()

    # check if game is running or finished
    def is_started(self):
        if self.start_time is not None:
            return self.start_time < timezone.now()
        else:
            return False

    # check if game is finished
    def is_finished(self):
        if self.end_time is not None:
            return self.end_time < timezone.now()
        else:
            return False

    # get number of players in the game
    def get_number_of_players(self):
        return self.players_count

    # make player's move
    def make_move(self, move):
        board = self.get_board()
        if not self.is_started():
            return dict(
                message="This game didn't started yet.",
                status=400
            )
        elif self.is_finished():
            return dict(
                message='This game is already finished.',
                status=400
            )
        elif board[move.x][move.y] is not None:
            # spot is taken
            return dict(
                message='This spot is already taken.',
                status=400
            )
        else:
            # check if it's turn of move's player
            last_move = Move.get_game_moves(self).first()
            # check if it's first move
            if last_move is None:
                if move.player.owner is False:
                    return dict(
                        message="It's not your turn to move",
                        status=400
                    )
            # double move of the same player
            elif last_move.player == move.player:
                return dict(
                    message="It's not your turn to move",
                    status=400
                )
            # correct move of game's owner
            if move.player.owner is True:
                board[move.x][move.y] = 'o'
                self.set_board(board)
                self.save()
                move.save()
                return dict(
                    message='ok',
                    status=200
                )
            # correct move of game's guest
            else:
                board[move.x][move.y] = 'g'
                self.set_board(board)
                self.save()
                move.save()
                return dict(
                    message='ok',
                    status=200
                )

    # return game (without the board) in json format
    def as_json_without_board(self):
        return dict(
            id=self.id,
            players_count=self.get_number_of_players(),
            started=self.is_started(),
            finished=self.is_finished(),
            surrendered=(self.game_end_status == 's'),
            draw=(self.game_end_status == 'd')
        )

    # return game in json format
    def as_json(self):
        json_dict = self.as_json_without_board()
        json_dict['board'] = self.get_board()
        return json_dict


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, related_name='players')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    won = models.BooleanField(default=False)
    owner = models.BooleanField()
    first = models.BooleanField()

    # return player's info as dictionary
    def as_json(self):
        return dict(
            name=self.user.username,
            won=self.won,
            owner=self.owner,
            first=self.first,
            user=self.user.id,
            game=Game.get_player_game(self).id
        )


class Move(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    timestamp = models.DateTimeField(default=timezone.now)
    x = models.IntegerField()
    y = models.IntegerField()

    @classmethod
    def get_game_moves(cls, game):
        return Move.objects.filter(game=game).order_by('-timestamp').all()

    # return move in json format
    def as_json(self):
        return dict(
            id=self.id,
            player=self.player.id,
            timestamp=self.timestamp,
            x=self.x,
            y=self.y,
        )
