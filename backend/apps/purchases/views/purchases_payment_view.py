from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.purchases.models import PurchasesPayment
from apps.purchases.serializers.purchases_payment_serializer import (
    PurchasesPaymentListSerializer,
    PurchasesPaymentDetailSerializer,
    PurchasesPaymentCreateSerializer,
    PurchasesPaymentUpdateSerializer,
    PurchasesPaymentDeleteSerializer,
)
from apps.purchases.services.purchases_payment_service import (
    PurchasesPaymentService,
)
from apps.purchases.filters import PurchasesPaymentFilter


# =========================================================
# PURCHASES PAYMENT VIEW SET
# =========================================================
class PurchasesPaymentViewSet(ModelViewSet):

    filterset_class = PurchasesPaymentFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        PurchasesPayment.objects
        .select_related(
            "invoice__supplier",
            "order",
            "supplier",
            "processed_by",
        )
    )

    search_fields    = [
        "transaction_id",
        "reference_number",
        "supplier__name",
        "invoice__code",
    ]
    filterset_fields = ["status", "supplier", "invoice", "order"]
    ordering_fields  = ["payment_date", "created_at", "amount"]
    ordering         = ["-payment_date"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : PurchasesPaymentListSerializer,
            "retrieve"       : PurchasesPaymentDetailSerializer,
            "create"         : PurchasesPaymentCreateSerializer,
            "update"         : PurchasesPaymentUpdateSerializer,
            "partial_update" : PurchasesPaymentUpdateSerializer,
            "destroy"        : PurchasesPaymentDeleteSerializer,
        }
        return action_map.get(
            self.action, PurchasesPaymentListSerializer
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
        payment = PurchasesPaymentService.get_by_id(kwargs["pk"])
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

        payment = PurchasesPaymentService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = PurchasesPaymentDetailSerializer(payment)
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

        payment = PurchasesPaymentService.update(
            payment_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            partial=partial,
        )

        out = PurchasesPaymentDetailSerializer(payment)
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

        PurchasesPaymentService.delete(payment_id=kwargs["pk"])

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # REFUND PAYMENT
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="refund")
    def refund(self, request, *args, **kwargs):
        payment = PurchasesPaymentService.refund(
            payment_id=kwargs["pk"],
            user=request.user,
        )
        out = PurchasesPaymentDetailSerializer(payment)
        return ApiResponse.success(
            data=out.data,
            message="Payment refunded successfully.",
        )

    # --------------------------------------------------
    # ALL PAYMENTS (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = PurchasesPaymentListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )

