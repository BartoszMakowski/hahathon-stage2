from django.db import models
from django.contrib.auth.models import User


# proxy for User class
class UserProfile(User):
    class Meta:
        proxy = True

    @classmethod
    def is_username_taken(cls, username):
        existing_user = User.objects.filter(username=username)
        if existing_user.exists():
            return True
        else:
            return False


class Player(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    game_id = models.IntegerField(null=True)
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
            game=self.game_id,
        )
