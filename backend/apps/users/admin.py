from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import User, UserSession, UserLoginHistory


class UserChangeFormCustom(UserChangeForm):
    """Custom form for changing user in admin"""
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class UserCreationFormCustom(UserCreationForm):
    """Custom form for creating user in admin"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User Admin with enhanced features
    """
    form = UserChangeFormCustom
    add_form = UserCreationFormCustom
    
    # List display
    list_display = (
        'username',
        'full_name',
        'email',
        'role_badge',
        'is_active',
        'is_staff',
        'last_login',
        'login_count_display'
    )
    
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',  # Changed from 'date_joined'
    )
    
    search_fields = (
        'username',
        'email',
        'full_name',
    )
    
    readonly_fields = (
        'last_login',
        'created_at',  # Changed from 'date_joined'
        'updated_at',
        'last_login_ip',
        'last_login_user_agent',
        'login_count_display',
        'session_count_display',
        'user_permissions_display'
    )
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Information'), {
            'fields': ('email', 'full_name')
        }),
        (_('Role and Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('User Preferences'), {
            'fields': ('theme', 'language'),
            'classes': ('collapse',)
        }),
        (_('Login Information'), {
            'fields': ('last_login', 'last_login_ip', 'last_login_user_agent'),
            'classes': ('collapse',)
        }),
        (_('Important Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2', 'role'),
        }),
    )
    
    ordering = ('-created_at',)  # Changed from '-date_joined'
    list_per_page = 25
    list_select_related = True
    
    def get_queryset(self, request):
        """Annotate queryset with additional counts"""
        return super().get_queryset(request).annotate(
            login_count=Count('login_history', filter=Q(login_history__success=True)),
            session_count=Count('sessions', filter=Q(sessions__is_active=True))
        )
    
    def role_badge(self, obj):
        """Display role as colored badge"""
        colors = {
            'admin': '#dc3545',      # Red
            'manager': '#fd7e14',    # Orange
            'user': '#28a745',       # Green
            'viewer': '#17a2b8',     # Cyan
            'guest': '#6c757d',      # Gray
        }
        color = colors.get(obj.role, '#6c757d')
        role_display = obj.get_role_display()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, role_display
        )
    role_badge.short_description = 'Role'
    role_badge.admin_order_field = 'role'
    
    def login_count_display(self, obj):
        """Display login count with icon"""
        count = getattr(obj, 'login_count', 0)
        return format_html(
            '<span style="font-weight: bold;">🔐 {}</span>',
            count
        )
    login_count_display.short_description = 'Login Count'
    
    def session_count_display(self, obj):
        """Display active session count"""
        count = getattr(obj, 'session_count', 0)
        if count > 0:
            return format_html(
                '<span style="color: #28a745;">🟢 {}</span>',
                count
            )
        return format_html('<span style="color: #6c757d;">⚫ 0</span>')
    session_count_display.short_description = 'Active Sessions'
    
    def user_permissions_display(self, obj):
        """Display user permissions"""
        permissions = obj.get_permissions_list()
        if permissions == ['*']:
            return format_html('<span style="color: #dc3545;">🔓 Full Access (Admin)</span>')
        
        return format_html(
            '<details><summary style="cursor: pointer;">{} permissions</summary>'
            '<div style="margin-top: 5px; max-height: 150px; overflow-y: auto;">'
            '<ul style="margin: 0; padding-left: 20px;">{}</ul></div></details>',
            len(permissions),
            ''.join([f'<li>{p}</li>' for p in permissions])
        )
    user_permissions_display.short_description = 'Permissions'
    
    def get_readonly_fields(self, request, obj=None):
        """Set readonly fields based on user permissions"""
        readonly = list(self.readonly_fields)
        
        # Non-superusers can't change certain fields
        if not request.user.is_superuser:
            readonly.extend(['role', 'is_staff', 'is_superuser'])
        
        return readonly
    
    def save_model(self, request, obj, form, change):
        """Track who created/updated the user"""
        if not change:
            # User is being created
            pass
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting your own account"""
        if obj and obj == request.user:
            return False
        return super().has_delete_permission(request, obj)
    
    actions = ['activate_users', 'deactivate_users', 'set_role_admin', 
               'set_role_manager', 'set_role_user']
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        # Prevent deactivating yourself
        queryset = queryset.exclude(id=request.user.id)
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def set_role_admin(self, request, queryset):
        """Set role to Admin"""
        updated = queryset.update(role='admin')
        self.message_user(request, f'{updated} users were set to Admin role.')
    set_role_admin.short_description = 'Set role to Admin'
    
    def set_role_manager(self, request, queryset):
        """Set role to Manager"""
        updated = queryset.update(role='manager')
        self.message_user(request, f'{updated} users were set to Manager role.')
    set_role_manager.short_description = 'Set role to Manager'
    
    def set_role_user(self, request, queryset):
        """Set role to User"""
        updated = queryset.update(role='user')
        self.message_user(request, f'{updated} users were set to User role.')
    set_role_user.short_description = 'Set role to User'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin for User Session model"""
    list_display = (
        'user_link',
        'ip_address',
        'is_active',
        'created_at',
        'expires_at',
        'last_activity',
        'status_badge'
    )
    
    list_filter = (
        'is_active',
        'created_at',
        'expires_at',
    )
    
    search_fields = (
        'user__username',
        'user__email',
        'ip_address',
        'token',
    )
    
    readonly_fields = (
        'token',
        'user',
        'ip_address',
        'user_agent',
        'created_at',
        'expires_at',
        'last_activity',
        'is_active',
    )
    
    fieldsets = (
        ('Session Information', {
            'fields': ('token', 'user', 'is_active')
        }),
        ('Location Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'last_activity')
        }),
    )
    
    def user_link(self, obj):
        """Display user with link"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def status_badge(self, obj):
        """Display status badge"""
        from django.utils import timezone
        if obj.expires_at and timezone.now() > obj.expires_at:
            return format_html('<span style="color: #dc3545;">Expired</span>')
        elif obj.is_active:
            return format_html('<span style="color: #28a745;">Active</span>')
        return format_html('<span style="color: #6c757d;">Inactive</span>')
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Prevent manual addition of sessions"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of sessions"""
        return True
    
    actions = ['revoke_selected_sessions']
    
    def revoke_selected_sessions(self, request, queryset):
        """Revoke selected sessions"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} sessions were revoked.')
    revoke_selected_sessions.short_description = 'Revoke selected sessions'


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    """Admin for User Login History model"""
    list_display = (
        'user_link',
        'login_time',
        'ip_address',
        'success_badge',
        'failure_reason'
    )
    
    list_filter = (
        'success',
        'login_time',
    )
    
    search_fields = (
        'user__username',
        'user__email',
        'ip_address',
        'failure_reason',
    )
    
    readonly_fields = (
        'user',
        'login_time',
        'ip_address',
        'user_agent',
        'success',
        'failure_reason',
    )
    
    fieldsets = (
        ('Login Information', {
            'fields': ('user', 'login_time', 'success')
        }),
        ('Location Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Failure Information', {
            'fields': ('failure_reason',)
        }),
    )
    
    def user_link(self, obj):
        """Display user with link"""
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def success_badge(self, obj):
        """Display success badge"""
        if obj.success:
            return format_html('<span style="color: #28a745;">✓ Success</span>')
        return format_html('<span style="color: #dc3545;">✗ Failed</span>')
    success_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Prevent manual addition of login history"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing login history"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup"""
        return request.user.is_superuser


# Optional: Add User Stats Widget to Admin Dashboard
class UserStatsWidget:
    """Custom admin dashboard widget"""
    
    @staticmethod
    def render():
        """Render user statistics"""
        from django.utils import timezone
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'online_users': UserSession.objects.filter(is_active=True).values('user').distinct().count(),
            'today_logins': UserLoginHistory.objects.filter(
                login_time__date=timezone.now().date(),
                success=True
            ).count(),
            'admins': User.objects.filter(role='admin').count(),
            'managers': User.objects.filter(role='manager').count(),
            'users': User.objects.filter(role='user').count(),
        }
        
        return format_html("""
        <div class="module" style="margin-bottom: 20px;">
            <table style="width: 100%%; border-collapse: collapse;">
                <caption>User Statistics</caption>
                <tr>
                    <th style="padding: 8px; text-align: left;">Total Users</th>
                    <td style="padding: 8px;"><strong>{total_users}</strong></td>
                    <th style="padding: 8px; text-align: left;">Active Users</th>
                    <td style="padding: 8px;"><strong>{active_users}</strong></td>
                </tr>
                <tr>
                    <th style="padding: 8px; text-align: left;">Online Now</th>
                    <td style="padding: 8px;"><strong style="color: green;">{online_users}</strong></td>
                    <th style="padding: 8px; text-align: left;">Today's Logins</th>
                    <td style="padding: 8px;"><strong>{today_logins}</strong></td>
                </tr>
                <tr>
                    <th style="padding: 8px; text-align: left;">Administrators</th>
                    <td style="padding: 8px;"><strong style="color: #dc3545;">{admins}</strong></td>
                    <th style="padding: 8px; text-align: left;">Managers</th>
                    <td style="padding: 8px;"><strong style="color: #fd7e14;">{managers}</strong></td>
                </tr>
                <tr>
                    <th style="padding: 8px; text-align: left;">Regular Users</th>
                    <td colspan="3" style="padding: 8px;"><strong style="color: #28a745;">{users}</strong></td>
                </tr>
            </table>
        </div>
        """.format(**stats))


# Optional: Add custom admin index template
class CustomAdminSite(admin.AdminSite):
    """Custom admin site with dashboard widgets"""
    
    def index(self, request, extra_context=None):
        """Override index to add widgets"""
        extra_context = extra_context or {}
        extra_context['user_stats'] = UserStatsWidget.render()
        return super().index(request, extra_context)


# Uncomment to use custom admin site
# admin_site = CustomAdminSite(name='myadmin')
# admin_site.register(User, UserAdmin)
# admin_site.register(UserSession, UserSessionAdmin)
# admin_site.register(UserLoginHistory, UserLoginHistoryAdmin)