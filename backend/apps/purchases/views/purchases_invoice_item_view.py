from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.purchases.models import PurchasesInvoiceItem
from apps.purchases.serializers.purchases_invoice_item_serializer import (
    PurchasesInvoiceItemListSerializer,
    PurchasesInvoiceItemDetailSerializer,
    PurchasesInvoiceItemCreateSerializer,
    PurchasesInvoiceItemUpdateSerializer,
    PurchasesInvoiceItemDeleteSerializer,
)
from apps.purchases.services.purchases_invoice_item_service import (
    PurchasesInvoiceItemService,
)


# =========================================================
# PURCHASES INVOICE ITEM VIEW SET
# =========================================================
class PurchasesInvoiceItemViewSet(ModelViewSet):

    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        PurchasesInvoiceItem.objects
        .select_related("invoice__supplier", "variant")
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
            "list"           : PurchasesInvoiceItemListSerializer,
            "retrieve"       : PurchasesInvoiceItemDetailSerializer,
            "create"         : PurchasesInvoiceItemCreateSerializer,
            "update"         : PurchasesInvoiceItemUpdateSerializer,
            "partial_update" : PurchasesInvoiceItemUpdateSerializer,
            "destroy"        : PurchasesInvoiceItemDeleteSerializer,
        }
        return action_map.get(
            self.action, PurchasesInvoiceItemListSerializer
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
        item = PurchasesInvoiceItemService.get_by_id(kwargs["pk"])
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

        item = PurchasesInvoiceItemService.create(
            validated_data=serializer.validated_data,
        )

        out = PurchasesInvoiceItemDetailSerializer(item)
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

        item = PurchasesInvoiceItemService.update(
            item_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            partial=partial,
        )

        out = PurchasesInvoiceItemDetailSerializer(item)
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

        PurchasesInvoiceItemService.delete(item_id=kwargs["pk"])

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )
