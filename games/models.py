from django.db import models
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
    owner = models.ForeignKey(Player, related_name='owner')
    guest = models.ForeignKey(Player, related_name='guest')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    board = models.CharField(max_length=225)
    game_end_status = models.CharField(choices=GAME_END_STATUS, max_length=1)

    def set_gamefield(self, x):
        self.board = json.dumps(x)

    def get_gamefield(self):
        return json.loads(self.board)


class Move(models.Model):
    player = models.ForeignKey(Player)
    timestamp = models.DateTimeField(default=timezone.now)
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()

# class BoardField(models.Model):
#          x = models.IntegerField(validators=[MinValueValidator()]),
#          y = models.IntegerField)(),
#          status = models.CharField(choices=FIELD_STATUS)