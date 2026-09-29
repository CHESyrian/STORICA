"""
Each DTO is a frozen dataclass with a `from_dict` classmethod that
parses the raw API response (strings for decimals/dates/datetimes)
into proper Python types.
"""

from __future__ import annotations

from typing import Optional
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


# ==============================================================
# HELPER FUNCTIONS
# ==============================================================
def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _parse_decimal(value: str | None) -> Decimal | None:
    return Decimal(value) if value not in (None, "") else None


# ==============================================================
# WORKER ERRORS DTO
# ==============================================================
@dataclass
class WorkerError:
    type: str
    message: str
    traceback: str


# ==============================================================
# PRODUCTS DTO
# ==============================================================
@dataclass(slots=True)
class ProductDTO:
    id: int
    sku: str
    slug: str
    name: str
    category: int
    category_name: str
    unit: str
    is_active: bool
    created_at: str

    @classmethod
    def from_dict(cls, data: dict) -> "ProductDTO":
        return cls(
            id=data["id"],
            sku=data["sku"],
            slug=data["slug"],
            name=data["name"],
            category=data["category"],
            category_name=data["category_name"],
            unit=data["unit"],
            is_active=data["is_active"],
            created_at=data["created_at"],
        )


# ==========================================================================================
# Category
# ==========================================================================================
@dataclass(frozen=True)
class CategoryDTO:
    id: int
    code: str
    slug: str
    name: str
    parent: int | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "CategoryDTO":
        return cls(
            id=data["id"],
            code=data["code"],
            slug=data["slug"],
            name=data["name"],
            parent=data.get("parent"),
            is_active=data["is_active"],
            created_at=_parse_datetime(data["created_at"]),
        )



# ==========================================================================================
# Warehouse
# ==========================================================================================
@dataclass(frozen=True)
class WarehouseDTO:
    id: int
    code: str
    slug: str
    name: str
    location: str
    phone: str
    status: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "WarehouseDTO":
        return cls(
            id=data["id"],
            code=data["code"],
            slug=data["slug"],
            name=data["name"],
            location=data["location"],
            phone=data["phone"],
            status=data["status"],
            is_active=data["is_active"],
            created_at=_parse_datetime(data["created_at"]),
        )


# ==========================================================================================
# Batch
# ==========================================================================================
@dataclass(frozen=True)
class BatchDTO:
    id: int
    code: str
    slug: str
    variant: int
    variant_sku: str
    warehouse: int
    warehouse_name: str
    quantity: Decimal
    cost_price: Decimal
    production_date: date
    expiry_date: date
    status: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "BatchDTO":
        return cls(
            id=data["id"],
            code=data["code"],
            slug=data["slug"],
            variant=data["variant"],
            variant_sku=data["variant_sku"],
            warehouse=data["warehouse"],
            warehouse_name=data["warehouse_name"],
            quantity=_parse_decimal(data["quantity"]),
            cost_price=_parse_decimal(data["cost_price"]),
            production_date=_parse_date(data["production_date"]),
            expiry_date=_parse_date(data["expiry_date"]),
            status=data["status"],
            is_active=data["is_active"],
            created_at=_parse_datetime(data["created_at"]),
        )


# ==========================================================================================
# Stock Movement
# ==========================================================================================
@dataclass(frozen=True)
class StockMovementDTO:
    id: int
    movement_id: str
    movement_type: str
    movement_type_display: str
    status: str
    status_display: str
    product: int
    product_name: str
    quantity: Decimal
    unit_price: Decimal
    movement_date: datetime
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "StockMovementDTO":
        return cls(
            id=data["id"],
            movement_id=data["movement_id"],
            movement_type=data["movement_type"],
            movement_type_display=data["movement_type_display"],
            status=data["status"],
            status_display=data["status_display"],
            product=data["product"],
            product_name=data["product_name"],
            quantity=_parse_decimal(data["quantity"]),
            unit_price=_parse_decimal(data["unit_price"]),
            movement_date=_parse_datetime(data["movement_date"]),
            created_at=_parse_datetime(data["created_at"]),
        )


# ==========================================================================================
# Variant
# ==========================================================================================
@dataclass(frozen=True)
class VariantDTO:
    id: int
    sku: str
    slug: str
    product: int
    product_name: str
    product_sku: str
    name: str
    quantity: Decimal
    color: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> "VariantDTO":
        return cls(
            id=data["id"],
            sku=data["sku"],
            slug=data["slug"],
            product=data["product"],
            product_name=data["product_name"],
            product_sku=data["product_sku"],
            name=data["name"],
            quantity=_parse_decimal(data["quantity"]),
            color=data["color"],
            is_active=data["is_active"],
            created_at=_parse_datetime(data["created_at"]),
        )

