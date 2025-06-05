from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

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
    
class AdminUserListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_candidate', 'is_company_admin', 'is_fitwork_admin',
            'company', 'company_name',
            'is_active', 'date_joined'
        ]
        
class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    company = serializers.UUIDField(source='company_id', allow_null=True, required=False) 

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name',
                  'is_candidate', 'is_company_admin', 'is_fitwork_admin', 'company']

    def validate_is_fitwork_admin(self, value):
        if value: # If attempting to set is_fitwork_admin to True
            raise serializers.ValidationError("Creating other Fitwork admin users is not permitted through this interface.")
        return value # Should always be False or not present

    def validate(self, data):
        if data.get('is_fitwork_admin'):
             raise serializers.ValidationError({"is_fitwork_admin": "Cannot create Fitwork admins here."})
         
        return data

    def create(self, validated_data):
        company_id_val = validated_data.pop('company_id', None)
        
        validated_data['is_fitwork_admin'] = False 

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_candidate=validated_data.get('is_candidate', False),
            is_company_admin=validated_data.get('is_company_admin', False),
            is_fitwork_admin=False, # Overriding any input, ensuring it's false
            company_id=company_id_val if validated_data.get('is_company_admin') else None
        )
        return user

class AdminUserUpdateSerializer(serializers.ModelSerializer):
    company = serializers.UUIDField(source='company_id', allow_null=True, required=False)
    password = serializers.CharField(write_only=True, required=False, allow_blank=False, min_length=8)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'is_candidate', 'is_company_admin', 'is_fitwork_admin',
            'company', 'is_active', 'password'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'username': {'required': False},
            'is_fitwork_admin': {'read_only': True},
            'password': {'write_only': True},
        }

    def validate(self, data):
        instance = self.instance  # The user being updated

        if instance and instance.is_fitwork_admin:
            raise serializers.ValidationError("Fitwork admin profiles cannot be modified via this interface.")

        if data.get('is_fitwork_admin'):
            raise serializers.ValidationError(
                {"is_fitwork_admin": "Cannot change 'is_fitwork_admin' status via this interface."}
            )

        is_company_admin_target_state = data.get('is_company_admin', instance.is_company_admin if instance else False)
        company_id_target = data.get('company_id', instance.company_id if instance else None)

        if is_company_admin_target_state and not company_id_target:
            raise serializers.ValidationError({"company": "Company is required if user is set as a company admin."})

        if not is_company_admin_target_state:
            data['company_id'] = None

        return data

    def update(self, instance, validated_data):
        if 'company_id' in validated_data:
            instance.company_id = validated_data.pop('company_id')

        if 'is_company_admin' in validated_data and not validated_data['is_company_admin']:
            instance.company = None

        # Handle password update
        if 'password' in validated_data:
            instance.password = make_password(validated_data.pop('password'))

        return super().update(instance, validated_data)

