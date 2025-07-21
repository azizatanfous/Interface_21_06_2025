# ---------- plugin_dialog.py ----------
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QComboBox, QStackedWidget, QWidget, QSpinBox
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsSingleSymbolRenderer, QgsFillSymbol, QgsLineSymbol, QgsCoordinateReferenceSystem, QgsField
)
from PyQt5.QtCore import QVariant
import processing
import os

class UrbanFlammableLoaderDialog(QDialog):
    """
    Main plugin dialog class for loading layers, selecting a study area, cropping, buffering, 
    and merging urban and flammable layers.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Urban & Flammable Loader, Cropper & Buffer")
        self.resize(520, 640)
        # Stack widget to manage multi-page interface
        self.stack = QStackedWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
        # -------- Page 1: Input Layers and Buffer Configuration --------
        page1 = QWidget()
        layout1 = QVBoxLayout()
        # Admin Layer input
        self.adminPath = QLineEdit()
        self.browseAdmin = QPushButton("Browse")
        admin_layout = QHBoxLayout()
        admin_layout.addWidget(self.adminPath)
        admin_layout.addWidget(self.browseAdmin)
        layout1.addWidget(QLabel("Portuguese Map (Admin Layer)"))
        layout1.addLayout(admin_layout)
        # Urban Layer input
        self.urbanPath = QLineEdit()
        self.browseUrban = QPushButton("Browse")
        urban_layout = QHBoxLayout()
        urban_layout.addWidget(self.urbanPath)
        urban_layout.addWidget(self.browseUrban)
        layout1.addWidget(QLabel("Urban Layer"))
        layout1.addLayout(urban_layout)
        # Flammable Layer input with option selection
        self.optionSelector = QComboBox()
        self.optionSelector.addItems(["altorisco", "todos"])
        self.flammablePath = QLineEdit()
        self.browseFlammable = QPushButton("Browse")
        flam_layout = QHBoxLayout()
        flam_layout.addWidget(QLabel("Select Option:"))
        flam_layout.addWidget(self.optionSelector)
        flam_file = QHBoxLayout()
        flam_file.addWidget(self.flammablePath)
        flam_file.addWidget(self.browseFlammable)
        layout1.addLayout(flam_layout)
        layout1.addLayout(flam_file)
        # Output folder input
        self.outputFolderPath = QLineEdit()
        self.browseOutputFolder = QPushButton("Browse")
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.outputFolderPath)
        output_layout.addWidget(self.browseOutputFolder)
        layout1.addWidget(QLabel("Output Folder"))
        layout1.addLayout(output_layout)
        # Buffer distance input
        self.bufferDistance = QSpinBox()
        self.bufferDistance.setMinimum(1)
        self.bufferDistance.setMaximum(10000)
        self.bufferDistance.setValue(2)
        layout1.addWidget(QLabel("Buffer Distance (meters):"))
        layout1.addWidget(self.bufferDistance)
        # Action buttons
        self.loadButton = QPushButton("Load All Layers")
        self.nextButton = QPushButton("Next → Select Study Area")
        layout1.addWidget(self.loadButton)
        layout1.addWidget(self.nextButton)
        page1.setLayout(layout1)
        # -------- Page 2: Select Study Area --------
        page2 = QWidget()
        layout2 = QVBoxLayout()
        layout2.addWidget(QLabel("Select Study Area"))
        self.districtDropdown = QComboBox()
        self.municipalityDropdown = QComboBox()
        layout2.addWidget(QLabel("District:"))
        layout2.addWidget(self.districtDropdown)
        layout2.addWidget(QLabel("Municipality:"))
        layout2.addWidget(self.municipalityDropdown)

        self.cropButton = QPushButton("Crop, Buffer, Merge with Layer Flag")
        layout2.addWidget(self.cropButton)
        page2.setLayout(layout2)
        # Add pages to stack
        self.stack.addWidget(page1)
        self.stack.addWidget(page2)
        # Connect buttons to their actions
        self.browseAdmin.clicked.connect(self.set_admin_path)
        self.browseUrban.clicked.connect(self.set_urban_path)
        self.browseFlammable.clicked.connect(self.set_flammable_path)
        self.browseOutputFolder.clicked.connect(self.set_output_folder)
        self.loadButton.clicked.connect(self.load_layers)
        self.nextButton.clicked.connect(self.fill_dropdowns_and_next)
        self.cropButton.clicked.connect(self.crop_layers)
        self.districtDropdown.currentTextChanged.connect(self.update_municipalities)
    # ---------- Input Path Handlers ----------
    def set_admin_path(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Portuguese Map (Admin Layer)')
        self.adminPath.setText(path)

    def set_urban_path(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Urban Layer')
        self.urbanPath.setText(path)

    def set_flammable_path(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Select Flammable Layer')
        self.flammablePath.setText(path)

    def set_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        self.outputFolderPath.setText(folder)
    # ---------- Layer Loading ----------
    def load_layers(self):
        self.admin_layer = QgsVectorLayer(self.adminPath.text(), "Portuguese Map", "ogr")
        self.urban_layer = QgsVectorLayer(self.urbanPath.text(), "Urban", "ogr")
        self.flammable_layer = QgsVectorLayer(self.flammablePath.text(), f"Flammable - {self.optionSelector.currentText()}", "ogr")

        if self.admin_layer.isValid():
            QgsProject.instance().addMapLayer(self.admin_layer)
            self.apply_color(self.admin_layer, "#f4e1c1", outline=True)
        if self.urban_layer.isValid():
            QgsProject.instance().addMapLayer(self.urban_layer)
            self.urban_color = "#3399cc"
            self.apply_color(self.urban_layer, self.urban_color)
        if self.flammable_layer.isValid():
            QgsProject.instance().addMapLayer(self.flammable_layer)
            self.flammable_color = "#ff4d4d"
            self.apply_color(self.flammable_layer, self.flammable_color)
    # ---------- Dropdown Handling ----------
    def fill_dropdowns_and_next(self):
        """Fill district dropdown with available districts and switch to next page."""
        districts = sorted({f['district'] for f in self.admin_layer.getFeatures() if f['district']})
        self.districtDropdown.clear()
        self.districtDropdown.addItems(districts)
        self.stack.setCurrentIndex(1)

    def update_municipalities(self):
        """Update municipalities based on the selected district."""
        district = self.districtDropdown.currentText()
        municipalities = sorted({f['municipality'] for f in self.admin_layer.getFeatures() if f['district'] == district})
        self.municipalityDropdown.clear()
        self.municipalityDropdown.addItems(municipalities)

    def apply_color(self, layer, color_hex, outline=False):
        """Apply color to a given layer depending on its geometry type."""
        if layer.geometryType() == 2:
            symbol = QgsFillSymbol.createSimple({'color': color_hex, 'outline_color': '#555555' if outline else color_hex, 'outline_width': '0.3'})
        elif layer.geometryType() == 1:
            symbol = QgsLineSymbol.createSimple({'color': color_hex, 'width': '0.5'})
        else:
            symbol = layer.renderer().symbol()
            symbol.setColor(QColor(color_hex))
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))
        layer.triggerRepaint()
        
    # ---------- Cropping and Buffering ----------
    def crop_layers(self):
        """
        Crop the Admin layer by selected district/municipality, crop urban and flammable layers
        accordingly, buffer the urban layer, merge outputs, and load the result into QGIS.
        """
        district = self.districtDropdown.currentText()
        municipality = self.municipalityDropdown.currentText()
        region_name = district if not municipality else f"{district}_{municipality}"
        output_folder = self.outputFolderPath.text()
        # Crop Admin layer by district/municipality
        selected_layer_path = os.path.join(output_folder, f"selected_region_temp_{region_name}.gpkg")
        processing.run("native:extractbyexpression", {
            'INPUT': self.admin_layer,
            'EXPRESSION': f'"district" = \'{district}\'' + (f' AND "municipality" = \'{municipality}\'' if municipality else ''),
            'OUTPUT': selected_layer_path
        })
        # Crop Urban Layer
        urban_out_path = os.path.join(output_folder, f"Cropped_Urban_{region_name}.gpkg")
        processing.run("native:selectbylocation", {'INPUT': self.urban_layer, 'PREDICATE': [0], 'INTERSECT': selected_layer_path, 'METHOD': 0})
        processing.run("native:saveselectedfeatures", {'INPUT': self.urban_layer, 'OUTPUT': urban_out_path})
        # Buffer Urban Layer
        buffer_distance = self.bufferDistance.value()
        buffer_out_path = os.path.join(output_folder, f"buffer_croppedurban_{region_name}.gpkg")
        processing.run("native:buffer", {'INPUT': urban_out_path, 'DISTANCE': buffer_distance, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0, 'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': buffer_out_path})
        # Add 'layer' flag attribute to identify buffered/non-buffered features
        for path, label in [(urban_out_path, 'no buffer'), (buffer_out_path, 'buffer')]:
            layer = QgsVectorLayer(path, "temp", "ogr")
            layer.startEditing()
            if 'layer' not in [f.name() for f in layer.fields()]:
                layer.dataProvider().addAttributes([QgsField('layer', QVariant.String)])
                layer.updateFields()
            idx = layer.fields().indexFromName('layer')
            for feat in layer.getFeatures():
                layer.changeAttributeValue(feat.id(), idx, label)
            layer.commitChanges()
        # Merge buffered and non-buffered layers
        merge_out_path = os.path.join(output_folder, f"buffered_cropped_urbanlayer_{region_name}.gpkg")
        if os.path.exists(merge_out_path):
            os.remove(merge_out_path)
        processing.run("native:mergevectorlayers", {
            'LAYERS': [buffer_out_path, urban_out_path],
            'CRS': QgsCoordinateReferenceSystem('EPSG:3763'),
            'OUTPUT': merge_out_path
        })
        # Load merged layer
        merged_layer = QgsVectorLayer(merge_out_path, f"Buffered Cropped UrbanLayer - {region_name}", "ogr")
        if merged_layer.isValid():
            QgsProject.instance().addMapLayer(merged_layer)
        # Crop Flammable Layer
        flammable_out_path = os.path.join(output_folder, f"Cropped_Flammable_{region_name}.gpkg")
        processing.run("native:selectbylocation", {'INPUT': self.flammable_layer, 'PREDICATE': [0], 'INTERSECT': selected_layer_path, 'METHOD': 0})
        processing.run("native:saveselectedfeatures", {'INPUT': self.flammable_layer, 'OUTPUT': flammable_out_path})
        # Load and color flammable layer
        cropped_flammable = QgsVectorLayer(flammable_out_path, f"Cropped Flammable - {region_name}", "ogr")
        if cropped_flammable.isValid():
            QgsProject.instance().addMapLayer(cropped_flammable)
            self.apply_color(cropped_flammable, self.flammable_color)
