import django_filters    


# ========================================================================

class DateRangeFilterSet(django_filters.FilterSet):

    created_from = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
    )

    created_to = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
    )

    updated_from = django_filters.DateFilter(
        field_name="updated_at",
        lookup_expr="date__gte",
    )

    updated_to = django_filters.DateFilter(
        field_name="updated_at",
        lookup_expr="date__lte",
    )


# ========================================================================

class ExpiredRangeFilterSet(django_filters.FilterSet):

    expired_from = django_filters.DateFilter(
        field_name="expiry_date",
        lookup_expr="date__gte",
    )

    expired_to = django_filters.DateFilter(
        field_name="expiry_date",
        lookup_expr="date__lte",
    )


# ========================================================================

class ProductionRangeFilterSet(DateRangeFilterSet):

    produced_from = django_filters.DateFilter(
        field_name="production_date",
        lookup_expr="date__gte",
    )

    produced_to = django_filters.DateFilter(
        field_name="production_date",
        lookup_expr="date__lte",
    )

    expired_from = django_filters.DateFilter(
        field_name="expiry_date",
        lookup_expr="date__gte",
    )

    expired_to = django_filters.DateFilter(
        field_name="expiry_date",
        lookup_expr="date__lte",
    )


# ========================================================================

