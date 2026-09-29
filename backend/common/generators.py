import uuid
import secrets

from django.db import IntegrityError
from django.utils import timezone


# =====================================================
# CONFIG
# =====================================================
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


# =====================================================
# INTERNAL HELPERS
# =====================================================
def _encode_uuid(value: uuid.UUID) -> str:
    """
    Convert UUID4 into compact base32 string.
    """
    num = value.int
    chars = []

    for _ in range(26):
        num, rem = divmod(num, 32)
        chars.append(ALPHABET[rem])

    return "".join(reversed(chars))


def _raw_code(length: int = 15) -> str:
    raw = _encode_uuid(uuid.uuid4())
    raw = raw[:length]

    return "-".join([
        raw[0:5],
        raw[5:10],
        raw[10:15],
    ])


def _date() -> str:
    return timezone.now().strftime("%Y%m%d")


# =====================================================
# BASE STRATEGY
# =====================================================
class CodeStrategy:
    prefix = ""

    @classmethod
    def format(cls, raw: str) -> str:
        return raw

    @classmethod
    def generate(cls) -> str:
        code = cls.format(_raw_code())

        if cls.prefix:
            return f"{cls.prefix}-{_date()}-{code}"

        return f"{_date()}-{code}"


# =====================================================
# STRATEGIES
# =====================================================
class WarehouseCode(CodeStrategy):
    prefix = "WH"


class CategoryCode(CodeStrategy):
    prefix = "CAT"


class SKUCode(CodeStrategy):
    prefix = "SKU"


class CustomerCode(CodeStrategy):
    prefix = "CT"


class SupplierCode(CodeStrategy):
    prefix = "SP"


class SalesOrderCode(CodeStrategy):
    prefix = "SO"

    @classmethod
    def format(cls, raw: str) -> str:
        p = raw.split("-")
        return f"{p[0]}-{p[1]}"


class PurchasesOrderCode(CodeStrategy):
    prefix = "PO"

    @classmethod
    def format(cls, raw: str) -> str:
        p = raw.split("-")
        return f"{p[0]}-{p[1]}"


class SalesInvoiceCode(CodeStrategy):
    prefix = "SI"

    @classmethod
    def format(cls, raw: str) -> str:
        p = raw.split("-")
        return f"{p[0]}-{p[1]}"


class PurchasesInvoiceCode(CodeStrategy):
    prefix = "PI"

    @classmethod
    def format(cls, raw: str) -> str:
        p = raw.split("-")
        return f"{p[0]}-{p[1]}"


class BatchCode(CodeStrategy):
    prefix = "BAT"


# =====================================================
# SAFE UNIQUE GENERATOR
# =====================================================
def generate_unique_code(
    model,
    field: str,
    strategy,
    max_attempts: int = 20,
):
    """
    Generate collision-safe unique code.

    True uniqueness is enforced by DB unique constraints.
    """

    for _ in range(max_attempts):
        code = strategy.generate()

        exists = model.objects.filter(
            **{field: code}
        ).exists()

        if not exists:
            return code

    raise RuntimeError(
        f"Could not generate unique {field}"
    )

# =====================================================
# GENERATE TRANSACTION ID
# =====================================================
def generate_transaction_id(prefix="TXN"):
    """
    Generate a unique, human-readable financial transaction ID.

    Example:
        TXN-20260811-083045-A7K9X2
    """
    timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")
    random_part = secrets.token_hex(3).upper()

    return f"{prefix}-{timestamp}-{random_part}"


# =====================================================
# ERP ENGINE FACADE (PUBLIC API)
# =====================================================
class GenCodeEngine:
    """
    Single entry point for all ERP codes
    """

    @staticmethod
    def warehouse(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=WarehouseCode,
        )

    @staticmethod
    def category(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=CategoryCode,
        )

    @staticmethod
    def customer(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=CustomerCode,
        )

    @staticmethod
    def supplier(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=SupplierCode,
        )

    @staticmethod
    def sku(model):
        return generate_unique_code(
            model=model,
            field="sku",
            strategy=SKUCode,
        )

    @staticmethod
    def sales_order(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=SalesOrderCode,
        )

    @staticmethod
    def purchase_order(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=PurchasesOrderCode,
        )

    @staticmethod
    def salas_invoice(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=SalesInvoiceCode,
        )

    @staticmethod
    def purchase_invoice(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=PurchasesInvoiceCode,
        )

    @staticmethod
    def batch(model):
        return generate_unique_code(
            model=model,
            field="code",
            strategy=BatchCode,
        )

    @staticmethod
    def transaction(prefix):
        return generate_transaction_id(
            prefix=prefix
        )



