#!/usr/bin/python

#    This file is part of python-registry.
#
#    python-registry is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    python-registry is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with python-registry.  If not, see <http://www.gnu.org/licenses/>.


import sys
import wx
from Registry import *

def nop(*args, **kwargs):
    pass

class RegistryTreeCtrl(wx.TreeCtrl):
    def __init__(self, *args, **kwargs):
        super(RegistryTreeCtrl, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpandItem)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelected)
        self._value_list_view = False

    def add_registry(self, registry):
        root_key = registry.root()
        root_item = self.AddRoot(root_key.name())
        self.SetPyData(root_item, {"key": root_key,
                                    "has_expanded": False})

        if len(root_key.subkeys()) > 0:
            self.SetItemHasChildren(root_item)

    def _extend(self, item):
        key = self.GetPyData(item)["key"]
        
        for subkey in key.subkeys():
            subkey_item = self.AppendItem(item, subkey.name())
            self.SetPyData(subkey_item, {"key": subkey,
                                         "has_expanded": False})

            if len(subkey.subkeys()) > 0:
                self.SetItemHasChildren(subkey_item)

        self.GetPyData(item)["has_expanded"] = True                

    def OnExpandItem(self, event):
        item = event.GetItem()
        if not item.IsOk():
            item = self.GetSelection()

        if not self.GetPyData(item)["has_expanded"]:
            self._extend(item)

    def OnSelected(self, event):
        if not self._value_list_view:
            return

        item = event.GetItem()
        if not item.IsOk():
            item = self.GetSelection()

        key = self.GetPyData(item)["key"]

        self._value_list_view.DeleteAllItems()
        for value in key.values():
            n = self._value_list_view.GetItemCount()
            self._value_list_view.InsertStringItem(n, value.name())
            self._value_list_view.SetStringItem(n, 1, value.value_type_str())

    def set_value_list(self, list_view):
        self._value_list_view = list_view

def _expand_into(dest, src):
    vbox = wx.BoxSizer(wx.VERTICAL)
    vbox.Add(src, 1, wx.EXPAND | wx.ALL)
    dest.SetSizer(vbox)

class RegView(wx.Frame):
    def __init__(self, parent, registry):
        super(RegView, self).__init__(parent, -1, "Registry Viewer")

        vsplitter = wx.SplitterWindow(self, -1)
        panel_left = wx.Panel(vsplitter, -1)
        self._tree = RegistryTreeCtrl(panel_left, -1)
        _expand_into(panel_left, self._tree)

        hsplitter = wx.SplitterWindow(vsplitter, -1)
        panel_top = wx.Panel(hsplitter, -1)
        panel_bottom = wx.Panel(hsplitter, -1)

        self._value_list_view = wx.ListCtrl(panel_top, -1, style=wx.LC_REPORT)
        self._value_list_view.InsertColumn(0, "Value name")
        self._value_list_view.InsertColumn(1, "Value type")
        self._value_list_view.SetColumnWidth(1, 100)
        self._value_list_view.SetColumnWidth(0, 300)
        self._tree.set_value_list(self._value_list_view)

        _expand_into(panel_top,    self._value_list_view)
        _expand_into(panel_bottom, wx.StaticText(panel_bottom, -1, "hello world2"))

        hsplitter.SplitHorizontally(panel_top, panel_bottom)
        vsplitter.SplitVertically(panel_left, hsplitter)
        _expand_into(self, vsplitter)

        self.SetSize((800, 600))
        self.Centre()

        self._tree.add_registry(registry)

def usage():
    return "  USAGE:\n\t%s <Windows Registry file>" % (sys.argv[0])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print usage()
        sys.exit(-1)

    registry = Registry.Registry(sys.argv[1])

    app = wx.App(False)
    frame = RegView(None, registry=registry)
    frame.Show()
    app.MainLoop()
