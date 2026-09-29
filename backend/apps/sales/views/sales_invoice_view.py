from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.sales.models import SalesInvoice
from apps.sales.serializers.sales_invoice_serializer import (
    SalesInvoiceListSerializer,
    SalesInvoiceDetailSerializer,
    SalesInvoiceCreateSerializer,
    SalesInvoiceUpdateSerializer,
    SalesInvoiceDeleteSerializer,
)
from apps.sales.services.sales_invoice_service import (
    SalesInvoiceService,
)
from apps.sales.filters import SalesInvoiceFilter


# =========================================================
# SALES INVOICE VIEW SET
# =========================================================
class SalesInvoiceViewSet(ModelViewSet):

    filterset_class = SalesInvoiceFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        SalesInvoice.objects
        .select_related("customer", "order")
        .prefetch_related("items__variant")
        .filter(is_active=True)
    )

    search_fields    = ["code", "customer__name"]
    filterset_fields = [
        "status", "customer", "order", "is_active",
    ]
    ordering_fields  = ["invoice_date", "created_at", "code"]
    ordering         = ["-invoice_date"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : SalesInvoiceListSerializer,
            "retrieve"       : SalesInvoiceDetailSerializer,
            "create"         : SalesInvoiceCreateSerializer,
            "update"         : SalesInvoiceUpdateSerializer,
            "partial_update" : SalesInvoiceUpdateSerializer,
            "destroy"        : SalesInvoiceDeleteSerializer,
        }
        return action_map.get(
            self.action, SalesInvoiceListSerializer
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
        invoice = SalesInvoiceService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(invoice)
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

        invoice = SalesInvoiceService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = SalesInvoiceDetailSerializer(invoice)
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

        invoice = SalesInvoiceService.update(
            invoice_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = SalesInvoiceDetailSerializer(invoice)
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

        SalesInvoiceService.delete(
            invoice_id=kwargs["pk"],
            user=request.user,
        )

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # POST INVOICE (FIFO stock-out)
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="post")
    def post_invoice(self, request, *args, **kwargs):
        invoice = SalesInvoiceService.post_invoice(
            invoice_id=kwargs["pk"],
            user=request.user,
        )
        out = SalesInvoiceDetailSerializer(invoice)
        return ApiResponse.success(
            data=out.data,
            message="Invoice posted successfully.",
        )

    # --------------------------------------------------
    # CANCEL INVOICE
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, *args, **kwargs):
        invoice = SalesInvoiceService.cancel(
            invoice_id=kwargs["pk"],
            user=request.user,
        )
        out = SalesInvoiceDetailSerializer(invoice)
        return ApiResponse.success(
            data=out.data,
            message="Invoice cancelled successfully.",
        )

    # --------------------------------------------------
    # ALL SALES INVOICES (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = SalesInvoiceListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )

