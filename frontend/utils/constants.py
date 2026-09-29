# /frontend/utils/constants.py
from typing import Dict
from enum import Enum

from PyQt6.QtGui import QColor




# ـــــــــــــــــــــــــــــــ VARIABLES ـــــــــــــــــــــــــــــــــــــ
IMAGE_FILTER  = "Images (*.png *.jpg *.jpeg *.webp *.bmp)"
MAX_DIMENSION = 999_999.99


# ـــــــــــــــــــــــــــــــ CLASSES ـــــــــــــــــــــــــــــــــــــ
# ====================================================================================
# ENUMS
# ====================================================================================
class MessageType(Enum):
    """Message types with their respective icons and colors"""
    INFO = ("ℹ", "#3B82F6", "#EFF6FF", "#1E40AF")
    SUCCESS = ("✓", "#10B981", "#ECFDF5", "#065F46")
    WARNING = ("⚠", "#F59E0B", "#FFFBEB", "#92400E")
    ERROR = ("✕", "#EF4444", "#FEF2F2", "#991B1B")
    QUESTION = ("?", "#8B5CF6", "#F5F3FF", "#5B21B6")


# ====================================================================================
# COLORS CLASS
# ====================================================================================
class Color:

    # ====================================================================================
    # BLACK / DARK
    # ====================================================================================
    COLOR_BL01 = "#000000"
    COLOR_BL02 = "#0F1117"
    COLOR_BL03 = "#131722"
    COLOR_BL04 = "#161B29"
    COLOR_BL05 = "#181C27"
    COLOR_BL06 = "#1A2030"
    COLOR_BL07 = "#1E2235"
    COLOR_BL08 = "#20283B"
    COLOR_BL09 = "#232838"
    COLOR_BL10 = "#252B42"

    # ====================================================================================
    # BLUE
    # ====================================================================================
    COLOR_BU01 = "#4F8EF7"
    COLOR_BU02 = "#66A3FF"
    COLOR_BU03 = "#3B7AE6"
    COLOR_BU04 = "#2F5FAF"
    COLOR_BU05 = "#1F3D73"
    COLOR_BU06 = "#57B7FF"
    COLOR_BU07 = "#3FA9F5"
    COLOR_BU08 = "#1E90FF"
    COLOR_BU09 = "#0066CC"
    COLOR_BU10 = "#003F88"

    # ====================================================================================
    # CYAN
    # ====================================================================================
    COLOR_CY01 = "#38E2B8"
    COLOR_CY02 = "#4FF0C7"
    COLOR_CY03 = "#24C79F"
    COLOR_CY04 = "#1F7F69"
    COLOR_CY05 = "#0E5C4B"
    COLOR_CY06 = "#2DD4BF"
    COLOR_CY07 = "#14B8A6"
    COLOR_CY08 = "#0F766E"
    COLOR_CY09 = "#115E59"
    COLOR_CY10 = "#134E4A"

    # ====================================================================================
    # GREEN
    # ====================================================================================
    COLOR_GR01 = "#4FCF7A"
    COLOR_GR02 = "#22C55E"
    COLOR_GR03 = "#16A34A"
    COLOR_GR04 = "#15803D"
    COLOR_GR05 = "#166534"
    COLOR_GR06 = "#86EFAC"
    COLOR_GR07 = "#BBF7D0"
    COLOR_GR08 = "#14532D"
    COLOR_GR09 = "#65A30D"
    COLOR_GR10 = "#84CC16"

    # ====================================================================================
    # YELLOW
    # ====================================================================================
    COLOR_YE01 = "#F7B24F"
    COLOR_YE02 = "#F59E0B"
    COLOR_YE03 = "#D97706"
    COLOR_YE04 = "#B45309"
    COLOR_YE05 = "#92400E"
    COLOR_YE06 = "#FBBF24"
    COLOR_YE07 = "#FCD34D"
    COLOR_YE08 = "#FFDD57"
    COLOR_YE09 = "#FFE066"
    COLOR_YE10 = "#FFF3BF"

    # ====================================================================================
    # ORANGE
    # ====================================================================================
    COLOR_OR01 = "#F97316"
    COLOR_OR02 = "#EA580C"
    COLOR_OR03 = "#C2410C"
    COLOR_OR04 = "#FB923C"
    COLOR_OR05 = "#FDBA74"
    COLOR_OR06 = "#FF922B"
    COLOR_OR07 = "#FF7F11"
    COLOR_OR08 = "#FF6F00"
    COLOR_OR09 = "#E8590C"
    COLOR_OR10 = "#D9480F"

    # ====================================================================================
    # RED
    # ====================================================================================
    COLOR_RE01 = "#F75959"
    COLOR_RE02 = "#EF4444"
    COLOR_RE03 = "#DC2626"
    COLOR_RE04 = "#B91C1C"
    COLOR_RE05 = "#991B1B"
    COLOR_RE06 = "#FCA5A5"
    COLOR_RE07 = "#FECACA"
    COLOR_RE08 = "#7F1D1D"
    COLOR_RE09 = "#E11D48"
    COLOR_RE10 = "#BE123C"

    # ====================================================================================
    # PURPLE
    # ====================================================================================
    COLOR_PU01 = "#9B6BFF"
    COLOR_PU02 = "#8B5CF6"
    COLOR_PU03 = "#7C3AED"
    COLOR_PU04 = "#6D28D9"
    COLOR_PU05 = "#5B21B6"
    COLOR_PU06 = "#C084FC"
    COLOR_PU07 = "#E879F9"
    COLOR_PU08 = "#D946EF"
    COLOR_PU09 = "#C026D3"
    COLOR_PU10 = "#A21CAF"

    # ====================================================================================
    # GRAY
    # ====================================================================================
    COLOR_GY01 = "#FFFFFF"
    COLOR_GY02 = "#F8FAFC"
    COLOR_GY03 = "#F1F5F9"
    COLOR_GY04 = "#E2E8F0"
    COLOR_GY05 = "#CBD5E1"
    COLOR_GY06 = "#94A3B8"
    COLOR_GY07 = "#64748B"
    COLOR_GY08 = "#475569"
    COLOR_GY09 = "#334155"
    COLOR_GY10 = "#1E293B"

    # ====================================================================================
    # PINK
    # ====================================================================================
    COLOR_PI01 = "#FF6B9A"
    COLOR_PI02 = "#FF8FAB"
    COLOR_PI03 = "#FFB3C6"
    COLOR_PI04 = "#FFC2D1"
    COLOR_PI05 = "#FFE5EC"
    COLOR_PI06 = "#D63384"
    COLOR_PI07 = "#C2255C"
    COLOR_PI08 = "#A61E4D"
    COLOR_PI09 = "#FF4D6D"
    COLOR_PI10 = "#FF758F"

    # ====================================================================================
    # COLLECTION
    # ====================================================================================
    BACKGROUND        = "#0F1117"   # main background
    SURFACE           = "#181C27"   # cards / panels
    SURFACE2          = "#1E2235"   # raised elements
    BORDER            = "#2A2F45"   # subtle borders
    ACCENT            = "#4F8EF7"   # sky blue
    ACCENT1           = "#1565c0"   # primary blue
    ACCENT2           = "#38E2B8"   # teal highlight
    DANGER            = "#F75959"   # red / error
    WARNING           = "#F7B24F"   # amber / warning
    SUCCESS           = "#4FCF7A"   # green / success
    TEXT              = "#E8ECF4"   # primary text
    TEXT_DIM          = "#7A8099"   # muted text
    TEXT_BRIGHT       = "#FFFFFF"   # high emphasis
    TEXT_PRIMARY      = "#BCBCBC"   # Dark Gray
    TEXT_SECONDARY    = "#757575"   # Medium Gray
    PRIMARY           = "#1976d2"   # Blue
    PRIMARY_DARK      = "#1565c0"   # Dark Blue
    PRIMARY_LIGHT     = "#42a5f5"   # Light Blue    
    SECONDARY         = "#9c27b0"   # Purple
    SUCCESS_2         = "#4caf50"   # Green
    WARNING_2         = "#ff9800"   # Orange
    ERROR             = "#f44336"   # Red
    ERROR_BG          = "#ffebee"
    INFO              = "#00bcd4"   # Cyan    
    HOVER             = "#e3f2fd"   # Light Blue Hover
    ACTIVE            = "#bbdefb"   # Active state
    DISABLED          = "#e0e0e0"   # Disabled state
    MUTED             = "#9ca3af"   # Muted


# ====================================================================================
# FONT SIZE CLASS
# ====================================================================================
class FontSize:

    # ====================================================================================
    # FONT SIZE (FONT_SIZE_)
    # RANGE: 8 -> 32 STEP 2
    # ====================================================================================
    FONT_SIZE_8  = 8
    FONT_SIZE_10 = 10
    FONT_SIZE_12 = 12
    FONT_SIZE_14 = 14
    FONT_SIZE_16 = 16
    FONT_SIZE_18 = 18
    FONT_SIZE_20 = 20
    FONT_SIZE_22 = 22
    FONT_SIZE_24 = 24
    FONT_SIZE_26 = 26
    FONT_SIZE_28 = 28
    FONT_SIZE_30 = 30
    FONT_SIZE_32 = 32
    FONT_SIZE_34 = 34
    FONT_SIZE_36 = 36
    FONT_SIZE_38 = 38
    FONT_SIZE_40 = 40
    FONT_SIZE_46 = 46
    FONT_SIZE_52 = 52


# ====================================================================================
# HEIGHT CLASS
# ====================================================================================
class RowHeight:

    # ====================================================================================
    # ROW HEIGHT (ROW_HEIGHT_)
    # RANGE: 30 -> 100 STEP 5,15, 25
    # ====================================================================================
    ROW_HEIGHT_30  = 30
    ROW_HEIGHT_35  = 35
    ROW_HEIGHT_40  = 40
    ROW_HEIGHT_45  = 45
    ROW_HEIGHT_50  = 50
    ROW_HEIGHT_55  = 55
    ROW_HEIGHT_60  = 60
    ROW_HEIGHT_75  = 75
    ROW_HEIGHT_100 = 100


# ====================================================================================
# BOUND_ CLASS
# ====================================================================================
class Bound:
    
    # ====================================================================================
    # BOUND_S / SIZES
    # RANGE: 100 -> 5000 STEP 100,1000
    # ====================================================================================
    BOUND_100  = 100
    BOUND_200  = 200
    BOUND_300  = 300
    BOUND_400  = 400
    BOUND_500  = 500
    BOUND_600  = 600
    BOUND_700  = 700
    BOUND_800  = 800
    BOUND_900  = 900
    BOUND_1000 = 1000
    BOUND_2000 = 2000
    BOUND_3000 = 3000
    BOUND_4000 = 4000
    BOUND_5000 = 5000


# ====================================================================================
# TIMEOUT CLASS
# ====================================================================================
class TimeOut:

    # ====================================================================================
    # TIMEOUT / MS / S / M / H / D
    # ====================================================================================
    # ـــ MS ـــــــــــــــــــ
    TIMEOUT_3000 = 3000
    TIMEOUT_4000 = 4000
    TIMEOUT_5000 = 5000
    TIMEOUT_6000 = 6000
    TIMEOUT_7000 = 7000


# ====================================================================================
# FONT FAMILY CLASS
# ====================================================================================
class FontFamily:

    # ====================================================================================
    # SYSTEM / DEFAULT
    # ====================================================================================
    INTER            = "Inter, sans-serif"
    ROBOTO           = "Roboto, sans-serif"
    OPEN_SANS        = "Open Sans, sans-serif"

    # ====================================================================================
    # UI / MODERN ERP FONTS
    # ====================================================================================
    POPPINS          = "Poppins, sans-serif"
    MONTSERRAT       = "Montserrat, sans-serif"
    LATO             = "Lato, sans-serif"
    SEGOE            = "Segoe UI"

    # ====================================================================================
    # MONOSPACE / CODE / SYSTEM DATA
    # ====================================================================================
    FIRA_CODE        = "Fira Code, monospace"
    SOURCE_CODE_PRO  = "Source Code Pro, monospace"

    # ====================================================================================
    # DISPLAY / HEADINGS
    # ====================================================================================
    PLAYFAIR_DISPLAY = "Playfair Display, serif"
    MERRIWEATHER     = "Merriweather, serif"


# ====================================================================================
# ICONS
# ====================================================================================
class Icon:
    ARROW_DOWN_0_1 = "frontend/resources/icons/arrow-down-0-1.svg"
    ARROW_DOWN_1_0 = "frontend/resources/icons/arrow-down-1-0.svg"
    ARROW_DOWN_A_Z = "frontend/resources/icons/arrow-down-a-z.svg"
    ARROW_UP_0_1 = "frontend/resources/icons/arrow-up-0-1.svg"
    ARROW_UP_1_0 = "frontend/resources/icons/arrow-up-1-0.svg"
    ARROW_UP_A_Z = "frontend/resources/icons/arrow-up-a-z.svg"
    BADGE_DOLLAR_SIGN = "frontend/resources/icons/badge-dollar-sign.svg"
    BANKNOTE_ARROW_DOWN = "frontend/resources/icons/banknote-arrow-down.svg"
    BANKNOTE_ARROW_UP = "frontend/resources/icons/banknote-arrow-up.svg"
    BOXES = "frontend/resources/icons/boxes.svg"
    CHART_BAR = "frontend/resources/icons/chart-bar.svg"
    CHART_NO_AXES_COMBINED = "frontend/resources/icons/chart-no-axes-combined.svg"
    CHEVRON_LEFT = "frontend/resources/icons/chevron-left.svg"
    CHEVRON_RIGHT = "frontend/resources/icons/chevron-right.svg"
    CHEVRONS_LEFT = "frontend/resources/icons/chevrons-left.svg"
    CHEVRONS_RIGHT = "frontend/resources/icons/chevrons-right.svg"
    CIRCLE_X = "frontend/resources/icons/circle-x.svg"
    COG = "frontend/resources/icons/cog.svg"
    FILE_PEN_LINE = "frontend/resources/icons/file-pen-line.svg"
    FILE_PLUS_CORNER = "frontend/resources/icons/file-plus-corner.svg"
    FILE_PLUS = "frontend/resources/icons/file-plus.svg"
    LAYOUT_DASHBOARD = "frontend/resources/icons/layout-dashboard.svg"
    LOG_OUT = "frontend/resources/icons/log-out.svg"
    PACKAGE = "frontend/resources/icons/package.svg"
    REFRESH_CCW_DOT = "frontend/resources/icons/refresh-ccw-dot.svg"
    REFRESH_CCW = "frontend/resources/icons/refresh-ccw.svg"
    ROTATE_CW = "frontend/resources/icons/rotate-cw.svg"
    SEND = "frontend/resources/icons/send.svg"
    SETTINGS = "frontend/resources/icons/settings.svg"
    SHOPPING_BAG = "frontend/resources/icons/shopping-bag.svg"
    SHOPPING_CART = "frontend/resources/icons/shopping-cart.svg"
    TRASH_2 = "frontend/resources/icons/trash-2.svg"
    USERS = "frontend/resources/icons/users.svg"
    PANEL = "frontend/resources/icons/control-panel.svg"


# ====================================================================================
# IMAGES
# ====================================================================================
class Image:
    BRAND   = "frontend/resources/images/storica_word.png"
    MAIN    = "frontend/resources/images/storica_main.png"
    EFFECTS = "frontend/resources/images/storica_effects.png"


# ====================================================================================
# APPS
# ====================================================================================
class AppNames:
    ORDERS            = "Orders"
    SALES_ORDER       = "Sales_Order"
    PURCHASES_ORDER   = "Purchases_Order"
    PURCHASES         = "Purchases"
    SALES             = "Sales"
    INVENTORY         = "Inventory"
    DEALERS           = "Dealers"
    PANEL             = "Panel"
    INVOICES          = "Invoices"
    SALES_INVOICE     = "Sales_Invoice"
    PURCHASES_INVOICE = "Purchases_Invoice"
    SUPPLIER          = "Supplier"
    CUSTOMER          = "Customer"
    DASHBOARD         = "Dashboard"
    LOGIN             = "Login"
    LOG_IN            = "Log In"
    LOGOUT            = "Logout"
    LOG_OUT           = "Log Out"


# ====================================================================================
# STATUS MESSAGE
# ====================================================================================
class StatusMessage:
    SUCCESS  = "success"
    ERROR    = "error"
    INFO     = "info"


# ـــــــــــــــــــــــــ LISTS / DICTIONARIES ـــــــــــــــــــــــــ

# ====================================================================================
# Colour constants – defined once, not rebuilt per cell
# ====================================================================================
PAYMENT_COLOURS: Dict[str, Dict[str, QColor]] = {
    "paid":    {"fg": QColor(0, 150, 0),   "bg": QColor(220, 255, 220)},
    "partial": {"fg": QColor(200, 100, 0), "bg": QColor(255, 255, 200)},
    "unpaid":  {"fg": QColor(200, 0, 0),   "bg": QColor(255, 220, 220)},
}

STATUS_COLOURS: Dict[str, QColor] = {
    # ─── Draft / Pending ───
    "draft":     QColor(200, 200, 0),      # Yellow
    "pending":   QColor(200, 200, 0),      # Yellow
    
    # ─── Processing / In Progress ───
    "processing": QColor(255, 165, 0),     # Orange
    "sent":       QColor(255, 165, 0),     # Orange
    "shipped":    QColor(255, 165, 0),     # Orange
    
    # ─── Active / Confirmed ───
    "active":     QColor(0, 200, 0),       # Green
    "confirmed":  QColor(0, 200, 0),       # Green
    "completed":  QColor(0, 200, 0),       # Green
    "paid":       QColor(0, 200, 0),       # Green
    "delivered":  QColor(0, 200, 0),       # Green
    
    # ─── Partial / Mixed ───
    "partial":    QColor(255, 200, 0),     # Amber/Gold
    "partial_paid": QColor(255, 200, 0),   # Amber/Gold
    
    # ─── Warning / Attention ───
    "posted":     QColor(0, 120, 0),       # Dark Green
    "overdue":    QColor(255, 100, 0),     # Dark Orange
    "expired":    QColor(255, 100, 0),     # Dark Orange
    "recalled":   QColor(255, 100, 0),     # Dark Orange
    "maintenance": QColor(255, 165, 0),    # Orange
    "sold_out":   QColor(200, 100, 0),     # Brown/Orange
    
    # ─── Cancelled / Failed ───
    "cancelled":  QColor(180, 0, 0),       # Dark Red
    "failed":     QColor(180, 0, 0),       # Dark Red
    "returned":   QColor(200, 100, 0),     # Brown/Orange
    "refunded":   QColor(200, 100, 0),     # Brown/Orange
    
    # ─── Inactive ───
    "inactive":   QColor(150, 150, 150),   # Gray
}

BOOLEAN_COLOURS: Dict[str, QColor] = {
    "True":     QColor(20, 220, 00),
    "False":    QColor(220, 20, 20),
}

# Row highlight when is_low_stock is true (stock status table)
LOW_STOCK_COLOURS: Dict[str, QColor] = {
    "fg": QColor(185, 28, 28),       # red-700 text
    "bg": QColor(254, 226, 226),     # red-100 background
}

STATUS_TOOLTIPS: Dict[str, str] = {
    "draft":     "Draft – not yet finalised",
    "posted":    "Posted – finalised transaction",
    "cancelled": "Cancelled – transaction voided",
    "returned":  "Returned – items returned",
}

NUMERIC_FIELDS = frozenset({
    "total", "paid_amount", "due_amount",
    "price", "amount", "quantity", "stock",
    "min_stock", "batch_count", "cost_value",
})

COLORS_STYLE = {
    "primary": {
        "bg": "#3B82F6",
        "hover": "#2563EB",
        "pressed": "#1D4ED8",
        "text": "#FFFFFF"
    },
    "secondary": {
        "bg": "#F1F5F9",
        "hover": "#E2E8F0",
        "pressed": "#CBD5E1",
        "text": "#334155"
    },
    "success": {
        "bg": "#10B981",
        "hover": "#059669",
        "pressed": "#047857",
        "text": "#FFFFFF"
    },
    "danger": {
        "bg": "#EF4444",
        "hover": "#DC2626",
        "pressed": "#B91C1C",
        "text": "#FFFFFF"
    }
}
# ====================================================================================
# STATUS / CHOICES
# ====================================================================================

# ــــــــــــــــــ ORDER STATUS ــــــــــــــــــ
ORDER_STATUS = [
    ("draft", "Draft"),
    ("confirmed", "Confirmed"),
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("delivered", "Delivered"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ("returned", "Returned"),
]

# ــــــــــــــــــ INVOICE STATUS ــــــــــــــــــ
INVOICE_STATUS = [
    ("draft", "Draft"),
    ("sent", "Sent"),
    ("paid", "Paid"),
    ("partial", "Partially Paid"),
    ("overdue", "Overdue"),
    ("cancelled", "Cancelled"),
    ("refunded", "Refunded"),
]

# ــــــــــــــــــ PAYMENT STATUS ــــــــــــــــــ
PAYMENT_STATUS = [
    ("pending", "Pending"),
    ("partial", "Partial"),
    ("completed", "Completed"),
    ("failed", "Failed"),
    ("refunded", "Refunded"),
]

# ــــــــــــــــــ WAREHOUSE STATUS ــــــــــــــــــ
WAREHOUSE_STATUS = [
    ("active", "Active"),
    ("inactive", "Inactive"),
    ("maintenance", "Under Maintenance"),
]

# ــــــــــــــــــ BATCH STATUS ــــــــــــــــــ
BATCH_STATUS = [
    ("active", "Active"),
    ("expired", "Expired"),
    ("recalled", "Recalled"),
    ("sold_out", "Sold Out"),
]

# ــــــــــــــــــ STOCK MOVEMENT STATUS ــــــــــــــــــ
STOCK_MOVEMENT_TYPES = [
    ("in", "Stock In"),
    ("out", "Stock Out"),
    ("transfer", "Transfer"),
    ("adjustment", "Adjustment"),
    ("return", "Return"),
]

# ــــــــــــــــــ MOVEMENT STATUS ــــــــــــــــــ
MOVEMENT_STATUS = [
    ("pending", "Pending"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

# ــــــــــــــــــ UNIT CHOICES ــــــــــــــــــ
UNIT_CHOICES = [
    ("pcs", "Pieces"),
    ("kg", "Kilogram"),
    ("g", "Gram"),
    ("l", "Liter"),
    ("ml", "Milliliter"),
    ("box", "Box"),
    ("pack", "Pack"),
    ("set", "Set"),
]


# ====================================================================================
# TABLES HEADERS / COLUMNS
# ====================================================================================

# ــــــــــــــــــ CATEGORY ــــــــــــــــــ
CATEGORIES_COLUMN_MAP = {
    "ID"         : "id",
    "Code"       : "code",
    "Name"       : "name",
    "Slug"       : "slug",
    "Parent"     : "parent_name",
    "Active"     : "is_active",
    "Created At" : "created_at",
}

# ــــــــــــــــــ PRODUCT ــــــــــــــــــ
PRODUCTS_COLUMN_MAP = {
    "ID"         : "id",
    "SKU"        : "sku",
    "Slug"       : "slug",
    "Name"       : "name",
    "Category"   : "category_name",
    "Unit"       : "unit",
    "Active"     : "is_active",
    "Created At" : "created_at",
}

# ــــــــــــــــــ STOCK MOVEMENT ــــــــــــــــــ
STOCK_MOVEMENTS_COLUMN_MAP = {
    "ID": "id",
    "Movement ID": "movement_id",
    "Type": "movement_type",
    "Status": "status",
    "Product": "product_name",
    "Batch": "batch_code",
    "From WH": "from_warehouse_name",
    "To WH": "to_warehouse_name",
    "Quantity": "quantity",
    "Unit Price": "unit_price",
    "Reference": "reference_number",
    "Date": "movement_date",
    "Created": "created_at",
}

# ــــــــــــــــــ STOCK STATUS ــــــــــــــــــ
STOCK_STATUS_COLUMN_MAP = {
    "Variant SKU": "variant_sku",
    "Variant": "variant_name",
    "Product": "product_name",
    "Product SKU": "product_sku",
    "Category": "category_name",
    "Warehouse": "warehouse_name",
    "WH Code": "warehouse_code",
    "Quantity": "quantity",
    "Min Stock": "min_stock",
    "Low Stock": "is_low_stock",
    "Batches": "batch_count",
    "Earliest Expiry": "earliest_expiry",
    "Cost Value": "cost_value",
}

# ــــــــــــــــــ VARIANT ــــــــــــــــــ
VARIANTS_COLUMN_MAP = {
    "ID"         : "id",
    "SKU"        : "sku",
    "Product"    : "product_name",
    "Name"       : "name",
    "Color"      : "color",
    "Quantity"   : "quantity",
    "Min Stock"  : "min_stock",
    "Active"     : "is_active",
    "Created At" : "created_at",
}

# ــــــــــــــــــ WAREHOUSE ــــــــــــــــــ
WAREHOUSES_COLUMN_MAP = {
    "ID"         : "id",
    "Code"       : "code",
    "Name"       : "name",
    "Slug"       : "slug",
    "Location"   : "location",
    "Phone"      : "phone",
    "Status"     : "status",
    "Active"     : "is_active",
    "Created At" : "created_at",
}

# ــــــــــــــــــ BATCH ــــــــــــــــــ
BATCHES_COLUMN_MAP = {
    "ID": "id",
    "Code": "code",
    "Slug": "slug",
    "Variant": "variant_name",
    "Variant SKU": "variant_sku",
    "Warehouse": "warehouse_name",
    "Quantity": "quantity",
    "Cost Price": "cost_price",
    "Production Date": "production_date",
    "Expiry Date": "expiry_date",
    "Status": "status",
    "Active": "is_active",
    "Created": "created_at",
}

# ----------------------------- PURCHASES ------------------------------
# ــــــــــــــــــ PURCHASE ORDER ــــــــــــــــــ
PURCHASES_ORDERS_COLUMN_MAP = {
    "ID": "id",
    "Code": "code",
    "Supplier": "supplier_name",
    "Order Date": "order_date",
    "Status": "status",
    "Active": "is_active",
    "Created At": "created_at",
}

# ــــــــــــــــــ PURCHASE INVOICE ــــــــــــــــــ
PURCHASES_INVOICES_COLUMN_MAP = {
    "ID": "id",
    "Code": "code",
    "Supplier": "supplier_name",
    "Order": "order",
    "Invoice Date": "invoice_date",
    "Status": "status",
    "Total Amount": "total_amount",
    "Amount Paid": "amount_paid",
    "Active": "is_active",
    "Created At": "created_at",
}

# ــــــــــــــــــ PURCHASE PAYMENT ــــــــــــــــــ
PURCHASES_PAYMENTS_COLUMN_MAP = {
    "ID": "id",
    "Payment ID": "payment_id",
    "Transaction ID": "transaction_id",
    "Invoice ID": "invoice",
    "Invoice Code": "invoice_code",
    "Supplier ID": "supplier",
    "Supplier Name": "supplier_name",
    "Amount": "amount",
    "Payment Date": "payment_date",
    "Status": "status",
    "Created At": "created_at",
}

# ــــــــــــــــــ SUPPLIER ــــــــــــــــــ
SUPPLIERS_COLUMN_MAP = {
    "ID": "id",
    "Code": "code",
    "Slug": "slug",
    "Name": "name",
    "Email": "email",
    "Phone": "phone",
    "Verified": "is_verified",
    "Active": "is_active",
    "Created At": "created_at",
 }

# ــــــــــــــــــ  ــــــــــــــــــ

# ــــــــــــــــــ  ــــــــــــــــــ

# ــــــــــــــــــ  ــــــــــــــــــ

# ــــــــــــــــــ PURCHASE ORDER DETAILS ــــــــــــــــــ
PURCHASE_ORDER_DETAIL_FIELDS = {
    "Code":       "code",
    "Supplier":   "supplier_name",
    "Order Date": "order_date",
    "Status":     "status",
    "Notes":      "notes",
    "Active":     "is_active",
    "Created By": "created_by_name",
    "Updated By": "updated_by_name",
    "Created At": "created_at",
    "Updated At": "updated_at",
}

PURCHASE_ORDER_ITEMS_COLUMN_MAP = {
    "Variant":  "variant_name",
    "Quantity": "quantity",
}

# ــــــــــــــــــ PURCHASE INVOICE DETAILS ــــــــــــــــــ
PURCHASE_INVOICE_DETAIL_FIELDS = {
    "Code":          "code",
    "Supplier":      "supplier_name",
    "Warehouse":     "warehouse_name",
    "Order":         "order_code",
    "Invoice Date":  "invoice_date",
    "Paid Date":     "paid_date",
    "Status":        "status",
    "Discount Rate": "discount_rate",
    "Tax Rate":      "tax_rate",
    "Total Amount":  "total_amount",
    "Amount Paid":   "amount_paid",
    "Notes":         "notes",
    "Active":        "is_active",
    "Created By":    "created_by_name",
    "Updated By":    "updated_by_name",
    "Created At":    "created_at",
    "Updated At":    "updated_at",
}

PURCHASE_INVOICE_ITEMS_COLUMN_MAP = {
    "Variant":          "variant_name",
    "Quantity":         "quantity",
    "Cost Price":       "cost_price",
    "Discount Rate":    "discount_rate",
    "Tax Rate":         "tax_rate",
    "Production Date":  "production_date",
    "Expiry Date":      "expiry_date",
    "Notes":            "notes",
}

# ــــــــــــــــــ PURCHASE PAYMENT DETAILS ــــــــــــــــــ
PURCHASE_PAYMENT_DETAIL_COLUMN_MAP = {
    "ID": "id",
    "Payment ID": "payment_id",
    "Transaction ID": "transaction_id",
    "Invoice": "invoice",
    "Invoice Code": "invoice_code",
    "Order": "order",
    "Supplier": "supplier",
    "Supplier Name": "supplier_name",
    "Amount": "amount",
    "Payment Date": "payment_date",
    "Status": "status",
    "Reference Number": "reference_number",
    "Notes": "notes",
    "Processed By": "processed_by",
    "Processed By Name": "processed_by_name",
    "Created At": "created_at",
}
# ----------------------------- SALES ------------------------------
# ــــــــــــــــــ SALE ORDER ــــــــــــــــــ
SALES_ORDERS_COLUMN_MAP = {
    "ID": "id",
    "Code": "code",
    "Customer ID": "customer",
    "Customer Name": "customer_name",
    "Order Date": "order_date",
    "Status": "status",
    "Active": "is_active",
    "Created At": "created_at",
}

# ــــــــــــــــــ SALE INVOICE ــــــــــــــــــ
SALES_INVOICES_COLUMN_MAP = {
    "ID": "id",
    "Code": "code",
    "Customer ID": "customer",
    "Customer Name": "customer_name",
    "Order ID": "order",
    "Invoice Date": "invoice_date",
    "Status": "status",
    "Total Amount": "total_amount",
    "Amount Paid": "amount_paid",
    "Active": "is_active",
    "Created At": "created_at",
}

# ــــــــــــــــــ SALE PAYMENT ــــــــــــــــــ
SALES_PAYMENTS_COLUMN_MAP = {
    "ID": "id",
    "Payment ID": "payment_id",
    "Transaction ID": "transaction_id",
    "Invoice ID": "invoice",
    "Invoice Code": "invoice_code",
    "Customer ID": "customer",
    "Customer Name": "customer_name",
    "Amount": "amount",
    "Payment Date": "payment_date",
    "Status": "status",
    "Created At": "created_at",
}

# ــــــــــــــــــ CUSTOMER ــــــــــــــــــ
CUSTOMERS_COLUMN_MAP = {
    "ID": "id",
    "Code": "code",
    "Slug": "slug",
    "Name": "name",
    "Email": "email",
    "Phone": "phone",
    "Verified": "is_verified",
    "Active": "is_active",
    "Created At": "created_at",
}

# ====================================================================================
# NAVBAR COMPONENTS
# ====================================================================================

# ----------------------------- INVENTORY ------------------------------
# ــــــــــــــــــ CATEGORY ــــــــــــــــــ
CATEGORIES_NAVBAR_COMPONENTS = [
    'button_1', 
    'search', 
    'choice', 
    'active', 
    'refresh_btn'
]

# ــــــــــــــــــ PRODUCT ــــــــــــــــــ
PRODUCTS_NAVBAR_COMPONENTS = [
    'button_1', 
    'search', 
    'status', 
    'choice', 
    'active', 
    'refresh_btn'
]

# ــــــــــــــــــ STOCK MOVEMENT ــــــــــــــــــ
# Complete only — movements are created by sales/purchases flows
STOCK_MOVEMENTS_NAVBAR_COMPONENTS = [
    'button_2',
    'search',
    'status',
    'choice',
    'from_label',
    'date_from',
    'to_label',
    'date_to',
    'refresh_btn',
]

# ــــــــــــــــــ STOCK MOVEMENT ــــــــــــــــــ
STOCK_STATUS_NAVBAR_COMPONENTS = [
    'search',
    'status',
    'choice',
    'flag',
    'refresh_btn',
]

# ــــــــــــــــــ VARIANT ــــــــــــــــــ
VARIANTS_NAVBAR_COMPONENTS = [
    'button_1', 
    'search', 
    'choice', 
    'active', 
    'refresh_btn'
]

# ــــــــــــــــــ WAREHOUSE ــــــــــــــــــ
WAREHOUSES_NAVBAR_COMPONENTS = [
    'button_1', 
    'status', 
    'search', 
    'active', 
    'refresh_btn'
]

# ــــــــــــــــــ BATCH ــــــــــــــــــ
BATCHES_NAVBAR_COMPONENTS = [
    'search',
    'status',
    'choice',
    'from_label',
    'date_from',
    'to_label',
    'date_to',
    'active',
    'refresh_btn',
]

# ----------------------------- PURCHASES ------------------------------
# ــــــــــــــــــ PURCHASE ORDER ــــــــــــــــــ
# button_1: add order, button_2: add invoice,
# button_3: confirm, button_4: cancel
PURCHASES_ORDERS_NAVBAR_COMPONENTS = [
    'button_1',
    'button_2',
    'button_3',
    'button_4',
    'search',
    'status',
    'active',
    'refresh_btn',
]

# ــــــــــــــــــ PURCHASE INVOICE ــــــــــــــــــ
# button_1: add payment, button_2: cancel
# (no Post — stock received on create)
PURCHASES_INVOICES_NAVBAR_COMPONENTS = [
    'button_1',
    'button_2',
    'search',
    'status',
    'active',
    'refresh_btn',
]

# ــــــــــــــــــ SALES PAYMENT ــــــــــــــــــ
# button_1: refund selected payment
SALES_PAYMENTS_NAVBAR_COMPONENTS = [
    'button_1',
    'search',
    'status',
    'refresh_btn',
]

# ــــــــــــــــــ PURCHASE PAYMENT ــــــــــــــــــ
# (no action buttons — payments recorded from invoices)
PURCHASES_PAYMENTS_NAVBAR_COMPONENTS = [
    'search',
    'status',
    'refresh_btn',
]


# ــــــــــــــــــ SUPPLIER ــــــــــــــــــ
# button_1 add, button_2 edit, button_3 delete; flag=verified, active
SUPPLIERS_NAVBAR_COMPONENTS = [
    'button_1',
    'button_2',
    'button_3',
    'search',
    'flag',
    'active',
    'refresh_btn',
]

# ــــــــــــــــــ  ــــــــــــــــــ

# ــــــــــــــــــ  ــــــــــــــــــ

# ----------------------------- SALES ------------------------------
# ــــــــــــــــــ SALE ORDER ــــــــــــــــــ
# button_1: add order, button_2: add invoice,
# button_3: confirm, button_4: cancel
SALES_ORDERS_NAVBAR_COMPONENTS = [
    'button_1',
    'button_2',
    'button_3',
    'button_4',
    'search',
    'status',
    'active',
    'refresh_btn',
]

# ــــــــــــــــــ SALE INVOICE ــــــــــــــــــ
# button_1: add payment, button_2: post, button_3: cancel
SALES_INVOICES_NAVBAR_COMPONENTS = [
    'button_1',
    'button_2',
    'button_3',
    'search',
    'status',
    'choice',
    'active',
    'refresh_btn',
]

# ــــــــــــــــــ CUSTOMER ــــــــــــــــــ
# button_1 add, button_2 edit, button_3 delete; flag=verified, active
CUSTOMERS_NAVBAR_COMPONENTS = [
    'button_1',
    'button_2',
    'button_3',
    'button_4',
    'search',
    'flag',
    'active',
    'refresh_btn',
]

# ــــــــــــــــــ  ــــــــــــــــــ


# ــــــــــــــــــ  ــــــــــــــــــ



# ====================================================================================
# 
# ====================================================================================




# ----------------------------- USERS ------------------------------
USERS_COLUMN_MAP = {
    "ID": "id",
    "Username": "username",
    "Full Name": "full_name",
    "Email": "email",
    "Role": "role",
    "Active": "is_active",
    "Staff": "is_staff",
    "Last Login": "last_login",
    "Created At": "created_at",
}

USERS_NAVBAR_COMPONENTS = [
    "button_1",
    "button_2",
    "button_3",
    "button_4",
    "search",
    "choice",
    "active",
    "refresh_btn",
]
