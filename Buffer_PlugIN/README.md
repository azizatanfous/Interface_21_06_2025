# 🌍 Urban & Flammable Loader Plugin for QGIS

---

## 🗺️ Overview
This QGIS plugin streamlines geospatial analysis of **urban areas** and **flammable zones in Portugal**.

### What You Can Do:
- Load **Portuguese administrative boundaries**, **urban areas**, and **flammable zones**
- Select a **district** and optional **municipality** as your study area
- **Crop** urban and flammable layers to the selected region
- Apply a **buffer zone** around urban areas
- **Merge** buffered and non-buffered urban layers
- Visualize everything directly within QGIS 

---

## ✨ Features
- 📌 Load **Map of Portugal**, **Urban**, and **Flammable** layers
- 📌 Focus your analysis by **district/municipality**
- 📌 **Crop** layers to your selected study area
- 📌 Generate **buffer zones** around urban regions (configurable distance)
- 📌 **Merge** buffered & non-buffered urban areas
- 📌 Automatic coloring for easy visualization
- 📌 Outputs in **GPKG format** (compatible with GIS software)

---

## 🔄 Workflow
1. **Load Layers**:
   - Portuguese administrative map
   - Urban layer
   - Flammable layer
2. **Select Flammable Option**:  
   Choose either `altorisco` or `todos`
3. **Set Output Folder**
4. **Define Buffer Distance** (default: 2 meters)
5. **Choose Study Area**:
   - Select district
   - Optionally select municipality
6. **Process Data**:
   - Crop layers
   - Buffer urban layer
   - Merge outputs
   - Automatically load results into QGIS

---
## 📂 Default Data & Output Paths

By default, the plugin expects data to be located in:

`C:\Users\aziza\Desktop\Last_version_of_reaserch_work\interface_python\Interface_Github\Buffer_PlugIN\Data`

This folder should contain the following files:

| File Name             | Description                                |
|-----------------------|--------------------------------------------|
| `Portuguese_Map.gpkg` | Portuguese administrative boundaries       |
| `Urban.gpkg`          | Urban areas                                |
| `High_Risk.gpkg`      | Flammable zones for the **altorisco** option |
| `Todos.gpkg`          | Flammable zones for the **todos** option    |

When you use the plugin interface to browse files, you can navigate to this folder to load the default data.

---

### 📥 Output Folder

All processed outputs (cropped layers, buffers, merged files, etc.) are saved by default to:

`C:\Users\aziza\Desktop\Last_version_of_reaserch_work\interface_python\Interface_Github\Buffer_PlugIN\output_folder`

This is where you'll find:
- Cropped admin, urban, and flammable layers
- Buffered urban layers
- Merged urban layers (buffered + non-buffered)

> ⚙️ **Note:**  
> Both the **data source folder** and **output folder** can be customized directly via the plugin interface if you need to work with alternative directories or datasets.

---
## ⚙️ Installation Requirements

### Dependencies
Make sure your **QGIS Python environment** includes the following:

| Library         | Purpose                      |
|-----------------|------------------------------|
| `qgis.PyQt`     | Plugin user interface (UI)   |
| `qgis.core`     | Core GIS operations          |
| `qgis.gui`      | QGIS GUI integration         |
| `PyQt5.QtCore`  | Core Qt functions            |
| `processing`    | QGIS geoprocessing tools     |
| `os`            | File handling operations     |

> These are all standard in QGIS 3.x environments — no extra installation needed.

---

## 🚀 Usage Instructions

### Step 1: Load the Plugin
- Launch **QGIS**
- Install or enable **Urban & Flammable Loader Plugin**
- Open the plugin from the **Plugins** menu

### Step 2: Page 1
- Load **Admin**, **Urban**, and **Flammable** layers
- Choose the flammable option: `altorisco` or `todos`
- Define:
  - Output folder
  - Buffer distance (in meters)
- Click **Load All Layers**
- Proceed by clicking **Next → Select Study Area**

### Step 3: Page 2
- Select **district** and optionally a **municipality**
- Click **Crop, Buffer, Merge with Layer Flag** to process and generate outputs

---

## 📂 Output Files

| File Name                                    | Description                                |
|---------------------------------------------|--------------------------------------------|
| `selected_region_temp_{region}.gpkg`        | Cropped administrative layer              |
| `Cropped_Urban_{region}.gpkg`               | Cropped urban layer                       |
| `buffer_croppedurban_{region}.gpkg`         | Buffered urban layer                      |
| `buffered_cropped_urbanlayer_{region}.gpkg` | Merged urban (buffered & non-buffered)    |
| `Cropped_Flammable_{region}.gpkg`           | Cropped flammable layer                   |

> Example `{region}`: `Lisbon_Oeiras`

---

## 🎨 Layer Colors

| Layer            | Color                                |
|------------------|--------------------------------------|
| Admin Layer      | Light beige `#f4e1c1` with border    |
| Urban Layer      | Blue `#3399cc`                       |
| Buffered Urban   | Same as urban, labeled `"buffer"`    |
| Flammable Layer  | Red `#ff4d4d`                        |

---

## 🖥️ QGIS Compatibility
- ✅ Compatible with **QGIS 3.x** (tested on 3.16+)
- ❌ Not compatible with QGIS 2.x or older versions

---

## 👤 Author
- **Aziza Ben Tanfous**
- 📧 Email: [aztanf@gmail.com](mailto:aztanf@gmail.com)

---

## 📜 License
Released under the **MIT License**.