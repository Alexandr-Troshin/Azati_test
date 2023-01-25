from django.contrib.auth import get_user_model
from rest_framework import serializers
import json


User = get_user_model()

class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True, label='Confirm password'
    )
    balance_of_funds = serializers.JSONField(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'balance_of_funds']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        password2 = validated_data['password2']
        balance_of_funds = {'money': 0} # json.dumps({'money': 0})
        if (username and User.objects.filter(username=username).exclude(email=email).exists()):
            raise serializers.ValidationError(
                {'username': 'This Username already in use.'}
            )
        if password != password2:
            raise serializers.ValidationError({'password': 'The two passwords are differ.'})

        user = User(username=username, email=email, balance_of_funds = balance_of_funds)
        user.set_password(password)
        user.save()
        return user


class CustomUserRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'email', 'balance_of_funds']


class CustomUserUpdateFundsSerializer(serializers.ModelSerializer):

    income_stock = serializers.CharField()
    income_qty = serializers.IntegerField()
    class Meta:
        model = User
        fields = ['username', 'email', 'balance_of_funds', 'income_stock', 'income_qty']


