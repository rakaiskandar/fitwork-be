from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_candidate=True
        ) 
        return user

class CustomEmailTokenSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # login via email

    def validate(self, attrs):
        # Ensure compatibility with AbstractUser which uses `username`
        attrs['username'] = attrs.get('email')
        data = super().validate(attrs)

        self.user = self.user  # ✅ Ensure user is accessible later

        # Include custom claims
        data.update({
            "email": self.user.email,
            "is_candidate": self.user.is_candidate,
            "is_company_admin": self.user.is_company_admin,
            "is_fitwork_admin": self.user.is_fitwork_admin,
        })

        return data

    def create_token_response(self, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_candidate'] = user.is_candidate
        token['is_company_admin'] = user.is_company_admin
        token['is_fitwork_admin'] = user.is_fitwork_admin
        return token

    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.user  # user is set during validation
        data.update({
            "email": user.email,
            "is_candidate": user.is_candidate,
            "is_company_admin": user.is_company_admin,
            "is_fitwork_admin": user.is_fitwork_admin
        })
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Custom JWT claims
        token['email'] = user.email
        token['is_candidate'] = user.is_candidate
        token['is_company_admin'] = user.is_company_admin
        token['is_fitwork_admin'] = user.is_fitwork_admin

        return token
    
class RegisterCompanyAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'company_id']

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            company_id=validated_data['company_id'],
            is_candidate=False,
            is_company_admin=True
        )

