from rest_framework import serializers, exceptions
from django.contrib.auth import get_user_model, authenticate
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from rest_framework_simplejwt.serializers import RefreshToken
from .utils import Util


User = get_user_model()

def send_email(subject, message, email):
    data = {
        'subject': subject,
        'body': message,
        'to_email': email
        }
    Util.send_email(data)
    return True

class UserCreationSerializer(serializers.ModelSerializer):
    email       = serializers.EmailField()
    first_name  = serializers.CharField()
    last_name   = serializers.CharField()
    location    = serializers.CharField()
    dob         = serializers.DateField()
    password2   = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'dob', 'location', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }
        read_only_fields = ['email']
    
    def validate_data(self, data):
        password1 = data.get('password')
        password2 = data.get('password2')
        if password1!= password2:
            raise serializers.ValidationError('Passwords must match.')
        return data
        
    
    def create(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('Email already exists.')

        user = User.objects.create_user(
            email = data['email'],
            first_name = data['first_name'],
            last_name = data['last_name'],
            password = data['password']
        )
        user.dob = data['dob'] if 'dob' in data else None
        user.location = data['location'] if 'location' in data else None
        user.save()
        
        send_email (
            'Welcome to My Account',
            'Hello {0},\nThank you for registering with us.\nWe are happy to have you on board.\n\nRegards,\nMy Account Team'.format(user.first_name),
            user.email
        )

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    class Meta:
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'write_only': True},
        }
        validation_messages = {
            'email': {'required': 'You must provide an email address.'},
            'password': {'required': 'You must provide a password.'},
        }

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user with this email address exists.')
        return value
    
    def authenticate_user(self, email, password):
        user        = authenticate(email=email, password=password)
        if not user:
            raise exceptions.AuthenticationFailed("Invalid credentials")

        # Email Notification
        send_email(
            "Login Notification",
            "You're account has been login successfully",
            user.email
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    location    = serializers.CharField()
    dob         = serializers.DateField()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'dob', 'email', 'location', 'is_active']
        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'read_only': True},
        }
        read_only_fields = ['id','is_active']

class UserProfileResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'dob', 'email', 'location']


class UserUpdateSerializer(serializers.ModelSerializer):
    location    = serializers.CharField()
    dob         = serializers.DateField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'dob', 'email', 'location']
        extra_kwargs = {
            'id': {'read_only': True},
            'email': {'read_only': True},
            'is_active': {'read_only': True},
        }
        read_only_fields = ['id','is_active', 'email']


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    token_class = RefreshToken

    class Meta:
        fields = ['refresh_token']

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh_token"])
        try:
            refresh.blacklist()
        except AttributeError:
            raise serializers.ValidationError('Invalid token.')
        return True

class UserChangePasswordSerializer(serializers.Serializer):
    new_password        = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    re_new_password     = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    current_password    = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)

    class Meta:
        fields = ['new_password', 're_new_password', 'current_password']

    def validate(self, attrs):        
        new_password = attrs.get('new_password')
        re_new_password = attrs.get('re_new_password')
        current_password = attrs.get('current_password')

        user    = self.context.get('user')
        user    = User.objects.get(email=user.email)
        
        if not user.check_password(current_password):
            raise serializers.ValidationError("Your current password is wrong")
        
        if new_password != re_new_password:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")

        user.set_password(new_password)
        user.save()

        send_email(
            'Change Password',
            'Your password has been successfully changed.',
            user.email
        )
        return attrs    


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']
        
    def validate(self, attrs):
        email = attrs.get('email')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email = email)

            # uid = urlsafe_base64_encode(force_bytes(user.id))
            # print('Encoded UID', uid)
            # token = PasswordResetTokenGenerator().make_token(user)
            # print('Password Reset Token', token)
            # link = 'http://localhost:8000/api/auth/password/reset/'+uid+'/'+token+'/'
            # print('Password Reset Link', link)
            
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:8000/api/auth/reset-password/'+uid+'/'+token+'/'

            # Send EMail
            body = 'Click Following Link to Reset Your Password '+link
            
            send_email(
                'Reset Your Password',
                body,
                user.email
            )
            response = {
                "user"  : attrs,
                "uid"   : uid,
                "token" : token
            }
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')
        

class UserPasswordResetSerializer(serializers.Serializer):
    password    = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2   = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)

    class Meta:
        fields = ["uid", "token", 'password', 'password2']
        
    def validate(self, instance):
        try:
            uid         = self.context.get('uid')
            token       = self.context.get('token')
            password    = instance.get('password')
            password2   = instance.get('password2')

            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")

            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')

            user.set_password(password)
            user.save()

            send_email(
                'Password Reset Successful',
                'You have successfully reset you password.\nNow you can login with your new password',
                user.email
            )
            return instance
        
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
        raise serializers.ValidationError('Token is not Valid or Expired')