from pyside_ui.transform_ui import TransformUI
from PySide6 import QtWidgets

def show_ui():
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, TransformUI):
            widget.close()
    ui = TransformUI()
    ui.show()

# Only run when executed directly inside Maya
if __name__ == "__main__":
    show_ui()
