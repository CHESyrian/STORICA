from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    ConflictException,
    BusinessLogicException,
)
from common.models.choices import WarehouseStatus

from apps.inventory.models import Warehouse


# =========================================================
# WAREHOUSE SERVICE
# =========================================================
class WarehouseService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(warehouse_id: int) -> Warehouse:
        try:
            return Warehouse.objects.get(pk=warehouse_id)
        except Warehouse.DoesNotExist:
            raise NotFoundException(
                message=(
                    f"Warehouse with id {warehouse_id} not found."
                )
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> Warehouse:
        name = validated_data["name"]

        if Warehouse.objects.filter(name=name).exists():
            raise ConflictException(
                message="A warehouse with this name already exists."
            )

        warehouse = Warehouse(
            name=name,
            description=validated_data.get("description", ""),
            location=validated_data.get("location", ""),
            phone=validated_data.get("phone", ""),
            status=validated_data.get(
                "status", WarehouseStatus.ACTIVE
            ),
        )

        warehouse.code = GenCodeEngine.warehouse(Warehouse)

        if user:
            warehouse.created_by = user
            warehouse.updated_by = user

        warehouse.save()
        return warehouse

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        warehouse_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> Warehouse:
        warehouse = Warehouse.objects.select_for_update().get(
            pk=warehouse_id
        )

        fields = ["name", "description", "location", "phone", "status"]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(warehouse, field, validated_data[field])

        if user:
            warehouse.updated_by = user

        warehouse.save()
        return warehouse

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(warehouse_id: int, user=None) -> None:
        warehouse = Warehouse.objects.select_for_update().get(
            pk=warehouse_id
        )

        if warehouse.batches.filter(is_active=True).exists():
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a warehouse that has "
                    "active batches."
                )
            )

        warehouse.soft_delete(deleted_by=user)


