from rest_framework import serializers


class TrialBalanceRowSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    account_type = serializers.CharField()
    debit = serializers.DecimalField(max_digits=14, decimal_places=2)
    credit = serializers.DecimalField(max_digits=14, decimal_places=2)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2)


class TrialBalanceSerializer(serializers.Serializer):
    as_of = serializers.CharField()
    rows = TrialBalanceRowSerializer(many=True)
    totals = serializers.DictField()


class PLLineSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)


class ProfitLossSerializer(serializers.Serializer):
    date_from = serializers.CharField()
    date_to = serializers.CharField()
    income = PLLineSerializer(many=True)
    expense = PLLineSerializer(many=True)
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=14, decimal_places=2)


class AccountSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    account_type = serializers.CharField()
    is_active = serializers.BooleanField()
    is_system = serializers.BooleanField()
    description = serializers.CharField(allow_blank=True)
