from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.sales.models import SalesInvoiceItem
from apps.sales.serializers.sales_invoice_item_serializer import (
    SalesInvoiceItemListSerializer,
    SalesInvoiceItemDetailSerializer,
    SalesInvoiceItemCreateSerializer,
    SalesInvoiceItemUpdateSerializer,
    SalesInvoiceItemDeleteSerializer,
)
from apps.sales.services.sales_invoice_item_service import (
    SalesInvoiceItemService,
)


# =========================================================
# SALES INVOICE ITEM VIEW SET
# =========================================================
class SalesInvoiceItemViewSet(ModelViewSet):

    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        SalesInvoiceItem.objects
        .select_related("invoice__customer", "variant")
    )

    search_fields    = ["invoice__code", "variant__name"]
    filterset_fields = ["invoice", "variant"]
    ordering_fields  = ["id", "created_at"]
    ordering         = ["id"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : SalesInvoiceItemListSerializer,
            "retrieve"       : SalesInvoiceItemDetailSerializer,
            "create"         : SalesInvoiceItemCreateSerializer,
            "update"         : SalesInvoiceItemUpdateSerializer,
            "partial_update" : SalesInvoiceItemUpdateSerializer,
            "destroy"        : SalesInvoiceItemDeleteSerializer,
        }
        return action_map.get(
            self.action, SalesInvoiceItemListSerializer
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
        item = SalesInvoiceItemService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(item)
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

        item = SalesInvoiceItemService.create(
            validated_data=serializer.validated_data,
        )

        out = SalesInvoiceItemDetailSerializer(item)
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

        item = SalesInvoiceItemService.update(
            item_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            partial=partial,
        )

        out = SalesInvoiceItemDetailSerializer(item)
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

        SalesInvoiceItemService.delete(item_id=kwargs["pk"])

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )
