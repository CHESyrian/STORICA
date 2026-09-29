from django.db import models


class OrderStatus(models.TextChoices):
    DRAFT      = "draft", "Draft"
    CONFIRMED  = "confirmed", "Confirmed"
    PROCESSING = "processing", "Processing"
    SHIPPED    = "shipped", "Shipped"
    DELIVERED  = "delivered", "Delivered"
    COMPLETED  = "completed", "Completed"
    CANCELLED  = "cancelled", "Cancelled"
    RETURNED   = "returned", "Returned"


class InvoiceStatus(models.TextChoices):
    DRAFT     = "draft", "Draft"
    SENT      = "sent", "Sent"
    PAID      = "paid", "Paid"
    PARTIAL   = "partial", "Partially Paid"
    OVERDUE   = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"
    REFUNDED  = "refunded", "Refunded"


class PaymentStatus(models.TextChoices):
    PENDING   = "pending", "Pending"
    PARTIAL   = "partial", "Partial"
    COMPLETED = "completed", "Completed"
    FAILED    = "failed", "Failed"
    REFUNDED  = "refunded", "Refunded"


class WarehouseStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    MAINTENANCE = "maintenance", "Under Maintenance"


class BatchStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    EXPIRED = "expired", "Expired"
    RECALLED = "recalled", "Recalled"
    SOLD_OUT = "sold_out", "Sold Out"


class StockMovementType(models.TextChoices):
    IN = "in", "Stock In"
    OUT = "out", "Stock Out"
    TRANSFER = "transfer", "Transfer"
    ADJUSTMENT = "adjustment", "Adjustment"
    RETURN = "return", "Return"


class MovementStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class UnitChoices(models.TextChoices):
    PCS = "pcs", "Pieces"
    KG = "kg", "Kilogram"
    G = "g", "Gram"
    L = "l", "Liter"
    ML = "ml", "Milliliter"
    BOX = "box", "Box"
    PACK = "pack", "Pack"
    SET = "set", "Set"


