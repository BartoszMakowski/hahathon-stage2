from rest_framework import serializers
from games.models import Game, Move, Player
import simplejson as json


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = '__all__'
        ordering = ('-timestamp', )

    # save player as his id
    player = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        exclude = ('id', )

    name = serializers.CharField(source='user.username')
    # save game as its id
    game = serializers.SlugRelatedField(
        read_only=True,
        slug_field='id'
    )


# game serializer (without board)
class GameSerializer(serializers.ModelSerializer):

    class _UsernameField(serializers.CharField):
        # save user as his username
        def to_internal_value(self, data):
            return data['username']

    class _DrawBooleanField(serializers.BooleanField):
        # check if game was ended by draw
        def to_internal_value(self, data):
            return data == 'd'

    class _SurrenderedBooleanField(serializers.BooleanField):
        # check if game was ended by surrender
        def to_internal_value(self, data):
            return data == 's'

    players = PlayerSerializer(read_only=True, many=True)
    started = serializers.SerializerMethodField(method_name='is_started')
    finished = serializers.SerializerMethodField(method_name='is_finished')
    draw = _DrawBooleanField(source='game_end_status')
    surrendered = _SurrenderedBooleanField(source='game_end_status')

    def is_finished(self, obj):
        return obj.end_time is not None

    def is_started(self, obj):
        return obj.start_time is not None

    class Meta:
        model = Game
        exclude = (
            'start_time',
            'end_time',
            'game_end_status',
            'board',
        )


# game serializer containing board
class GameFullSerializer(GameSerializer):

    class _BoardField(serializers.CharField):
        def to_internal_value(self, data):
            return json.dumps(data)

        def to_representation(self, value):
            return json.loads(value)

    board = _BoardField()
