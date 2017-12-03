from django.db import models
from django.db.models import Q
from django.utils import timezone
from user.models import Player
import simplejson as json

GAME_END_STATUS = (
    ('n', 'normal'),
    ('s', 'surrendered'),
    ('d', 'draw')
)

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    player_p1 = models.ForeignKey(Player, related_name='owner_player')
    player_p2 = models.ForeignKey(Player, related_name='guest_player', null=True, blank=True)
    players_counter = models.IntegerField()
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    board = models.CharField(max_length=5000)
    game_end_status = models.CharField(choices=GAME_END_STATUS, max_length=1)

    def get_board(self):
        return json.loads(self.board)

    def set_board(self, board):
        self.board = json.dumps(board)

    # create board with null elements
    @classmethod
    def create_new_board(cls):
        new_board = []
        for i in range(15):
            new_board.append([None] * 15)
        return new_board

    # get all games awaiting for start
    @classmethod
    def get_awaiting_games(cls):
        return Game.objects.filter(players_counter=1).all()

    # get all games of the user
    @classmethod
    def get_user_games(cls, user):
        return Game.objects.filter(Q(player_p1__user=user) | Q(player_p2__user=user)).all()

    # get all finished games of the user
    @classmethod
    def get_user_finished_games(cls, user):
        return cls.get_user_games(user).filter(end_time__lt=timezone.now()).all()

    # get all awaiting games
    @classmethod
    def get_user_awaiting_games(cls, user):
        return cls.get_awaiting_games().filter(Q(player_p1__user=user) | Q(player_p2__user=user)).all()

    # get user's statistics (number of wins, draws and losses)
    @classmethod
    def get_user_stats(cls, user):
        user_games = cls.get_user_finished_games(user)
        normal_finished_games = user_games.filter(game_end_status='n')
        draw_finished_games = user_games.filter(game_end_status='d')
        surrendered_games = user_games.filter(game_end_status='s')

        draw_number = draw_finished_games.count()
        normal_number = normal_finished_games.count()
        surrendered_number = surrendered_games.count()
        won_number = normal_finished_games.filter(
            (Q(player_p1__user=user) & Q(player_p1__won=True))
            | (Q(player_p2__user=user) & Q(player_p2__won=True))
        ).count()

        won_by_surrender_number = surrendered_games.filter(
            (Q(player_p1__user=user) & Q(player_p1__won=True))
            | (Q(player_p2__user=user) & Q(player_p2__won=True))
        ).count()

        lost_by_surrender_number = surrendered_number - won_by_surrender_number
        lost_number = normal_number - won_number

        player_stats = dict(
            username=user.username,
            won=(won_number + won_by_surrender_number),
            lost=(lost_number + lost_by_surrender_number),
            won_by_surrender=won_by_surrender_number,
            draws=draw_number,
            surrendered=lost_by_surrender_number,
        )
        return player_stats


    def check_game_end(self):
        winner = self.check_horizontal_win()
        if winner is False:
            winner = self.check_vertical_win()
        if winner is not False:
            self.game_end_status = 'n'
            self.end()
            if winner == 'o':
                self.player_p1.won = True
                self.player_p1.save()
            else:
                self.player_p2.won = True
                self.player_p2.save()

        if self.check_full_board():
            self.end()
            self.game_end_status = 'd'


    def check_full_board(self):
        board = self.get_board()
        for i in range(15):
            for j in range(15):
                if board[i][j] is not None:
                    return False
        return True


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
        try:
            return self.start_time < timezone.now()
        except:
            return False

    # check if game is finished
    def is_finished(self):
        try:
            return self.end_time < timezone.now()
        except:
            return False

    # get number of players in the game
    def get_number_of_players(self):
        return self.players_counter

    # get players' info in json format
    def get_players_jsons(self):
        players_jsons = [self.player_p1.as_json(), ]
        if self.player_p2 is not None:
            players_jsons.append(self.player_p2.as_json())
        return players_jsons

    # return user's player in the game
    def get_my_player(self, user):
        if self.player_p1.user == user:
            return self.player_p1
        elif self.player_p2 is not None \
                and self.player_p2.user == user:
            return self.player_p2
        else:
            return None

    # make player's move
    def make_move(self, move):
        board = self.get_board()
        if not self.is_started():
            return dict(
                message='This game is not started yet.',
                status=400
            )
        elif self.is_finished():
            return dict(
                message='This game is finished already.',
                status=400
            )
        elif board[move.x_coordinate][move.y_coordinate] is not None:  # field is taken
            return dict(
                message='This field is already taken',
                status=400
            )
        else:
            if move.player == self.player_p1:
                board[move.x_coordinate][move.y_coordinate] = 'o'
                self.set_board(board)
                self.save()
                return dict(
                    message='ok',
                    status=200
                )

            elif move.player == self.player_p2:
                board[move.x_coordinate][move.y_coordinate] = 'g'
                self.set_board(board)
                self.save()
                return dict(
                    message='ok',
                    status=200
                )


    # return game (without the board) in json format
    def as_json_without_board(self):
        return dict(
            id=self.id,
            players_count=self.get_number_of_players(),
            players=self.get_players_jsons(),
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


class Move(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game)
    player = models.ForeignKey(Player)
    timestamp = models.DateTimeField(default=timezone.now)
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()

    def as_json(self):
        return dict(
            id=self.id,
            player=self.player.id,
            timestamp=self.timestamp,
            x=self.x_coordinate,
            y=self.y_coordinate,
        )

    # class BoardField(models.Model):
    #          x = models.IntegerField(validators=[MinValueValidator()]),
    #          y = models.IntegerField)(),
    #          status = models.CharField(choices=FIELD_STATUS)
