from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance
from maya import cmds
import maya.OpenMayaUI as omui

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

class TransformUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super().__init__(parent)
        self.setWindowTitle("Transform Tool - PySide6")
        self.setFixedSize(400, 250)
        self.build_ui()
        self.connect_signals()
        self.selection_job = cmds.scriptJob(event=["SelectionChanged", self.on_selection_changed], protected=True)

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.object_label = QtWidgets.QLabel("Object: [ No selection ]")
        layout.addWidget(self.object_label)

        self.translate_inputs = self.create_vector_input("Translate")
        layout.addLayout(self.translate_inputs['layout'])

        self.rotate_inputs = self.create_vector_input("Rotate")
        layout.addLayout(self.rotate_inputs['layout'])

        btn_row_1 = QtWidgets.QHBoxLayout()
        self.spawn_btn = QtWidgets.QPushButton("Spawn camera Object")
        self.reset_btn = QtWidgets.QPushButton("Reset")
        btn_row_1.addWidget(self.spawn_btn)
        btn_row_1.addWidget(self.reset_btn)
        layout.addLayout(btn_row_1)

        btn_row_2 = QtWidgets.QHBoxLayout()
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.apply_close_btn = QtWidgets.QPushButton("Apply & Close")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        btn_row_2.addWidget(self.apply_btn)
        btn_row_2.addWidget(self.apply_close_btn)
        btn_row_2.addWidget(self.cancel_btn)
        layout.addLayout(btn_row_2)

    def create_vector_input(self, label_text):
        layout = QtWidgets.QHBoxLayout()

        checkbox = QtWidgets.QCheckBox(label_text)
        checkbox.setFixedWidth(80)

        x_label = QtWidgets.QLabel("X:")
        x_input = QtWidgets.QLineEdit()
        y_label = QtWidgets.QLabel("Y:")
        y_input = QtWidgets.QLineEdit()
        z_label = QtWidgets.QLabel("Z:")
        z_input = QtWidgets.QLineEdit()

        for field in (x_input, y_input, z_input):
            field.setFixedWidth(50)

        layout.addWidget(checkbox)
        layout.addWidget(x_label)
        layout.addWidget(x_input)
        layout.addWidget(y_label)
        layout.addWidget(y_input)
        layout.addWidget(z_label)
        layout.addWidget(z_input)
        layout.addStretch()

        return {
            'checkbox': checkbox,
            'x': x_input,
            'y': y_input,
            'z': z_input,
            'layout': layout
        }

    def connect_signals(self):
        self.apply_btn.clicked.connect(self.apply)
        self.apply_close_btn.clicked.connect(self.apply_and_close)
        self.cancel_btn.clicked.connect(self.close)
        self.spawn_btn.clicked.connect(self.spawn_camera)
        self.reset_btn.clicked.connect(self.reset_fields)

        self.translate_inputs['checkbox'].stateChanged.connect(
            lambda: self.set_enabled_state(self.translate_inputs, self.translate_inputs['checkbox'].isChecked()))
        self.rotate_inputs['checkbox'].stateChanged.connect(
            lambda: self.set_enabled_state(self.rotate_inputs, self.rotate_inputs['checkbox'].isChecked()))

        self.update_selected_object()
        self.update_transform_fields()

    def set_enabled_state(self, input_group, enabled):
        input_group['x'].setEnabled(enabled)
        input_group['y'].setEnabled(enabled)
        input_group['z'].setEnabled(enabled)

    def on_selection_changed(self):
        self.update_selected_object()
        self.update_transform_fields()

    def update_selected_object(self):
        selection = cmds.ls(selection=True)
        if selection:
            self.object_label.setText(f"Object: {selection[0]}")
        else:
            self.object_label.setText("Object: [ No selection ]")

    def update_transform_fields(self):
        selection = cmds.ls(selection=True)
        if not selection:
            for group in [self.translate_inputs, self.rotate_inputs]:
                for key in ['x', 'y', 'z']:
                    group[key].setText("")
            return

        obj = selection[0]
        try:
            translate = cmds.getAttr(f"{obj}.translate")[0]
            rotate = cmds.getAttr(f"{obj}.rotate")[0]
        except Exception:
            translate = (0.0, 0.0, 0.0)
            rotate = (0.0, 0.0, 0.0)

        self.translate_inputs['x'].setText(str(translate[0]))
        self.translate_inputs['y'].setText(str(translate[1]))
        self.translate_inputs['z'].setText(str(translate[2]))

        self.rotate_inputs['x'].setText(str(rotate[0]))
        self.rotate_inputs['y'].setText(str(rotate[1]))
        self.rotate_inputs['z'].setText(str(rotate[2]))

    def reset_fields(self):
        for group in [self.translate_inputs, self.rotate_inputs]:
            for key in ['x', 'y', 'z']:
                group[key].setText("")
        self.translate_inputs['checkbox'].setChecked(False)
        self.rotate_inputs['checkbox'].setChecked(False)

    def apply(self):
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning("No object selected.")
            return
        obj = selection[0]

        if self.translate_inputs['checkbox'].isChecked():
            tx = self.get_value(self.translate_inputs['x'])
            ty = self.get_value(self.translate_inputs['y'])
            tz = self.get_value(self.translate_inputs['z'])
            cmds.setAttr(f"{obj}.translate", tx, ty, tz)

        if self.rotate_inputs['checkbox'].isChecked():
            rx = self.get_value(self.rotate_inputs['x'])
            ry = self.get_value(self.rotate_inputs['y'])
            rz = self.get_value(self.rotate_inputs['z'])
            cmds.setAttr(f"{obj}.rotate", rx, ry, rz)

        self.update_selected_object()
        self.update_transform_fields()

    def apply_and_close(self):
        self.apply()
        self.close()

    def get_value(self, field):
        try:
            return float(field.text())
        except ValueError:
            return 0.0

    def spawn_camera(self):
        cam = cmds.camera()[0]
        cmds.select(cam)
        self.update_selected_object()
        self.update_transform_fields()

    def closeEvent(self, event):
        if cmds.scriptJob(exists=self.selection_job):
            cmds.scriptJob(kill=self.selection_job, force=True)
        super().closeEvent(event)
