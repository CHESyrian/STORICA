from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.purchases.models import Supplier
from apps.purchases.serializers.supplier_serializer import (
    SupplierListSerializer,
    SupplierDetailSerializer,
    SupplierCreateSerializer,
    SupplierUpdateSerializer,
    SupplierDeleteSerializer,
)
from apps.purchases.services.supplier_service import SupplierService
from apps.purchases.filters import SupplierFilter


# =========================================================
# SUPPLIER VIEW SET
# =========================================================
class SupplierViewSet(ModelViewSet):

    filterset_class = SupplierFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = Supplier.objects.filter(is_active=True)

    search_fields  = ["name", "email", "phone", "code"]
    filterset_fields = ["is_verified", "is_active"]
    ordering_fields  = ["name", "created_at", "code"]
    ordering         = ["-created_at"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : SupplierListSerializer,
            "retrieve"       : SupplierDetailSerializer,
            "create"         : SupplierCreateSerializer,
            "update"         : SupplierUpdateSerializer,
            "partial_update" : SupplierUpdateSerializer,
            "destroy"        : SupplierDeleteSerializer,
        }
        return action_map.get(self.action, SupplierListSerializer)

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
        supplier = SupplierService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(supplier)
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

        supplier = SupplierService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = SupplierDetailSerializer(supplier)
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

        supplier = SupplierService.update(
            supplier_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = SupplierDetailSerializer(supplier)
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

        SupplierService.delete(
            supplier_id=kwargs["pk"],
            user=request.user,
        )

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # ALL SUPPLIERS (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = SupplierListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )
