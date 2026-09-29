from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.inventory.models import Warehouse
from apps.inventory.serializers.warehouse_serializer import (
    WarehouseListSerializer,
    WarehouseDetailSerializer,
    WarehouseCreateSerializer,
    WarehouseUpdateSerializer,
    WarehouseDeleteSerializer,
)
from apps.inventory.services.warehouse_service import (
    WarehouseService,
)
from apps.inventory.filters import WarehouseFilter


# =========================================================
# WAREHOUSE VIEW SET
# =========================================================
class WarehouseViewSet(ModelViewSet):

    filterset_class = WarehouseFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = Warehouse.objects.filter(is_active=True)

    search_fields    = ["name", "code", "location", "phone"]
    filterset_fields = ["status", "is_active"]
    ordering_fields  = ["name", "created_at", "status"]
    ordering         = ["name"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : WarehouseListSerializer,
            "retrieve"       : WarehouseDetailSerializer,
            "create"         : WarehouseCreateSerializer,
            "update"         : WarehouseUpdateSerializer,
            "partial_update" : WarehouseUpdateSerializer,
            "destroy"        : WarehouseDeleteSerializer,
        }
        return action_map.get(
            self.action, WarehouseListSerializer
        )

    # --------------------------------------------------
    # LIST
    # --------------------------------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    def retrieve(self, request, *args, **kwargs):
        warehouse = WarehouseService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(warehouse)
        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        warehouse = WarehouseService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = WarehouseDetailSerializer(warehouse)
        return ApiResponse.success(
            data=out.data,
            message=SuccessMessages.CREATE,
            status_code=status.HTTP_201_CREATED,
        )

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        warehouse = WarehouseService.update(
            warehouse_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = WarehouseDetailSerializer(warehouse)
        return ApiResponse.success(
            data=out.data,
            message=SuccessMessages.UPDATE,
        )

    # --------------------------------------------------
    # DESTROY
    # --------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        WarehouseService.delete(
            warehouse_id=kwargs["pk"],
            user=request.user,
        )

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # ALL WAREHOUSES (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = WarehouseListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )
