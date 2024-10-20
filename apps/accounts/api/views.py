from rest_framework.response import Response
from rest_framework.views import APIView, exceptions
from rest_framework import status, permissions, generics
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserLoginSerializer,
    UserCreationSerializer,

    UserChangePasswordSerializer, #change Password
    SendPasswordResetEmailSerializer, #send password reset email
    UserPasswordResetSerializer, #reset password
)


from .renderers import UserRenderer, JsonRenderer
from django.contrib.auth import authenticate

def get_auth_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserProfileView(APIView):
    serializer_class = UserSerializer
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

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
    serializer_class = UserLoginSerializer
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        """
        Handles user login and returns authentication tokens.

        **POST** `/api/auth/login/`

        Returns a JSON response with the authentication tokens and a success message.

        **Request Body Values**

        * `email`: The user's email address.\n
        * `password`: The user's password.

        **Response Values**

        * `message`: A message indicating that the user is authenticated.\n
        * `tokens`: A dictionary containing the user's authentication tokens, including the access token and refresh token.

        **Status Codes**

        * `200 OK`: The user is authenticated and the authentication tokens were returned successfully.\n
        * `400 Bad Request`: The request was invalid, or the user is not authenticated.
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.validated_data)

        if not user:
            raise exceptions.AuthenticationFailed("Invalid credentials")

        return Response(
            {
                "message": "Login successfully",
                "tokens": get_auth_tokens(user),
            },
            status=status.HTTP_200_OK,
        )


class RegisterView(APIView):
    serializer_class = UserCreationSerializer
    renderer_classes = [JsonRenderer]
    permission_classes = [permissions.AllowAny]

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
        # send email with verification link or token
        return Response({
            'message': 'User created successfully',
            'tokens': get_auth_tokens(serializer.instance)
        }, 
        status=status.HTTP_201_CREATED)
    


class SendPasswordResetEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SendPasswordResetEmailSerializer
    renderer_classes = [UserRenderer]

    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
    permission_classes  = [permissions.AllowAny]
    serializer_class    = UserPasswordResetSerializer
    renderer_classes    = [UserRenderer]
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)
    

class UserChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = UserChangePasswordSerializer
    renderer_classes   = [UserRenderer]

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)