from functools import partial


class DialogHandler:
    """
    Generic handler for create dialogs.

    The dialog must implement:
        validate() -> list[str]
        get_data() -> dict
        save_btn (QPushButton)
    """

    def __init__(
        self,
        *,
        executor,
        overlay,
        message_manager,
    ):
        self.executor = executor
        self.overlay = overlay
        self.msg = message_manager

    def open(
        self,
        dialog,
        create_fn,
        entity_name: str,
    ):
        # Avoid stacking multiple handlers if the dialog is reused or
        # open() is invoked more than once (double error dialogs).
        try:
            dialog.save_btn.clicked.disconnect()
        except TypeError:
            pass
        dialog.save_btn.clicked.connect(
            partial(self._submit, dialog, create_fn, entity_name)
        )
        dialog.exec()

    def _submit(
        self,
        dialog,
        create_fn,
        entity_name,
    ):
        errors = dialog.validate()

        if errors:
            self.msg.error(
                "Invalid input",
                "\n".join(errors),
            )
            return

        data = dialog.get_data()

        self.overlay.show()

        self.executor.run(
            create_fn,
            data,
            on_result=lambda result: self._success(
                result,
                dialog,
                entity_name,
            ),
            on_error=lambda error: self._error(
                entity_name,
                error,
            ),
        )

    def _success(
        self,
        result,
        dialog,
        entity_name,
    ):
        self.overlay.hide()

        if result.ok:
            dialog.close()
            self.msg.success(
                "Success",
                f"{entity_name} created.",
            )
        else:
            self.msg.error(
                "Error",
                str(result.error),
            )

    def _error(
        self,
        entity_name,
        error,
    ):
        self.overlay.hide()
        self.msg.error(
            "Error",
            f"Failed to create {entity_name.lower()}: {error}",
        )