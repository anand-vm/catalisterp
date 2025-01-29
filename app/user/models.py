# catalisterp/app/user/models.py
import uuid
import time
import logging
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.db import models
from utils.models import CommonFields

# Create your models here.
User = get_user_model()
logger = logging.getLogger("django")

class CustomUserManager(BaseUserManager):
    def create_user(self, email, mobile_number, password=None, **extra_fields):
        if not email and not mobile_number:
            raise ValueError("Either Email or Mobile Number must be set")
        
        email = self.normalize_email(email) if email else None
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, mobile_number=mobile_number, **extra_fields)
        user.username = f"user_{uuid.uuid4().hex[:8]}"  # Generate random username
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email=email, mobile_number=mobile_number, password=password, **extra_fields)


class UserScope(CommonFields):
    name = models.CharField(max_length=50, unique=True)
    allowed_groups = models.ManyToManyField(Group, blank=True, related_name="user_scopes_groups")
    allowed_permissions = models.ManyToManyField(Permission, blank=True, related_name="user_scopes_permissions")
    custom_permissions = models.JSONField(default=dict)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True, help_text='Enter a valid email address.')
    #mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="Mobile number")
    mobile_number = PhoneNumberField(unique=True, null=True, blank=True, region="IN")
    username = models.CharField(max_length=30, unique=True, verbose_name="Username", help_text="Auto-generated username")

    # Authentication Fields
    email_verified = models.BooleanField(default=False)
    mobile_verified = models.BooleanField(default=False)
    user_scope = models.ForeignKey(UserScope, on_delete=models.SET_NULL, null=True, blank=True)

    # Django Permissions & Groups
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, blank=True, related_name="custom_users_groups")
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="custom_users_permissions")
    
    # Logging
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)  # Common UUID field for all models with autogenerate
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="created_users")
    updated_by = models.ForeignKey("auth.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="updated_users")


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  # Login with email instead of username
    REQUIRED_FIELDS = ['mobile_number']

    def __str__(self):
        return self.email or self.mobile_number

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class UserDetails(CommonFields):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='user_details')
    last_login_time = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    # Company & Multi-Tenancy Support
    company_id = models.ForeignKey("company.Company", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    employee_id = models.ForeignKey("hr.Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    # Preferences
    language = models.CharField(max_length=10, default="en", choices=[("en", "English"), ("fr", "French"), ("es", "Spanish")])
    timezone = models.CharField(max_length=50, default="UTC")
    notification_type = models.CharField(max_length=20, choices=[("email", "Email"), ("sms", "SMS"), ("none", "None")], default="email")
    referred_by = models.CharField(max_length=50, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='user_profile_pictures/', null=True, blank=True)
    jdoc = models.JSONField(default=dict)
