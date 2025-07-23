from PyQt5.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressDialog,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox, QSpinBox, QDoubleSpinBox,
    QAbstractSpinBox, QLabel, QCheckBox, QLineEdit, QPushButton, QStackedWidget,
    QScrollArea
)
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QDoubleSpinBox, QAbstractSpinBox, QGridLayout, QSizePolicy
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class ParameterDialog(QDialog):
    """
    Dialog to configure fire-management plugin parameters across three tabs:
      1. General  (input/output folder, mode, x0, y0)
      2. Parameters (processing toggles)
      3. Constants  (numeric and variable settings)

    Instructions:
      - Navigate each tab to update values.
      - Hover over fields for guidance.
      - Click 'OK' to apply or 'Cancel' to discard.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interface Parameters")
        self.setMinimumWidth(550)
        self.setWindowIcon(QIcon(':/icons/fire.png'))

        # Global stylesheet: elegant, minimal theme
        self.setStyleSheet("""
            QDialog { background-color: #FAFAFA; color: #2E2E2E; }
            QLabel, QCheckBox, QTabBar, QPushButton { font-family: 'Segoe UI', sans-serif; }
            QTabWidget::pane { border: 1px solid #D0D0D0; border-radius: 4px; margin-top: 2px; }
            QTabBar::tab { background: #EAEAEA; padding: 8px 16px; margin: 2px; border-radius: 4px; }
            QTabBar::tab:selected { background: #FFFFFF; border: 1px solid #A0A0A0; border-bottom: none; }
            QPushButton { background-color: #4A90E2; color: #FFFFFF; padding: 6px 12px; border-radius: 4px; }
            QPushButton:hover { background-color: #357ABD; }
            QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox { background-color: #FFFFFF; padding: 4px; border: 1px solid #B0B0B0; border-radius: 3px; }
        """ )

        # Introduction label
        intro = QLabel(
            "Set the parameters below to configure the interface.\n"
            "These values are used to create direct and indirect interfaces, "
            "in order to assess the exposure of flammable areas to nearby urban zones.",
            parent=self
        )
        intro.setWordWrap(True)
        intro.setFont(QFont('Segoe UI', 10, QFont.Bold))

        # Tabs
        self.tabs = QTabWidget(self)
        self._create_tab1()
        self._create_tab2()


        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(intro)
        layout.addWidget(self.tabs)
        layout.addWidget(buttons)


    def _create_tab1(self):
        page = QWidget()
        grid = QGridLayout(page)

        # ────────────────────────────────
        # 📂 Input Folder
        # ────────────────────────────────
        grid.addWidget(QLabel("📂 Input Folder:"), 0, 0)
        self.inputFolderEdit = QLineEdit()
        self.inputFolderEdit.setToolTip("Directory containing input data.")
        self.inputFolderEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        browseInput = QPushButton("Browse...")
        browseInput.setIcon(QIcon(':/icons/folder.png'))
        browseInput.setToolTip("Select input folder")
        browseInput.clicked.connect(self._browse_input)

        grid.addWidget(self.inputFolderEdit, 0, 1)
        grid.addWidget(browseInput, 0, 2)

        # ────────────────────────────────
        # 📁 Output Folder
        # ────────────────────────────────
        grid.addWidget(QLabel("📁 Output Folder:"), 1, 0)
        self.outputFolderEdit = QLineEdit()
        self.outputFolderEdit.setToolTip("Directory for saving results.")
        self.outputFolderEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        browseOutput = QPushButton("Browse...")
        browseOutput.setIcon(QIcon(':/icons/folder.png'))
        browseOutput.setToolTip("Select output folder")
        browseOutput.clicked.connect(self._browse_output)

        grid.addWidget(self.outputFolderEdit, 1, 1)
        grid.addWidget(browseOutput, 1, 2)

        # ────────────────────────────────
        # ⚙️ Processing Mode
        # ────────────────────────────────
        grid.addWidget(QLabel("⚙️ Processing Mode:"), 2, 0)
        self.optionCombo = QComboBox()
        self.optionCombo.addItems(["altorisco", "todos"])
        self.optionCombo.setToolTip("Select the type of processing to apply.")
        self.optionCombo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(self.optionCombo, 2, 1, 1, 2)

        # ────────────────────────────────
        # 📍 Coordinates
        # ────────────────────────────────
        grid.addWidget(QLabel("📍 X Coordinate (x0):"), 3, 0)
        self.x0DoubleSpin = QDoubleSpinBox()
        self.x0DoubleSpin.setRange(-1e9, 1e9)
        self.x0DoubleSpin.setValue(-98407.00)
        self.x0DoubleSpin.setToolTip("X-origin coordinate")
        self.x0DoubleSpin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        grid.addWidget(self.x0DoubleSpin, 3, 1, 1, 2)

        grid.addWidget(QLabel("📍 Y Coordinate (y0):"), 4, 0)
        self.y0DoubleSpin = QDoubleSpinBox()
        self.y0DoubleSpin.setRange(-1e9, 1e9)
        self.y0DoubleSpin.setValue(-102297.80)
        self.y0DoubleSpin.setToolTip("Y-origin coordinate")
        self.y0DoubleSpin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        grid.addWidget(self.y0DoubleSpin, 4, 1, 1, 2)

        # 🖱️ Pick Point
        self.pickPointBtn = QPushButton("🖱️ Pick Point")
        self.pickPointBtn.setToolTip("Click on the map canvas to choose x0/y0 coordinates.")
        self.pickPointBtn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid.addWidget(self.pickPointBtn, 5, 0, 1, 3, alignment=Qt.AlignCenter)

        page.setLayout(grid)
        self.tabs.addTab(page, "General")

    def _create_tab2(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        self.sub_tab_stack = QStackedWidget(page)

        # -------- Sub-tab 1: Numeric Constants (Scrollable) --------
        numeric_scroll_area = QScrollArea(page)
        numeric_scroll_area.setWidgetResizable(True)
        numeric_container = QWidget()
        numeric_layout = QVBoxLayout(numeric_container)

        numeric_group = QGroupBox("Numeric Constants", numeric_container)
        numeric_form_layout = QFormLayout(numeric_group)

        constants = [
            ("KDTREE_DIST_UPPERBOUND", 0, 1_000_000, 500, "Maximum distance allowed in KDTree nearest neighbor search"),
            ("d_box", 0, 100_000, 500, "Box radius around central point to filter data and generate plots"),
            ("K", 1, 1000, 3, "Number of flammable neighbors to explore from each urban point"),
            ("KF", 1, 1000, 5, "Number of urban neighbors to explore from each selected flammable point"),
            ("limiar", 0, 100, 1.05, "Threshold to validate triangle inequality in protection logic"),
            ("limiartheta", 0, 360, 60, "Maximum angle allowed for a protection segment to be considered valid"),
            ("QT", 0, 100, 5, "Minimum side contribution to the triangle perimeter (in percent)"),
            ("MAXDIST", 0, 1_000_000, 0, "Maximum distance between urban vertices (0 means do not densify)"),
            ("tolerance", 0, 10_000, 3, "Distance tolerance for matching and cleaning geometries"),
            ("bigN", 0, 1_000_000_000, 10**6, "Large constant used to represent 'infinity' in comparisons"),
            ("smallN", 0, 1, 1e-6, "Small constant to avoid division by zero or detect negligible differences"),
            ("POSVALUE", 0, 1_000_000, 9999, "Large positive value used as a placeholder or for flagging"),
            ("NEGVALUE", -1_000_000, 0, -1, "Negative value used to mark invalid or missing data"),
        ]

        for name, mn, mx, val, tooltip in constants:
            label = QLabel(f"<b>{name}</b>: {tooltip}", numeric_group)
            label.setWordWrap(True)
            numeric_form_layout.addRow(label)

            if isinstance(val, float):
                spin = QDoubleSpinBox(numeric_group)
                spin.setRange(mn, mx)
                spin.setDecimals(8)
                spin.setValue(val)
                setattr(self, f"{name}DoubleSpin", spin)
            else:
                spin = QSpinBox(numeric_group)
                spin.setRange(mn, mx)
                spin.setValue(val)
                setattr(self, f"{name}Spin", spin)

            spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
            spin.setToolTip(tooltip)
            numeric_form_layout.addRow("Value:", spin)

        numeric_layout.addWidget(numeric_group)

        next_btn = QPushButton("Next ➡", numeric_container)
        next_btn.clicked.connect(lambda: self.sub_tab_stack.setCurrentIndex(1))
        numeric_layout.addWidget(next_btn, alignment=Qt.AlignRight)

        numeric_scroll_area.setWidget(numeric_container)
        self.sub_tab_stack.addWidget(numeric_scroll_area)

        # -------- Sub-tab 2: Attribute Variables (Scrollable) --------
        attr_scroll_area = QScrollArea(page)
        attr_scroll_area.setWidgetResizable(True)
        attr_container = QWidget()
        attr_layout = QVBoxLayout(attr_container)

        attr_group = QGroupBox("Attribute Variables", attr_container)
        attr_form_layout = QFormLayout(attr_group)

        vars_ = [
            ("ADDVAR", False, "NEWVAR", "fid_1", "Include an additional urban attribute (e.g., district) in interface output"),
            ("ADDVAR2", False, "NEWVAR2", "CorePC", "Include a second urban attribute in interface output"),
            ("ADDFLAMVAR", False, "NEWFLAMVAR", "idflam", "Include an additional flammable attribute in output (e.g., feature ID)"),
            ("ADDFLAMVAR2", False, "NEWFLAMVAR2", "FuelRisk", "Include a second flammable attribute in output (e.g., risk level)"),
        ]

        for checkbox_name, default, var_name, var_default, tooltip in vars_:
            label = QLabel(f"<b>{checkbox_name}</b>: {tooltip}", attr_group)
            label.setWordWrap(True)
            attr_form_layout.addRow(label)

            checkbox = QCheckBox(attr_group)
            checkbox.setChecked(default)
            setattr(self, f"{checkbox_name}Check", checkbox)

            line_edit = QLineEdit(var_default, attr_group)
            setattr(self, f"{var_name}Edit", line_edit)

            attr_form_layout.addRow("Activate:", checkbox)
            attr_form_layout.addRow("Attribute Name:", line_edit)

        attr_layout.addWidget(attr_group)

        back_btn = QPushButton("⬅ Back", attr_container)
        back_btn.clicked.connect(lambda: self.sub_tab_stack.setCurrentIndex(0))
        attr_layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        attr_scroll_area.setWidget(attr_container)
        self.sub_tab_stack.addWidget(attr_scroll_area)

        # Add the stack to the main layout
        main_layout.addWidget(self.sub_tab_stack)
        page.setLayout(main_layout)
        self.tabs.addTab(page, "Parameters")


    def _browse_input(self):
        path = QFileDialog.getExistingDirectory(self, "Select Input Folder", "")
        if path:
            self.inputFolderEdit.setText(path)
        else:
            QMessageBox.warning(self, "Input Folder", "Please select an input folder.")

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if path:
            self.outputFolderEdit.setText(path)
        else:
            QMessageBox.warning(self, "Output Folder", "Please select an output folder.")

    def _on_ok(self):
        progress = QProgressDialog("Processing parameters...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        for i in range(101):
            QTimer.singleShot(i*20, lambda v=i: progress.setValue(v))
        QTimer.singleShot(105*20, lambda: (progress.close(), self.accept(), QMessageBox.information(self, "Done", "Parameters saved.")))

    def getValues(self):
        return {
            "INPUT_FOLDER": self.inputFolderEdit.text(),
            "OUTPUT_FOLDER": self.outputFolderEdit.text(),
            "option": self.optionCombo.currentText(),
            "x0": self.x0DoubleSpin.value(),
            "y0": self.y0DoubleSpin.value(),
            "K": self.KSpin.value(),
            "KF": self.KFSpin.value(),
            "limiar": self.limiarDoubleSpin.value(),
            "limiartheta": self.limiarthetaSpin.value(),
            "QT": self.QTSpin.value(),
            "KDTREE_DIST_UPPERBOUND": self.KDTREE_DIST_UPPERBOUNDSpin.value(),
            "d_box": self.d_boxSpin.value(),
            "MAXDIST": self.MAXDISTSpin.value(),
            "tolerance": self.toleranceSpin.value(),
            "bigN": self.bigNSpin.value(),
            "smallN": self.smallNDoubleSpin.value(),
            "POSVALUE": self.POSVALUESpin.value(),
            "NEGVALUE": self.NEGVALUESpin.value(),
            "ADDVAR": self.ADDVARCheck.isChecked(),
            "NEWVAR": self.NEWVAREdit.text(),
            "ADDVAR2": self.ADDVAR2Check.isChecked(),
            "NEWVAR2": self.NEWVAR2Edit.text(),
            "ADDFLAMVAR": self.ADDFLAMVARCheck.isChecked(),
            "NEWFLAMVAR": self.NEWFLAMVAREdit.text(),
            "ADDFLAMVAR2": self.ADDFLAMVAR2Check.isChecked(),
            "NEWFLAMVAR2": self.NEWFLAMVAR2Edit.text(),
        }
