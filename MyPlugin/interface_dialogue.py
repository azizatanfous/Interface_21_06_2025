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
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QTimer


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
        self.setWindowTitle("Fire Management Parameters")
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
            "Configure fire-management plugin parameters. Make sure each field is set correctly before proceeding.",
            parent=self
        )
        intro.setWordWrap(True)
        intro.setFont(QFont('Segoe UI', 10, QFont.Bold))

        # Tabs
        self.tabs = QTabWidget(self)
        self._create_tab1()
        self._create_tab2()
        self._create_tab3()

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
        form = QFormLayout(page)

        # Input folder
        self.inputFolderEdit = QLineEdit(page)
        self.inputFolderEdit.setToolTip("Directory containing input data.")
        browseInput = QPushButton("Browse...", page)
        browseInput.setIcon(QIcon(':/icons/folder.png'))
        browseInput.setToolTip("Select input folder")
        browseInput.clicked.connect(self._browse_input)
        h1 = QHBoxLayout(); h1.addWidget(self.inputFolderEdit); h1.addWidget(browseInput)
        form.addRow("INPUT_FOLDER:", h1)

        # Output folder
        self.outputFolderEdit = QLineEdit(page)
        self.outputFolderEdit.setToolTip("Directory for saving results.")
        browseOutput = QPushButton("Browse...", page)
        browseOutput.setIcon(QIcon(':/icons/folder.png'))
        browseOutput.setToolTip("Select output folder")
        browseOutput.clicked.connect(self._browse_output)
        h2 = QHBoxLayout(); h2.addWidget(self.outputFolderEdit); h2.addWidget(browseOutput)
        form.addRow("OUTPUT_FOLDER:", h2)

        # Mode
        self.optionCombo = QComboBox(page)
        self.optionCombo.addItems(["altorisco", "todos"]);
        self.optionCombo.setToolTip("Processing mode")
        form.addRow("Option:", self.optionCombo)

        # Coordinates
        self.x0DoubleSpin = QDoubleSpinBox(page)
        self.x0DoubleSpin.setRange(-1e9, 1e9); self.x0DoubleSpin.setValue(-98407.00)
        self.x0DoubleSpin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.x0DoubleSpin.setToolTip("X-origin coordinate")
        form.addRow("x0:", self.x0DoubleSpin)

        self.y0DoubleSpin = QDoubleSpinBox(page)
        self.y0DoubleSpin.setRange(-1e9, 1e9); self.y0DoubleSpin.setValue(-102297.80)
        self.y0DoubleSpin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.y0DoubleSpin.setToolTip("Y-origin coordinate")
        form.addRow("y0:", self.y0DoubleSpin)

        # Pick-point button
        self.pickPointBtn = QPushButton("Pick point", page)
        self.pickPointBtn.setToolTip("Click on the map to choose x0/y0")
        form.addRow("", self.pickPointBtn)
        
        self.tabs.addTab(page, "General")

    def _create_tab2(self):
        page = QWidget()
        form = QFormLayout(page)
        for name, default in [
            ("CREATE_INTERFACE", True), ("TESTIDX", True),
            ("READ", True), ("MAIN_ALGO", True),
            ("SELECT", True), ("SAVE", True)
        ]:
            cb = QCheckBox(name, page)
            cb.setChecked(default)
            cb.setToolTip(f"Enable {name.lower().replace('_', ' ')} stage")
            setattr(self, f"{name}Check", cb)
            form.addRow(cb)
        self.tabs.addTab(page, "Parameters")

    def _create_tab3(self): 
        page = QWidget()
        form = QFormLayout(page)

        # Numeric constants
        constants = [
            ("D", 0, 1_000_000, 500),
            ("d", 0, 1_000_000, 500),
            ("K", 1, 1000, 60),
            ("KF", 1, 1000, 60),
            ("limiar", 0, 100, 1.05),
            ("limiartheta", 0, 360, 60),
            ("QT", 0, 100, 5),
            ("MAXDIST", 0, 1_000_000, 0),
            ("tolerance", 0, 10_000, 3),
            ("KDTREE_DIST_UPPERBOUND", 0, 1_000_000, 500),
            ("d_box", 0, 100_000, 2500),
            ("bigN", 0, 1_000_000_000, 10**6),
            ("smallN", 0, 1, 1e-6),
            ("POSVALUE", 0, 1_000_000, 9999),
            ("NEGVALUE", -1_000_000, 0, -1),
        ]
        for name, mn, mx, val in constants:
            if isinstance(val, float):
                spin = QDoubleSpinBox(page)
                spin.setRange(mn, mx)
                spin.setValue(val)
                setattr(self, f"{name}DoubleSpin", spin)
            else:
                spin = QSpinBox(page)
                spin.setRange(mn, mx)
                spin.setValue(val)
                setattr(self, f"{name}Spin", spin)
            spin.setButtonSymbols(QAbstractSpinBox.NoButtons)
            spin.setToolTip(f"Set {name} value")
            form.addRow(f"{name}:", spin)

        # Quality factor (Q)
        self.QSpin = QDoubleSpinBox(page)
        self.QSpin.setRange(0.0, 1.0)
        self.QSpin.setSingleStep(0.01)
        self.QSpin.setValue(0.1)
        self.QSpin.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.QSpin.setToolTip("Quality factor")
        form.addRow("Q:", self.QSpin)

        # Variables
        vars_ = [
            ("ADDVAR", False, "NEWVAR", "fid_1"),
            ("ADDVAR2", False, "NEWVAR2", "CorePC"),
            ("ADDFLAMVAR", False, "NEWFLAMVAR", "idflam"),
            ("ADDFLAMVAR2", False, "NEWFLAMVAR2", "FuelRisk"),
        ]
        for chk, checked, ed, default in vars_:
            c = QCheckBox(chk, page)
            c.setChecked(checked)
            c.setToolTip(f"Enable {chk.lower()}")
            e = QLineEdit(default, page)
            e.setToolTip(f"Name for {chk.lower()}")
            setattr(self, f"{chk}Check", c)
            setattr(self, f"{ed}Edit", e)
            form.addRow(c, e)

        self.tabs.addTab(page, "Constants")


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
            "D": self.DSpin.value(),
            "d": self.dSpin.value(),
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
            "Q": self.QSpin.value(),
            "CREATE_INTERFACE": self.CREATE_INTERFACECheck.isChecked(),
            "TESTIDX": self.TESTIDXCheck.isChecked(),
            "READ": self.READCheck.isChecked(),
            "MAIN_ALGO": self.MAIN_ALGOCheck.isChecked(),
            "SELECT": self.SELECTCheck.isChecked(),
            "SAVE": self.SAVECheck.isChecked(),
        }
