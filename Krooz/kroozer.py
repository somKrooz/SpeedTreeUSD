from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
import hou
import xml.etree.ElementTree as ET
import json


class Cool_kroozer(QtWidgets.QDialog):
    def __init__(self):
        super(Cool_kroozer,self).__init__(hou.qt.mainWindow())
        self.configure_dialog()
        self.widgets()
        self.layout()
        self.connection()

    def configure_dialog(self):
        width = 340
        height = 300

        self.setWindowTitle("Speed Tree Importer")
        self.setMinimumWidth(width) 
        self.setMinimumHeight(height)

        self.setMaximumWidth(width)
        self.setMaximumHeight(height)
        

    def widgets(self):
        self.stmap = hou.qt.FileLineEdit()
        self.file = hou.qt.FileLineEdit()
        # self.mylbl = QtWidgets.QLabel("Krooz")

        self.com_geo = QtWidgets.QLineEdit()
        self.com_geo.setPlaceholderText("geo")

        self.com_mat = QtWidgets.QLineEdit()
        self.com_mat.setPlaceholderText("mat")

        self.out_mat = QtWidgets.QLineEdit()
        self.out_mat.setPlaceholderText("out_mat")


        self.Create = QtWidgets.QPushButton("Create")
        self.Init = QtWidgets.QPushButton("Auto Init")

    def layout(self):
        
        self.mainlyt = QtWidgets.QVBoxLayout(self)   
        self.optionlytb = QtWidgets.QFormLayout(self)
        self.optionlytb.addRow("File",self.file)
        self.optionlytb.addRow("Stmap",self.stmap)
        self.optionlytb.addRow("Comp Geometry",self.com_geo)
        self.optionlytb.addRow("Material Library",self.com_mat)
        self.optionlytb.addRow("Comp Material",self.out_mat)


        self.mainlyt.addLayout(self.optionlytb)
        # self.mainlyt.addWidget(self.mylbl)
        self.mainlyt.addWidget(self.Init)
        self.mainlyt.addWidget(self.Create)
        


    def connection(self):
        self.Create.clicked.connect(self.myThing)
        self.Init.clicked.connect(self.Auto_take)

    
    def Auto_take(self):
        self.com_geo.setText("/stage/componentgeometry1")
        self.com_mat.setText("/stage/materiallibrary1")
        self.out_mat.setText("/stage/componentmaterial1")


    def myThing(self):

        file_path = self.stmap.text()
        mesh_path = self.file.text()
        directory, filename = str(mesh_path).rsplit('/', 1)
        cool = str(mesh_path).split("/")
        name = str(cool[-1]).split(".")
        mesh_name = str(name[0])
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            xml_data = file.read()


        # Define map categories
        map_categories = {
            "Color": "COLOR",
            "Opacity": "OPACITY",
            "Normal": "NORMAL",
            "Gloss": "GLOSS",
            "Specular": "SPEC"
        }

        root = ET.fromstring(xml_data)

        materials_list = []

        for material_elem in root.findall('.//Material'):
            material_data = {"Material Name": material_elem.get("Name"), "Map Names": {}}

            for category in map_categories.values():
                material_data["Map Names"][category] = {"File": None, "Source": None}

            for map_elem in material_elem.findall('./Map'):
                map_name = map_elem.get("Name")
                category = map_categories.get(map_name, None)

                if category:
                    # Add map name and its file/source to the material data
                    material_data["Map Names"][category] = {
                        "File": map_elem.get("File"),
                        "Source": f"{directory}/{map_elem.get('File')}"
                    }

            materials_list.append(material_data)


        # Export JSON data to a file
        with open(f'{file_path}_cache.json', 'w') as json_file:
           json.dump(materials_list,json_file, indent=2)


        with open(f'{file_path}_cache.json', 'r') as json_file:
            materials_list = json.load(json_file)

        componentGeo = self.com_geo.text()
        materialLib = self.com_mat.text()
        componentMat = self.out_mat.text()

        mat = hou.node(materialLib)

        def prerequisites():
            global Nodes
            componentGeometry = hou.node(componentGeo)

            componentGeometry.parm("sourceinput").set(1)
            componentGeometry.parm("prefixpartitionsubsets").set(False)
            componentGeometry.parm("source").set(f"{mesh_path}")
            componentGeometry.parm("partitionattribs").set("shop_materialpath")

        prerequisites()

        material_count = 0

        for material in materials_list:
            material_name = material["Material Name"]
            map_names = material["Map Names"]

            main = mat.createNode("mtlxstandard_surface",material_name)
            main.parm("specular_roughness").set(.7)

            for category, map_data in map_names.items():
                if str(category).startswith("COLOR"):
                    if map_data["File"] != None:

                        img = mat.createNode("mtlximage",f"{material_name}_COLOR")
                        img.parm("file").set(map_data['Source'])
                        main.setInput(1,img)

                if str(category).startswith("OPACITY"):
                    if map_data["File"] != None:
                        op = mat.createNode("mtlximage",f"{material_name}_OPACITY")
                        op.parm("file").set(map_data['Source'])
                        main.setInput(38,op)

        #houdini 19.5 doesnt work ! mtx bump node   
                # if str(category).startswith("NORMAL"):
                #     if map_data["File"] != None:
                #         norm = mat.createNode("mtlximage",f"{material_name}_NORMAL")
                #         norm.parm("file").set(map_data['Source'])
                #         bump = mat.createNode("mtlxbump",f"{material_name}_Bump")
                #         bump.parm("scale").set(0.05)
                #         bump.setInput(0,norm)
                #         main.setInput(40,bump)

                if str(category).startswith("GLOSS"):
                    if map_data["File"] != None:
                        gls = mat.createNode("mtlximage",f"{material_name}_GLOSS")
                        gls.parm("file").set(map_data['Source'])
                        main.setInput(2,gls)
                
                        
            material_count +=1

        mat.layoutChildren()

        componentmaterial = hou.node(componentMat)
        componentmaterial.parm("nummaterials").set(material_count)

        for id, material in enumerate(materials_list): 
            material_name = material["Material Name"]
            componentmaterial.parm(f"primpattern{id+1}").set(f"/ASSET/geo/{mesh_name}/{material_name}")
            componentmaterial.parm(f"matspecpath{id+1}").set(f"/ASSET/mtl/{material_name}")