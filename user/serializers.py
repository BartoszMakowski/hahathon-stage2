from rest_framework import serializers

from user.models import UserProfile


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         # exclude = ('id', )
#         fields = ('username',)
#

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.RelatedField(source='user.username', read_only=True)
    username = username['useraname']

    class Meta:
        model = UserProfile
        # exclude = ('id', )
        fields = ('username',)

    def create(self, validated_data):
        print(validated_data)
        return UserProfile.objects.create(**validated_data)