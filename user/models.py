from django.db import models
from django.contrib.auth.models import User

# Create your models here.

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

    def as_json(self):
        return dict(
            username=self.username,
            draws=0,
            lost=0,
            surrendered=0,
            won=0,
            won_by_surrender=0
        )

class Player(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    game_id = models.CharField(max_length=100, null=True)
    won = models.BooleanField(default=False)
    first = models.BooleanField()

    def as_json(self):
        return dict(
            # id=1,
            name=self.user.username,
            won=False,
            owner=True,
            first=False,
            user=self.user.id,
            game=self.game_id
        )