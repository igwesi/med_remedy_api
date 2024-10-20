from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, GroupManager
from django.contrib.auth.models import update_last_login


class AccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email = self.normalize_email(email),
            first_name = first_name,
            last_name = last_name,
            password = password
        )
        user.is_admin     = True
        user.is_staff     = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(unique=True, validators=[EmailValidator])
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    location    = models.CharField(max_length=100, null=True, blank=True)
    dob         = models.DateField(null=True, blank=True, verbose_name="Date of Birth")

    is_patient  = models.BooleanField(default=False)
    is_doctor   = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    is_admin    = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login  = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects  = AccountManager()

    # @property
    # def token(self):
    #     """
    #     Allows us to get a user's token by calling `user.token` instead of
    #     `user.generate_jwt_token().

    #     The `@property` decorator above makes this possible. `token` is called
    #     a "dynamic property".
    #     """
    #     try:
    #         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    #         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    #         token = jwt_encode_handler(jwt_payload_handler(self))
    #     except Exception as ex:
    #         raise Exception(f"Token Generation Failed {ex}")
    #     # Update last login time after successful login
    #     update_last_login(None, self)
    #     return token
    

    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):        
        return True
    
class Group(Group):

    objects = GroupManager()

    def __str__(self):
        return self.name
