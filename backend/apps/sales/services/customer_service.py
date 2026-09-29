from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    ConflictException,
    BusinessLogicException,
)

from apps.sales.models import Customer


# =========================================================
# CUSTOMER SERVICE
# =========================================================
class CustomerService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(customer_id: int) -> Customer:
        try:
            return Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise NotFoundException(
                message=f"Customer with id {customer_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> Customer:
        if Customer.objects.filter(
            email=validated_data["email"]
        ).exists():
            raise ConflictException(
                message=(
                    "A customer with this email already exists."
                )
            )

        customer = Customer(
            name=validated_data["name"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            address=validated_data["address"],
            is_verified=validated_data.get("is_verified", False),
            notes=validated_data.get("notes", ""),
        )

        customer.code = GenCodeEngine.customer(Customer)

        if user:
            customer.created_by = user
            customer.updated_by = user

        customer.save()
        return customer

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        customer_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> Customer:
        customer = Customer.objects.select_for_update().get(
            pk=customer_id
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
                setattr(customer, field, validated_data[field])

        if user:
            customer.updated_by = user

        customer.save()
        return customer

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(customer_id: int, user=None) -> None:
        customer = Customer.objects.select_for_update().get(
            pk=customer_id
        )

        if customer.orders.filter(
            status__in=["confirmed", "processing"]
        ).exists():
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a customer with "
                    "active orders."
                )
            )

        customer.soft_delete(deleted_by=user)
