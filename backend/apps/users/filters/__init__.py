import django_filters

from apps.users.models import User


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "role": ["exact"],
            "is_active": ["exact"],
            "is_staff": ["exact"],
            "username": ["icontains"],
            "email": ["icontains"],
            "full_name": ["icontains"],
        }
