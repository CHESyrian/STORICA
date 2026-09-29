from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    ConflictException,
    BusinessLogicException,
)

from apps.purchases.models import Supplier


# =========================================================
# SUPPLIER SERVICE
# =========================================================
class SupplierService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(supplier_id: int) -> Supplier:
        try:
            return Supplier.objects.get(pk=supplier_id)
        except Supplier.DoesNotExist:
            raise NotFoundException(
                message=f"Supplier with id {supplier_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> Supplier:
        if Supplier.objects.filter(
            email=validated_data["email"]
        ).exists():
            raise ConflictException(
                message="A supplier with this email already exists."
            )

        supplier = Supplier(
            name=validated_data["name"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            address=validated_data["address"],
            is_verified=validated_data.get("is_verified", False),
            notes=validated_data.get("notes", ""),
        )

        supplier.code = GenCodeEngine.supplier(Supplier)

        if user:
            supplier.created_by = user
            supplier.updated_by = user

        supplier.save()
        return supplier

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        supplier_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> Supplier:
        supplier = Supplier.objects.select_for_update().get(
            pk=supplier_id
        )

        fields = [
            "name",
            "email",
            "phone",
            "address",
            "is_verified",
            "notes",
        ]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(supplier, field, validated_data[field])

        if user:
            supplier.updated_by = user

        supplier.save()
        return supplier

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(supplier_id: int, user=None) -> None:
        supplier = Supplier.objects.select_for_update().get(
            pk=supplier_id
        )

        if supplier.orders.filter(
            status__in=["confirmed", "processing"]
        ).exists():
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a supplier with active orders."
                )
            )

        supplier.soft_delete(deleted_by=user)
