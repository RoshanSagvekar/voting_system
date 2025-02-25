from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers
from .models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "email", "password", "confirm_password",
            "date_of_birth", "phone_number", "aadhar_number", "profile_picture"
        ]
    def validate(self, data):
        """Custom validation logic"""
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        if not data.get("first_name"):
            raise serializers.ValidationError({"first_name": "First name is required."})

        if not data.get("last_name"):
            raise serializers.ValidationError({"last_name": "Last name is required."})

        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        # import pdb
        # pdb.set_trace()
        email = attrs.get("email")
        password = attrs.get("password")

        # Check if email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("No account found with this email.")

        # Check password
        if not check_password(password, user.password):
            raise AuthenticationFailed("Incorrect password.")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationFailed("Your account is disabled.")

        # Generate token
        tokens = super().validate({"email": user.email, "password": password})

        return {
            "access": tokens["access"],
            "refresh": tokens["refresh"]
        }


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'party', 'votes', 'profile_picture']

class ElectionSerializer(serializers.ModelSerializer):
    has_voted = serializers.SerializerMethodField()

    class Meta:
        model = Election
        fields = ['id', 'name', 'start_date', 'end_date','has_voted']

    def get_has_voted(self, obj):
        """Check if the logged-in user has voted in this election"""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Vote.objects.filter(voter=user, election=obj).exists()
        return False