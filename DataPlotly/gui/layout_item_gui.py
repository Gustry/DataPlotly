# -*- coding: utf-8 -*-
"""Plot Layout Gui Handling

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtWidgets import (
    QPushButton,
    QVBoxLayout
)
from qgis.gui import (
    QgsLayoutItemAbstractGuiMetadata,
    QgsLayoutItemBaseWidget,
    QgsLayoutItemPropertiesWidget
)

from DataPlotly.layouts.plot_layout_item import ITEM_TYPE
from DataPlotly.gui.gui_utils import GuiUtils
from DataPlotly.gui.plot_settings_widget import DataPlotlyPanelWidget


class PlotLayoutItemWidget(QgsLayoutItemBaseWidget):
    """
    Configuration widget for layout plot items
    """

    def __init__(self, parent, layout_object):
        super().__init__(parent, layout_object)
        self.plot_item = layout_object
        self.message_bar = None

        vl = QVBoxLayout()
        vl.setContentsMargins(0, 0, 0, 0)

        self.plot_properties_button = QPushButton(self.tr('Setup Plot'))
        vl.addWidget(self.plot_properties_button)
        self.plot_properties_button.clicked.connect(self.show_properties)

        self.panel = None
        self.setPanelTitle(self.tr('Plot Properties'))
        self.item_properties_widget = QgsLayoutItemPropertiesWidget(self, layout_object)
        vl.addWidget(self.item_properties_widget)
        self.setLayout(vl)

    def show_properties(self):
        """
        Shows the plot properties panel
        """
        self.panel = DataPlotlyPanelWidget(mode=DataPlotlyPanelWidget.MODE_LAYOUT, message_bar=self.message_bar)
        self.panel.registerExpressionContextGenerator(self.plot_item)
        self.panel.set_print_layout(self.plot_item.layout())

        self.panel.linked_map_combo.blockSignals(True)
        self.panel.linked_map_combo.setItem(self.plot_item.linked_map)
        self.panel.linked_map_combo.blockSignals(False)

        self.panel.filter_by_map_check.toggled.connect(self.filter_by_map_toggled)
        self.panel.filter_by_atlas_check.toggled.connect(self.filter_by_atlas_toggled)
        self.panel.linked_map_combo.itemChanged.connect(self.linked_map_changed)

        self.panel.filter_by_map_check.blockSignals(True)
        self.panel.filter_by_map_check.setChecked(self.plot_item.filter_by_map)
        self.panel.filter_by_map_check.blockSignals(False)

        self.panel.filter_by_atlas_check.blockSignals(True)
        self.panel.filter_by_atlas_check.setChecked(self.plot_item.filter_by_atlas)
        self.panel.filter_by_atlas_check.blockSignals(False)

        self.panel.set_settings(self.plot_item.plot_settings)
        # self.panel.set_settings(self.layoutItem().plot_settings)
        self.openPanel(self.panel)
        self.panel.widgetChanged.connect(self.update_item_settings)
        self.panel.panelAccepted.connect(self.set_item_settings)

    def update_item_settings(self):
        """
        Updates the plot item without dismissing the properties panel
        """
        if not self.panel:
            return

        self.plot_item.set_plot_settings(self.panel.get_settings())
        self.plot_item.update()

    def set_item_settings(self):
        """
        Updates the plot item based on the settings from the properties panel
        """
        if not self.panel:
            return

        self.plot_item.set_plot_settings(self.panel.get_settings())
        self.panel = None
        self.plot_item.update()

    def filter_by_map_toggled(self, value):
        """
        Triggered when the filter by map option is toggled
        """
        self.plot_item.filter_by_map = bool(value)
        self.plot_item.update()

    def filter_by_atlas_toggled(self, value):
        """
        Triggered when the filter by atlas option is toggled
        """
        self.plot_item.filter_by_atlas = bool(value)
        self.plot_item.update()

    def linked_map_changed(self, linked_map):
        """
        Triggered when the linked map is changed
        """
        self.plot_item.set_linked_map(linked_map)
        self.plot_item.update()

    def setNewItem(self, item):  # pylint: disable=missing-docstring
        if item.type() != ITEM_TYPE:
            return False

        self.plot_item = item
        self.item_properties_widget.setItem(item)

        if self.panel is not None:
            self.panel.set_settings(self.plot_item.plot_settings)

            self.panel.filter_by_map_check.blockSignals(True)
            self.panel.filter_by_map_check.setChecked(item.filter_by_map)
            self.panel.filter_by_map_check.blockSignals(False)

            self.panel.filter_by_atlas_check.blockSignals(True)
            self.panel.filter_by_atlas_check.setChecked(item.filter_by_atlas)
            self.panel.filter_by_atlas_check.blockSignals(False)

            self.panel.linked_map_combo.blockSignals(True)
            self.panel.linked_map_combo.setItem(self.plot_item.linked_map)
            self.panel.linked_map_combo.blockSignals(False)

        return True

    def setDesignerInterface(self, iface):  # pylint: disable=missing-docstring
        super().setDesignerInterface(iface)
        self.message_bar = iface.messageBar()
        if self.panel:
            self.panel.message_bar = self.message_bar


class PlotLayoutItemGuiMetadata(QgsLayoutItemAbstractGuiMetadata):
    """
    Metadata for plot item GUI classes
    """

    def __init__(self):
        super().__init__(ITEM_TYPE, QCoreApplication.translate('DataPlotly', 'Plot Item'))

    def creationIcon(self):  # pylint: disable=missing-docstring, no-self-use
        return GuiUtils.get_icon('dataplotly.svg')

    def createItemWidget(self, item):  # pylint: disable=missing-docstring, no-self-use
        return PlotLayoutItemWidget(None, item)
