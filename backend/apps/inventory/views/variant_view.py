from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.inventory.models import Variant
from apps.inventory.serializers.variant_serializer import (
    VariantListSerializer,
    VariantDetailSerializer,
    VariantCreateSerializer,
    VariantUpdateSerializer,
    VariantDeleteSerializer,
)
from apps.inventory.services.variant_service import VariantService
from apps.inventory.filters import VariantFilter


# =========================================================
# VARIANT VIEW SET
# =========================================================
class VariantViewSet(ModelViewSet):

    filterset_class = VariantFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        Variant.objects
        .select_related("product__category")
        .filter(is_active=True)
    )

    search_fields    = ["sku", "name", "color", "product__name"]
    filterset_fields = ["product", "is_active"]
    ordering_fields  = ["sku", "name", "quantity", "created_at"]
    ordering         = ["product", "sku"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : VariantListSerializer,
            "retrieve"       : VariantDetailSerializer,
            "create"         : VariantCreateSerializer,
            "update"         : VariantUpdateSerializer,
            "partial_update" : VariantUpdateSerializer,
            "destroy"        : VariantDeleteSerializer,
        }
        return action_map.get(self.action, VariantListSerializer)

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
        variant = VariantService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(variant)
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

        variant = VariantService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = VariantDetailSerializer(variant)
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

        variant = VariantService.update(
            variant_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = VariantDetailSerializer(variant)
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

        VariantService.delete(
            variant_id=kwargs["pk"],
            user=request.user,
        )

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # ALL VARIANTS (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = VariantListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )
