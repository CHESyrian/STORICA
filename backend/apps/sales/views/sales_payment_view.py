from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.sales.models import SalesPayment
from apps.sales.serializers.sales_payment_serializer import (
    SalesPaymentListSerializer,
    SalesPaymentDetailSerializer,
    SalesPaymentCreateSerializer,
    SalesPaymentUpdateSerializer,
    SalesPaymentDeleteSerializer,
)
from apps.sales.services.sales_payment_service import (
    SalesPaymentService,
)
from apps.sales.filters import SalesPaymentFilter


# =========================================================
# SALES PAYMENT VIEW SET
# =========================================================
class SalesPaymentViewSet(ModelViewSet):

    filterset_class = SalesPaymentFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        SalesPayment.objects
        .select_related(
            "invoice__customer",
            "order",
            "customer",
            "processed_by",
        )
    )

    search_fields    = [
        "transaction_id",
        "reference_number",
        "customer__name",
        "invoice__code",
    ]
    filterset_fields = ["status", "customer", "invoice", "order"]
    ordering_fields  = ["payment_date", "created_at", "amount"]
    ordering         = ["-payment_date"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : SalesPaymentListSerializer,
            "retrieve"       : SalesPaymentDetailSerializer,
            "create"         : SalesPaymentCreateSerializer,
            "update"         : SalesPaymentUpdateSerializer,
            "partial_update" : SalesPaymentUpdateSerializer,
            "destroy"        : SalesPaymentDeleteSerializer,
        }
        return action_map.get(
            self.action, SalesPaymentListSerializer
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
        payment = SalesPaymentService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(payment)
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

        payment = SalesPaymentService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = SalesPaymentDetailSerializer(payment)
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

        payment = SalesPaymentService.update(
            payment_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            partial=partial,
        )

        out = SalesPaymentDetailSerializer(payment)
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

        SalesPaymentService.delete(payment_id=kwargs["pk"])

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # REFUND PAYMENT
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="refund")
    def refund(self, request, *args, **kwargs):
        payment = SalesPaymentService.refund(
            payment_id=kwargs["pk"],
            user=request.user,
        )
        out = SalesPaymentDetailSerializer(payment)
        return ApiResponse.success(
            data=out.data,
            message="Payment refunded successfully.",
        )

    # --------------------------------------------------
    # ALL SALES PAYMENTS (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = SalesPaymentListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )

