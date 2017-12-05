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
