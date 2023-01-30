#-----------------------------------------------------------
# Copyright (C) 2023 Ben Wirf
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtWidgets import (QAction, QMainWindow, QFrame, QGridLayout,
                            QHBoxLayout, QPushButton, QLabel)

from PyQt5.QtCore import Qt

from qgis.core import QgsMapLayerType

from qgis.gui import QgsMapCanvas

def classFactory(iface):
    return RasterViewerPlugin(iface)


class RasterViewerPlugin:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction('Raster Viewer', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.rasterViewerWindow = RasterViewer(self.iface.layerTreeView())

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        root = self.iface.layerTreeView().layerTreeModel().rootGroup()
        project_rasters = [l for l in root.findLayers() if l.layer().type() == QgsMapLayerType.RasterLayer and l.itemVisibilityChecked()]
        if not project_rasters:
            self.iface.messageBar().pushMessage('There are no visible raster layers in the current project')
        else:
            self.rasterViewerWindow.set_default_layer()
            self.rasterViewerWindow.show()
        

class RasterViewer(QMainWindow):
    def __init__(self, layer_tree_view):
        self.view = layer_tree_view
        self.root = self.view.layerTreeModel().rootGroup()
        super(RasterViewer, self).__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setGeometry(200, 200, 900, 800)
        self.frame = QFrame(self)
        self.setCentralWidget(self.frame)
        self.grid_layout = QGridLayout(self.frame)
        self.hb_layout = QHBoxLayout()
        self.prev_btn = QPushButton('Previous', self)
        self.prev_btn.clicked.connect(self.show_previous)
        self.nxt_btn = QPushButton('Next', self)
        self.nxt_btn.clicked.connect(self.show_next)
        self.label = QLabel('', self)
        self.label.setMinimumWidth(500)
        self.label.setAlignment(Qt.AlignCenter)
        self.canvas = QgsMapCanvas()
        self.layers = []
        self.layer_names = []
        self.hb_layout.addWidget(self.prev_btn)
        self.hb_layout.addWidget(self.label)
        self.hb_layout.addWidget(self.nxt_btn)
        self.grid_layout.addLayout(self.hb_layout, 0, 0, Qt.AlignCenter)
        self.grid_layout.addWidget(self.canvas)
        
    def set_default_layer(self):
        self.layers = [l for l in self.root.findLayers() if l.layer().type() == QgsMapLayerType.RasterLayer and l.itemVisibilityChecked()]
        self.sel_idxs = sorted(self.view.selectionModel().selectedIndexes())
        if self.sel_idxs:
            if self.view.index2node(self.sel_idxs[0]) in self.layers:
                self.canvas.setLayers([self.view.index2node(self.sel_idxs[0]).layer()])
            else:
                self.canvas.setLayers([self.layers[0].layer()])
        else:
            self.canvas.setLayers([self.layers[0].layer()])
        self.canvas.zoomToFullExtent()
        self.label.setText(self.canvas.layers()[0].name())
        
    def show_next(self):
        self.layers = [l for l in self.root.findLayers() if l.layer().type() == QgsMapLayerType.RasterLayer and l.itemVisibilityChecked()]
        self.layer_names = [l.layer().name() for l in self.layers]
        max_idx = len(self.layers)-1
        current_name = self.label.text()
        idx = self.layer_names.index(current_name)
        if idx == max_idx:
            self.canvas.setLayers([self.layers[0].layer()])
        else:
            self.canvas.setLayers([self.layers[idx+1].layer()])
        self.canvas.zoomToFullExtent()
        self.label.setText(self.canvas.layers()[0].name())
        
    def show_previous(self):
        self.layers = [l for l in self.root.findLayers() if l.layer().type() == QgsMapLayerType.RasterLayer and l.itemVisibilityChecked()]
        self.layer_names = [l.layer().name() for l in self.layers]
        max_idx = len(self.layers)-1
        current_name = self.label.text()
        idx = self.layer_names.index(current_name)
        if idx == 0:
            self.canvas.setLayers([self.layers[max_idx].layer()])
        else:
            self.canvas.setLayers([self.layers[idx-1].layer()])
        self.canvas.zoomToFullExtent()
        self.label.setText(self.canvas.layers()[0].name())