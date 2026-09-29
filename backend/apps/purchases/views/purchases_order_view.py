from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.purchases.models import PurchasesOrder
from apps.purchases.serializers.purchases_order_serializer import (
    PurchasesOrderListSerializer,
    PurchasesOrderDetailSerializer,
    PurchasesOrderCreateSerializer,
    PurchasesOrderUpdateSerializer,
    PurchasesOrderDeleteSerializer,
)
from apps.purchases.services.purchases_order_service import (
    PurchasesOrderService,
)
from apps.purchases.filters import PurchasesOrderFilter


# =========================================================
# PURCHASES ORDER VIEW SET
# =========================================================
class PurchasesOrderViewSet(ModelViewSet):

    filterset_class = PurchasesOrderFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        PurchasesOrder.objects
        .select_related("supplier")
        .prefetch_related("items__variant")
        .filter(is_active=True)
    )

    search_fields    = ["code", "supplier__name", "notes"]
    filterset_fields = ["status", "supplier", "is_active"]
    ordering_fields  = ["order_date", "created_at", "code"]
    ordering         = ["-order_date"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : PurchasesOrderListSerializer,
            "retrieve"       : PurchasesOrderDetailSerializer,
            "create"         : PurchasesOrderCreateSerializer,
            "update"         : PurchasesOrderUpdateSerializer,
            "partial_update" : PurchasesOrderUpdateSerializer,
            "destroy"        : PurchasesOrderDeleteSerializer,
        }
        return action_map.get(
            self.action, PurchasesOrderListSerializer
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
        order = PurchasesOrderService.get_by_id(kwargs["pk"])
        serializer = self.get_serializer(order)
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

        order = PurchasesOrderService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = PurchasesOrderDetailSerializer(order)
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

        order = PurchasesOrderService.update(
            order_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = PurchasesOrderDetailSerializer(order)
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

        PurchasesOrderService.delete(
            order_id=kwargs["pk"],
            user=request.user,
        )

        return ApiResponse.success(
            message=SuccessMessages.DESTROY,
            status_code=status.HTTP_200_OK,
        )

    # --------------------------------------------------
    # CONFIRM ACTION (draft → confirmed)
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, *args, **kwargs):
        order = PurchasesOrderService.confirm(
            order_id=kwargs["pk"],
            user=request.user,
        )
        out = PurchasesOrderDetailSerializer(order)
        return ApiResponse.success(
            data=out.data,
            message="Order confirmed successfully.",
        )

    # --------------------------------------------------
    # COMPLETE ACTION
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, *args, **kwargs):
        order = PurchasesOrderService.complete(
            order_id=kwargs["pk"],
            user=request.user,
        )
        out = PurchasesOrderDetailSerializer(order)
        return ApiResponse.success(
            data=out.data,
            message="Order completed successfully.",
        )

    # --------------------------------------------------
    # CANCEL ACTION
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, *args, **kwargs):
        order = PurchasesOrderService.cancel(
            order_id=kwargs["pk"],
            user=request.user,
        )
        out = PurchasesOrderDetailSerializer(order)
        return ApiResponse.success(
            data=out.data,
            message="Order cancelled successfully.",
        )

    # --------------------------------------------------
    # ALL ORDERS (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = PurchasesOrderListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )
        
