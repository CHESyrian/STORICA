from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """User role choices"""
    ADMIN = 'admin', 'Administrator'
    MANAGER = 'manager', 'Manager'
    USER = 'user', 'User'
    VIEWER = 'viewer', 'Viewer'
    GUEST = 'guest', 'Guest'


class UserManager(BaseUserManager):
    """Custom user manager for User model"""
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and save a regular user"""
        if not username:
            raise ValueError('The Username must be set')
        
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)
    
    def create_admin(self, username, email=None, password=None, **extra_fields):
        """Create an admin user (staff, not superuser)"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        return self.create_user(username, email, password, **extra_fields)
    
    def create_manager(self, username, email=None, password=None, **extra_fields):
        """Create a manager user"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.MANAGER)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with roles and permissions
    """
    # Basic fields
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        blank=True,
        null=True,
        unique=True
    )
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        blank=True,
        default=''
    )
    
    # Role and permissions
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.')
    )
    
    # User preferences
    theme = models.CharField(
        _('theme'),
        max_length=20,
        default='light',
        blank=True
    )
    language = models.CharField(
        _('language'),
        max_length=10,
        default='en',
        blank=True
    )
    
    # Tracking fields
    last_login_ip = models.GenericIPAddressField(
        _('last login IP'),
        blank=True,
        null=True
    )
    last_login_user_agent = models.TextField(
        _('last login user agent'),
        blank=True,
        default=''
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at  = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('updated at'), auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the full name of the user"""
        return self.full_name or self.username
    
    def get_short_name(self):
        """Return the short name of the user"""
        return self.username
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a permission (aligned with RolePermission ranks)."""
        from apps.users.services.user_service import UserService

        perms = UserService.permissions_for_user(self)
        return "*" in perms or permission in perms

    def get_permissions_list(self) -> list:
        """Permission strings for the UI — derived from role rank."""
        from apps.users.services.user_service import UserService

        return UserService.permissions_for_user(self)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for API response"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name or self.username,
            'role': self.role,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_superuser': self.is_superuser,
            'theme': self.theme,
            'language': self.language,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserSession(models.Model):
    """Track user sessions"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    token = models.CharField(max_length=500, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
    
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return timezone.now() >= self.expires_at


class UserLoginHistory(models.Model):
    """Track user login history for audit"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'user_login_history'
        ordering = ['-login_time']
        verbose_name_plural = 'user login histories'
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time} - {'Success' if self.success else 'Failed'}"