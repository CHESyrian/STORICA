"""
Stock status (read-only) view — aggregated on-hand by variant × warehouse.
"""
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)
from common.pagination import StandardResultsPyQtPagination

from apps.inventory.services.stock_status_service import StockStatusService
from apps.inventory.serializers.stock_status_serializer import (
    StockStatusSerializer,
)


class StockStatusViewSet(ViewSet):
    """
    GET /api/stock-status/          — paginated list
    GET /api/stock-status/all/      — full list (no pagination)
    """

    permission_classes = [IsAuthenticatedAndActive, RolePermission]

    def _parse_filters(self, request) -> dict:
        params = request.query_params

        def _int(name):
            raw = params.get(name)
            if raw in (None, ""):
                return None
            try:
                return int(raw)
            except (TypeError, ValueError):
                return None

        def _bool(name, default=None):
            raw = params.get(name)
            if raw is None or raw == "":
                return default
            return str(raw).lower() in ("1", "true", "yes")

        return {
            "search": params.get("search") or None,
            "warehouse_id": _int("warehouse") or _int("warehouse_id"),
            "category_id": _int("category") or _int("category_id"),
            "product_id": _int("product") or _int("product_id"),
            "variant_id": _int("variant") or _int("variant_id"),
            "is_active": _bool("is_active", True),
            "zero_stock": _bool("zero_stock", False),
            "low_stock": _bool("low_stock", False),
            "ordering": params.get("ordering") or None,
        }

    def list(self, request, *args, **kwargs):
        filters = self._parse_filters(request)
        rows = StockStatusService.list_status(**filters)

        paginator = StandardResultsPyQtPagination()
        page = paginator.paginate_queryset(rows, request, view=self)
        if page is not None:
            serializer = StockStatusSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = StockStatusSerializer(rows, many=True)
        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )

    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        filters = self._parse_filters(request)
        rows = StockStatusService.list_status(**filters)
        serializer = StockStatusSerializer(rows, many=True)
        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )
