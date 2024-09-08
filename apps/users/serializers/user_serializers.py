from rest_framework import serializers
from apps.users.models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'position',
            'email',
            'phone',
            'last_login',
        )
