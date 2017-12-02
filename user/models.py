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

    def stats_as_json(self, stats):
        return dict(
            username=self.username,
            draws=0,
            lost=0,
            surrendered=0,
            won=0,
            won_by_surrender=0
        )

class Player(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    game_id = models.CharField(max_length=100, null=True)
    won = models.BooleanField(default=False)
    owner = models.BooleanField()
    first = models.BooleanField()

    def as_json(self):
        return dict(
            # id=self.id,
            name=self.user.username,
            won=self.won,
            owner=self.owner,
            first=self.first,
            user=self.user.id,
            game=int(self.game_id),
        )