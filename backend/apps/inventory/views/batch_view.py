from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.inventory.models import Batch
from apps.inventory.serializers.batch_serializer import (
    BatchListSerializer,
    BatchDetailSerializer,
    BatchCreateSerializer,
    BatchUpdateSerializer,
    BatchDeleteSerializer,
)
from apps.inventory.services.batch_service import BatchService
from apps.inventory.filters import BatchFilter


# =========================================================
# BATCH VIEW SET
# =========================================================
class BatchViewSet(ModelViewSet):

    filterset_class = BatchFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        Batch.objects
        .select_related("variant__product", "warehouse")
        .filter(is_active=True)
    )

    search_fields    = [
        "code",
        "variant__sku",
        "variant__name",
        "warehouse__name",
    ]
    filterset_fields = [
        "status",
        "variant",
        "warehouse",
        "is_active",
    ]
    ordering_fields  = [
        "expiry_date",
        "production_date",
        "received_date",
        "created_at",
    ]
    ordering         = ["expiry_date"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : BatchListSerializer,
            "retrieve"       : BatchDetailSerializer,
            "create"         : BatchCreateSerializer,
            "update"         : BatchUpdateSerializer,
            "partial_update" : BatchUpdateSerializer,
            "destroy"        : BatchDeleteSerializer,
        }
        return action_map.get(self.action, BatchListSerializer)

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
        batch = BatchService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(batch)
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

        batch = BatchService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = BatchDetailSerializer(batch)
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

        batch = BatchService.update(
            batch_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = BatchDetailSerializer(batch)
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

        BatchService.delete(
            batch_id=kwargs["pk"],
            user=request.user,
        )

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )
