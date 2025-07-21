# ---------- UrbanFlammableLoader.py ----------
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .plugin_dialog import UrbanFlammableLoaderDialog

class UrbanFlammableLoader:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        self.action = QAction(QIcon(":/images/themes/default/mActionAddRasterLayer.svg"), "Urban Layer Loader and Cropper", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&UrbanFlammableLoader", self.action)

    def unload(self):
        self.iface.removePluginMenu("&UrbanFlammableLoader", self.action)

    def run(self):
        if self.dialog is None:
            self.dialog = UrbanFlammableLoaderDialog()
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()