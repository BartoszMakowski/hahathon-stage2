from django.db import models
from django.db.models import Q
from django.utils import timezone
from user.models import Player
# from django.core.validators import MinValueValidator, MaxValueValidator

import json

# FIELD_STATUS = (
#     ('o', 'owner'),
#     ('g', 'guest')
# )

# PLAYER_STATUS = (
#     ('w', 'winner'),
#     ('l', 'looser'),
#     ('d', 'draw')
# )

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
    board = models.CharField(max_length=225)
    game_end_status = models.CharField(choices=GAME_END_STATUS, max_length=1)

    @classmethod
    def create_new_board(cls):
        new_board = []
        for i in range(15):
            new_board.append([None] * 15)
        return new_board

    @classmethod
    def get_awaiting_games(cls):
        return Game.objects.all().exclude(start_time__gt=timezone.now())

    @classmethod
    def get_user_games(cls, user):
        return Game.objects.filter(Q(player_p1__user=user) | Q(player_p2__user=user)).all()

    @classmethod
    def get_user_finished_games(cls, user):
        return Game.objects.filter(Q(player_p1__user=user) | Q(player_p2__user=user)).filter(end_time < timezone.now()).all()

    def check_end(self):
        end_line = 5

        # horizontal - TODO: new function
        for i in range(15):
            field_owner = self.board[i][0]
            counter = 0
            for j in range(15):
                if self.board[i][j] == field_owner:
                    counter += 1
                    if counter == end_line and field_owner is not None:
                        return field_owner
                else:
                    counter = 1
                    field_owner = self.board[i][j]

        # vertical - TODO: new function
        for i in range(15):
            field_owner = self.board[0][i]
            counter = 0
            for j in range(15):
                if self.board[j][i] == field_owner:
                    counter += 1
                    if counter == end_line and field_owner is not None:
                        return field_owner
                else:
                    counter = 1
                    field_owner = self.board[j][i]
        return False

    def start(self):
        self.start_time = timezone.now()
        self.save()

    def end(self):
        self.end_time = timezone.now()
        self.save()

    def is_started(self):
        try:
            return self.start_time < timezone.now()
        except:
            return False

    def is_finished(self):
        try:
            return self.end_time < timezone.now()
        except:
            return False

    def get_number_of_players(self):
        return self.players_counter

    def get_players_jsons(self):
        players_jsons = [self.player_p1.as_json(), ]
        if self.player_p2 is not None:
            players_jsons.append(self.player_p2.as_json())
        return players_jsons

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

    def as_json(self):
        json_dict = self.as_json_without_board()
        json_dict['board'] = self.board
        return json_dict


class Move(models.Model):
    player = models.ForeignKey(Player)
    timestamp = models.DateTimeField(default=timezone.now)
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()

    # class BoardField(models.Model):
    #          x = models.IntegerField(validators=[MinValueValidator()]),
    #          y = models.IntegerField)(),
    #          status = models.CharField(choices=FIELD_STATUS)
