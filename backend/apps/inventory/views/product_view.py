from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.inventory.models import Product
from apps.inventory.serializers.product_serializer import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    ProductUpdateSerializer,
    ProductDeleteSerializer,
)
from apps.inventory.services.product_service import ProductService
from apps.inventory.filters import ProductFilter


# =========================================================
# PRODUCT VIEW SET
# =========================================================
class ProductViewSet(ModelViewSet):

    filterset_class = ProductFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        Product.objects
        .select_related("category")
        .filter(is_active=True)
    )

    search_fields    = ["name", "sku", "description"]
    filterset_fields = ["category", "unit", "is_active"]
    ordering_fields  = ["name", "sku", "created_at"]
    ordering         = ["name"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : ProductListSerializer,
            "retrieve"       : ProductDetailSerializer,
            "create"         : ProductCreateSerializer,
            "update"         : ProductUpdateSerializer,
            "partial_update" : ProductUpdateSerializer,
            "destroy"        : ProductDeleteSerializer,
        }
        return action_map.get(self.action, ProductListSerializer)

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
        product = ProductService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(product)
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

        product = ProductService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = ProductDetailSerializer(product)
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

        product = ProductService.update(
            product_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = ProductDetailSerializer(product)
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

        ProductService.delete(
            product_id=kwargs["pk"],
            user=request.user,
        )

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # ALL PRODUCTS (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = ProductListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )
