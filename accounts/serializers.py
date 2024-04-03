from dj_rest_auth.serializers import UserDetailsSerializer


class CustomUserSerializer(UserDetailsSerializer):

    class Meta(UserDetailsSerializer.Meta):
        fields = ("pk", "email", "username", "nickname", "user_type", "is_staff")