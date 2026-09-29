from .base_dialog import BaseDetailDialog


class ShowDataDialog(BaseDetailDialog):
    """
    Read-only dialog for displaying any data with configurable field mappings.

    Args:
        data: The raw API payload (dict).
        fields_map: {label: key} mapping for top‑level fields.
        items_map: {label: key} mapping for nested line items (or None).
        title: Dialog window title.
        width: Dialog width in pixels.
    """

    def __init__(
        self,
        data: dict,
        fields_map: dict[str, str],
        items_map: dict[str, str] | None = None,
        title: str = "Details",
        width: int = 700,
    ):
        super().__init__(
            title=title,
            data=data,
            width=width,
            fields_map=fields_map,
            items_map=items_map,
        )