import django_filters

from users.models import User


class ProfileFilterSet(django_filters.FilterSet):
    """Фильтры по параметрам из задания: пол, возраст, город, статус."""

    age_min = django_filters.NumberFilter(field_name="age", lookup_expr="gte")
    age_max = django_filters.NumberFilter(field_name="age", lookup_expr="lte")

    class Meta:
        model = User
        fields = ["gender", "city", "status", "age_min", "age_max"]
