from .serializers import (
    send_email,
    UserSerializer,
    LogoutSerializer,
    UserUpdateSerializer,
    UserLoginSerializer,
    UserCreationSerializer,

    UserChangePasswordSerializer, #change Password
    SendPasswordResetEmailSerializer, #send password reset email
    UserPasswordResetSerializer, #reset password

    UserProfileResponseSerializer,
)
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.filters import SearchFilter
from .renderers import UserRenderer, JsonRenderer
from rest_framework.views import APIView, exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema


def get_auth_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserProfileView(APIView):
    permission_classes  = [permissions.IsAuthenticated]
    serializer_class    = UserProfileResponseSerializer
    renderer_classes    = [UserRenderer]
    filter_backends     = (SearchFilter,)
    search_fields       = ('email',)

    @extend_schema(
            responses={
                200: UserProfileResponseSerializer
                (many=False),
            }
    )
    def get(self, request, format=None):
        """
        Return the current user's profile information.

        **GET** `/api/auth/me/`

        Returns a JSON response with the current user's profile information.

        **Response Values**

        * `user`: The user's profile information, including their: \n
            * user ID, \n
            * first name, 
            * last name, 
            * date of birth, 
            * email address, 
            * location,
            * is_active : whether they are active.
        * `message`: A message indicating that the user is authenticated.

        **Status Codes**

        * `200 OK`: The user is authenticated and the profile information was returned successfully.
        """
        serializer = self.serializer_class(request.user)        
        return Response({
            'user': serializer.data,
            'message':'Retrieved Successfully'
        }, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        """
        Update the current user's profile information.

        **PUT** `/api/auth/me/`

        Returns a JSON response with the updated user's profile information.

        **Request Body Values**

        * `first_name`: First name of the user\n
        * `last_name`: Last name of the user
        * `dob`: The user's date of birth (YYYY-MM-DD)
        * `email`: The user's email address
        * `location`: The user's location

        **Response Values**

        * `user`: The updated user's profile information, including their: \n
            * user ID, \n
            * first name, 
            * last name, 
            * date of birth, 
            * email address, 
            * location,
            * is_active : whether they are active.

        **Status Codes**

        * `200 OK`: The user's profile information was updated successfully.\n
        * `400 Bad Request`: The request was invalid, or the user's profile information could not be updated.
        """
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'user': serializer.data,
            'message':'Updated Successfully',
        }, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes  = [permissions.AllowAny]
    serializer_class    = UserLoginSerializer
    renderer_classes    = [UserRenderer]

    @extend_schema(
        description="User login endpoint",
        request=UserLoginSerializer,
        responses={
            200: UserProfileResponseSerializer(many=False),
        }
    )
    def post(self, request, format=None):
        """
            Handles user login request.
        
            **POST** `/api/auth/login/`
        
            Authenticates the user with the provided email and password, 
            returns a JSON response with the login message, user email, and authentication tokens.
        
            **Request Body Values**
        
            * `email`: The user's email address.\n
            * `password`: The user's password.
        
            **Response Values**
        
            * `message`: A message indicating the successful login.\n
            * `user`: The user's email address.
            * `tokens`: Authentication tokens for the user.
        
            **Status Codes**
        
            * `200 OK`: The user is authenticated successfully.
        """
        serializer  = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.authenticate_user(
                    email=serializer.validated_data.get('email'),
                    password=serializer.validated_data.get('password'))

        return Response(
            {
                "message"   : "Login successfully",
                "user"      : UserProfileResponseSerializer(user).data,
                "tokens"    : get_auth_tokens(user),
            },
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    permission_classes  = [permissions.AllowAny]
    serializer_class    = UserCreationSerializer
    renderer_classes    = [JsonRenderer]

    def post(self, request, format=None):
        """
        Handles user registration and returns a JSON response with the newly
        created user's information and authentication tokens.

        **POST** `/api/auth/register/`

        Returns a JSON response with the newly created user's information and
        authentication tokens.

        **Request Body Values**

        * `email`: The user's email address\n
        * `first_name`: First name of the user
        * `last_name`: Last name of the user
        * `dob`: The user's date of birth (YYYY-MM-DD)
        * `location`: The user's location
        * `password`: The user's password.
        * `password2`: The user's password confirmation.

        **Response Values**

        * `message`: A message indicating that the user was created successfully.\n
        * `user`: The newly created user's email address.
        * `tokens`: A dictionary containing the user's authentication tokens,
            including the access token and refresh token.

        **Status Codes**

        * `201 Created`: The user was created successfully and the authentication\n
            tokens were returned.
        * `400 Bad Request`: The request was invalid, or the user could not be
            created.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'message': 'User created successfully',
            'user'   : serializer.data['email'],
            'tokens' : get_auth_tokens(serializer.instance)
        }, 
        status=status.HTTP_201_CREATED)


class SendPasswordResetEmailView(APIView):
    permission_classes   = [permissions.AllowAny]
    serializer_class     = SendPasswordResetEmailSerializer
    renderer_classes     = [UserRenderer]

    
    def post(self, request, format=None):
        """
        Handles password reset email request.

        **POST** `/api/auth/send-reset-password-email/`

        Returns a JSON response with a success message.

        **Request Body Values**

        * `email`: The user's email address.

        **Response Values**

        * `message`: A message indicating that the password reset email was sent successfully.

        **Status Codes**

        * `200 OK`: The password reset email was sent successfully.\n
        * `400 Bad Request`: The request was invalid, or the password reset email could not be sent.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            'message':'Password Reset link send. Please check your Email',
        }, status=status.HTTP_200_OK)


from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
class UserPasswordResetView(APIView):
    permission_classes  = [permissions.AllowAny]
    serializer_class    = UserPasswordResetSerializer
    renderer_classes    = [UserRenderer]
    
    @extend_schema(
            description="User password reset endpoint",
            request=UserPasswordResetSerializer,
            responses={
                200: UserProfileResponseSerializer(many=False),
            }
    )
    def post(self, request, uid, token, format=None):
        """
        Handles password reset request.

        **POST** `/api/auth/reset-password/:uid/:token/`

        Returns a JSON response with a success message.

        **Request Body Values**

        * `password`: The new password for the user.\n
        * `password2`: Confirmation of the new password.

        **Response Values**

        * `message`: A message indicating that the password was reset successfully.

        **Status Codes**

        * `200 OK`: The password was reset successfully.\n
        * `400 Bad Request`: The request was invalid, or the password could not be reset.
        """
        serializer = self.serializer_class(data=request.data, context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        
        return Response({'message':'Password Reset Successfully'}, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = UserChangePasswordSerializer
    renderer_classes   = [UserRenderer]

    def post(self, request, format=None):
        """
        Handle user password change request.

        **POST** `/api/auth/change-password/`

        Validates the provided current password and the new passwords, updates the user's password, and returns a success message.

        **Request Body Values**

        * `current_password`: The user's current password.\n
        * `new_password`: The new password for the user.
        * `re_new_password`: Confirmation of the new password.

        **Response Values**

        * `message`: A message indicating that the password was changed successfully.

        **Status Codes**

        * `200 OK`: The user's password was changed successfully.\n
        * `400 Bad Request`: The request was invalid, or the password could not be changed.
        """
        serializer = self.serializer_class(data=request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'Password Changed Successfully'}, status=status.HTTP_200_OK)
    

class UserLogoutView(APIView):
    permission_classes      = [permissions.IsAuthenticated]
    renderer_classes        = [UserRenderer]
    serializer_class        = LogoutSerializer

    def post(self, request, format=None):
        """
        Handles user logout and returns a JSON response with a success message.

        **POST** `/api/auth/logout/`

        Returns a JSON response with a success message.

        **Request Body Values**

        * `refresh_token`: The user's refresh token obtained from the Login API.

        **Response Values**

        * `message`: A message indicating that the user is logged out successfully.

        **Status Codes**

        * `200 OK`: The user is logged out successfully.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message':'Logged Out Successfully'}, status=status.HTTP_200_OK)