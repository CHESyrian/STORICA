"""
Accounting report endpoints — trial balance and profit & loss.
"""

from datetime import datetime

from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action

from common.api_response import ApiResponse
from common.constants import SuccessMessages
from common.permissions import IsAuthenticatedAndActive, RolePermission

from apps.accounting.models import Account
from apps.accounting.services import (
    AccountingReportService,
    ChartOfAccountsService,
)
from apps.accounting.serializers.report_serializer import (
    TrialBalanceSerializer,
    ProfitLossSerializer,
    AccountSerializer,
)


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


class AccountingReportViewSet(ViewSet):
    """
    GET /api/accounting/trial-balance/?as_of=YYYY-MM-DD
    GET /api/accounting/profit-loss/?from=YYYY-MM-DD&to=YYYY-MM-DD
    GET /api/accounting/accounts/
    POST /api/accounting/seed-coa/   (manager+)
    """

    permission_classes = [IsAuthenticatedAndActive, RolePermission]

    @action(detail=False, methods=["get"], url_path="trial-balance")
    def trial_balance(self, request):
        as_of = _parse_date(request.query_params.get("as_of"))
        data = AccountingReportService.trial_balance(as_of=as_of)
        ser = TrialBalanceSerializer(data)
        return ApiResponse.success(
            data=ser.data,
            message=SuccessMessages.RETRIEVE,
        )

    @action(detail=False, methods=["get"], url_path="profit-loss")
    def profit_loss(self, request):
        date_from = _parse_date(
            request.query_params.get("from")
            or request.query_params.get("date_from")
        )
        date_to = _parse_date(
            request.query_params.get("to")
            or request.query_params.get("date_to")
        )
        data = AccountingReportService.profit_and_loss(
            date_from=date_from,
            date_to=date_to,
        )
        ser = ProfitLossSerializer(data)
        return ApiResponse.success(
            data=ser.data,
            message=SuccessMessages.RETRIEVE,
        )

    @action(detail=False, methods=["get"], url_path="accounts")
    def accounts(self, request):
        ChartOfAccountsService.seed_defaults()
        qs = Account.objects.filter(is_active=True).order_by("code")
        ser = AccountSerializer(qs, many=True)
        return ApiResponse.success(
            data=ser.data,
            message=SuccessMessages.RETRIEVE,
        )

    @action(detail=False, methods=["post"], url_path="seed-coa")
    def seed_coa(self, request):
        accounts = ChartOfAccountsService.seed_defaults(force=False)
        return ApiResponse.success(
            data={"count": len(accounts)},
            message="Chart of accounts seeded.",
        )
