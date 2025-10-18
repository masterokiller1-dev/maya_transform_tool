from PySide6 import QtWidgets
from maya import cmds
from maya_transform_tool.pyside_ui.transform_ui import TransformUI


def show_ui():
    """Show the Transform Tool UI (purple) without affecting viewport color."""
    # Close any existing instance
    for widget in QtWidgets.QApplication.allWidgets():
        if isinstance(widget, TransformUI):
            widget.close()

    ui = TransformUI()
    ui.show()


def reset_viewport_background():
    """Reset the Maya viewport to its default gray gradient."""
    cmds.displayRGBColor('background', 0.63, 0.63, 0.63)
    cmds.displayRGBColor('backgroundTop', 0.63, 0.63, 0.63)
    cmds.displayRGBColor('backgroundBottom', 0.05, 0.05, 0.05)

    # Refresh all model panels
    for panel in cmds.getPanel(type='modelPanel'):
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded')


if __name__ == "__main__":
    reset_viewport_background()  # ensure Maya viewport resets when launching
    show_ui()
