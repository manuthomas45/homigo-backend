from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from cloudinary.models import CloudinaryField

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('isVerified', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('status', 'active')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=15)
    profilePicture = CloudinaryField('image', blank=True, null=True)  
    role = models.CharField(max_length=50, default='user')
    isVerified = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='pending')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName', 'phoneNumber']

    def __str__(self):
        return self.email

class OTP(models.Model):
    email = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.email}"