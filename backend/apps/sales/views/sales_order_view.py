from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import (
    IsAuthenticatedAndActive,
    RolePermission,
)

from apps.sales.models import SalesOrder
from apps.sales.serializers.sales_order_serializer import (
    SalesOrderListSerializer,
    SalesOrderDetailSerializer,
    SalesOrderCreateSerializer,
    SalesOrderUpdateSerializer,
    SalesOrderDeleteSerializer,
)
from apps.sales.services.sales_order_service import SalesOrderService
from apps.sales.filters import SalesOrderFilter


# =========================================================
# SALES ORDER VIEW SET
# =========================================================
class SalesOrderViewSet(ModelViewSet):

    filterset_class = SalesOrderFilter
    permission_classes = [IsAuthenticatedAndActive, RolePermission]
    queryset = (
        SalesOrder.objects
        .select_related("customer")
        .prefetch_related("items__variant")
        .filter(is_active=True)
    )

    search_fields    = ["code", "customer__name", "notes"]
    filterset_fields = ["status", "customer", "is_active"]
    ordering_fields  = ["order_date", "created_at", "code"]
    ordering         = ["-order_date"]

    # --------------------------------------------------
    # SERIALIZER ROUTING
    # --------------------------------------------------
    def get_serializer_class(self):
        action_map = {
            "list"           : SalesOrderListSerializer,
            "retrieve"       : SalesOrderDetailSerializer,
            "create"         : SalesOrderCreateSerializer,
            "update"         : SalesOrderUpdateSerializer,
            "partial_update" : SalesOrderUpdateSerializer,
            "destroy"        : SalesOrderDeleteSerializer,
        }
        return action_map.get(
            self.action, SalesOrderListSerializer
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
        order = SalesOrderService.get_by_id(kwargs["pk"])
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

        order = SalesOrderService.create(
            validated_data=serializer.validated_data,
            user=request.user,
        )

        out = SalesOrderDetailSerializer(order)
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

        order = SalesOrderService.update(
            order_id=kwargs["pk"],
            validated_data=serializer.validated_data,
            user=request.user,
            partial=partial,
        )

        out = SalesOrderDetailSerializer(order)
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

        SalesOrderService.delete(
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
        order = SalesOrderService.confirm(
            order_id=kwargs["pk"],
            user=request.user,
        )
        out = SalesOrderDetailSerializer(order)
        return ApiResponse.success(
            data=out.data,
            message="Order confirmed successfully.",
        )

    # --------------------------------------------------
    # COMPLETE ACTION
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, *args, **kwargs):
        order = SalesOrderService.complete(
            order_id=kwargs["pk"],
            user=request.user,
        )
        out = SalesOrderDetailSerializer(order)
        return ApiResponse.success(
            data=out.data,
            message="Order completed successfully.",
        )

    # --------------------------------------------------
    # CANCEL ACTION
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, *args, **kwargs):
        order = SalesOrderService.cancel(
            order_id=kwargs["pk"],
            user=request.user,
        )
        out = SalesOrderDetailSerializer(order)
        return ApiResponse.success(
            data=out.data,
            message="Order cancelled successfully.",
        )

    # --------------------------------------------------
    # ALL SALES ORDERS (NO PAGINATION)
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="all")
    def all(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = SalesOrderListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return ApiResponse.success(
            data=serializer.data,
            message=SuccessMessages.RETRIEVE,
        )

