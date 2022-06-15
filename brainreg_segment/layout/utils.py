from qtpy.QtWidgets import QMessageBox


def display_warning(widget, title, message):
    """
    Display a warning in a pop up that informs
    about overwriting files
    """
    message_reply = QMessageBox.question(
        widget,
        title,
        message,
        QMessageBox.Yes | QMessageBox.Cancel,
    )
    if message_reply == QMessageBox.Yes:
        return True
    else:
        return False
