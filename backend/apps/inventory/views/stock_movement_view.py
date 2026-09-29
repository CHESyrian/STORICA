from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.inventory.models import StockMovement
from apps.inventory.serializers.stock_movement_serializer import (
    StockMovementListSerializer,
    StockMovementDetailSerializer,
    StockMovementCreateSerializer,
    StockMovementUpdateSerializer,
    StockMovementDeleteSerializer,
)
from apps.inventory.services.stock_movement_service import (
    StockMovementService,
)
from apps.inventory.filters import StockMovementFilter


# =========================================================
# STOCK MOVEMENT VIEW SET
# =========================================================
class StockMovementViewSet(ModelViewSet):

    filterset_class = StockMovementFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        StockMovement.objects
        .select_related(
            "product",
            "batch",
            "from_warehouse",
            "to_warehouse",
            "performed_by",
            "approved_by",
            "created_by",
        )
    )

    search_fields    = [
        "movement_id",
        "reference_number",
        "product__name",
        "product__sku",
    ]
    filterset_fields = [
        "movement_type",
        "status",
        "product",
        "batch",
        "from_warehouse",
        "to_warehouse",
        "performed_by",
    ]
    ordering_fields  = [
        "movement_date",
        "created_at",
        "quantity",
    ]
    ordering         = ["-movement_date"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : StockMovementListSerializer,
            "retrieve"       : StockMovementDetailSerializer,
            "create"         : StockMovementCreateSerializer,
            "update"         : StockMovementUpdateSerializer,
            "partial_update" : StockMovementUpdateSerializer,
            "destroy"        : StockMovementDeleteSerializer,
        }
        return action_map.get(
            self.action, StockMovementListSerializer
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
        movement = StockMovementService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(movement)
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

        movement = StockMovementService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = StockMovementDetailSerializer(movement)
        return ApiResponse.success(
            data=out.data,
            message=SuccessMessages.CREATE,
            status_code=status.HTTP_201_CREATED,
        )

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movement = StockMovementService.update(
            movement_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = StockMovementDetailSerializer(movement)
        return ApiResponse.success(
            data=out.data,
            message=SuccessMessages.UPDATE,
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    # --------------------------------------------------
    # DESTROY
    # --------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        StockMovementService.delete(movement_id=kwargs["pk"])

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )
