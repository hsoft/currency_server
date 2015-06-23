# Created By: Virgil Dupras
# Created On: 2010-02-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

# Interfaces for proxies in cocoalib

import logging

import objc

from ..reg import InvalidCodeError
from .objcmin import NSObject

def signature(signature):
    """Returns an objc.signature with 'i' and 'f' letters changed to correct NSInteger and
    CGFloat values.
    """
    signature = bytes(signature, encoding='ascii')
    signature = signature.replace(b'i', objc._C_NSInteger)
    signature = signature.replace(b'I', objc._C_NSUInteger)
    signature = signature.replace(b'f', objc._C_CGFloat)
    return objc.typedSelector(signature)

class PyGUIObject(NSObject):
    def initWithCocoa_pyParent_(self, cocoa, pyparent):
        super(PyGUIObject, self).init()
        self.cocoa = cocoa
        self.py = self.py_class(self, pyparent.py)
        return self
    
    def connect(self):
        if hasattr(self.py, 'connect'):
            self.py.connect()
    
    def disconnect(self):
        if hasattr(self.py, 'disconnect'):
            self.py.disconnect()
    
    def free(self):
        # call this method only when you don't need to use this proxy anymore. you need to call this
        # if you want to release the cocoa side (self.cocoa is holding a refcount)
        # We don't delete py, it might be called after the free. It will be garbage collected anyway.
        # The if is because there is something happening giving a new ref to cocoa right after
        # the free, and then the ref gets to 1 again, free is called again.
        self.disconnect()
        if hasattr(self, 'cocoa'):
            del self.cocoa
    
    #--- Python -> Cocoa
    def refresh(self):
        self.cocoa.refresh()
    

class PyOutline(PyGUIObject):
    def cancelEdits(self):
        self.py.cancel_edits()
    
    @signature('c@:@@')
    def canEditProperty_atPath_(self, propname, path):
        node = self.py.get_node(path)
        assert node is self.py.selected_node
        return getattr(node, 'can_edit_' + propname, False)
    
    def saveEdits(self):
        self.py.save_edits()
    
    def selectedPath(self):
        return self.py.selected_path
    
    def setSelectedPath_(self, path):
        self.py.selected_path = path
    
    def selectedPaths(self):
        return self.py.selected_paths
    
    def setSelectedPaths_(self, paths):
        self.py.selected_paths = paths
    
    def property_valueAtPath_(self, property, path):
        try:
            return getattr(self.py.get_node(path), property)
        except IndexError:
            logging.warning("%r doesn't have a node at path %r", self.py, path)
            return ''
    
    def setProperty_value_atPath_(self, property, value, path):
        setattr(self.py.get_node(path), property, value)
    
    #--- Python -> Cocoa
    def start_editing(self):
        self.cocoa.startEditing()
    
    def stop_editing(self):
        self.cocoa.stopEditing()
    
    def update_selection(self):
        self.cocoa.updateSelection()
    

class PyTable(PyGUIObject):
    #--- Helpers
    def _getrow(self, row):
        try:
            return self.py[row]
        except IndexError:
            msg = "Trying to get an out of bounds row ({} / {}) on table {}"
            logging.warning(msg.format(row, len(self.py), self.py.__class__.__name__))
    
    #--- Cocoa --> Python
    def add(self):
        self.py.add()
    
    def cancelEdits(self):
        self.py.cancel_edits()
    
    @signature('c@:@i')
    def canEditColumn_atRow_(self, column, row):
        return self.py.can_edit_cell(column, row)
    
    def deleteSelectedRows(self):
        self.py.delete()
    
    @signature('i@:')
    def numberOfRows(self):
        return len(self.py)
    
    def saveEdits(self):
        self.py.save_edits()
    
    def selectRows_(self, rows):
        self.py.select(list(rows))
    
    def selectedRows(self):
        return self.py.selected_indexes
    
    def selectionAsCSV(self):
        return self.py.selection_as_csv()
    
    @signature('v@:@@i')
    def setValue_forColumn_row_(self, value, column, row):
        # this try except is important for the case while a row is in edition mode and the delete
        # button is clicked.
        try:
            self._getrow(row).set_cell_value(column, value)
        except AttributeError:
            msg = "Trying to set an attribute that can't: {} with value {} at row {} on table {}"
            logging.warning(msg.format(column, value, row, self.py.__class__.__name__))
            raise
    
    @signature('v@:@c')
    def sortByColumn_desc_(self, column, desc):
        self.py.sort_by(column, desc=desc)
    
    @signature('@@:@i')
    def valueForColumn_row_(self, column, row):
        return self._getrow(row).get_cell_value(column)
    
    #--- Python -> Cocoa
    def show_selected_row(self):
        self.cocoa.showSelectedRow()
    
    def start_editing(self):
        self.cocoa.startEditing()
    
    def stop_editing(self):
        self.cocoa.stopEditing()
    
    def update_selection(self):
        self.cocoa.updateSelection()
    

class PyFairware(NSObject):
    def appName(self):
        return ""
    
    @signature('c@:')
    def isRegistered(self):
        return self.py.registered
    
    @signature('c@:')
    def isFirstRun(self):
        return self.py.is_first_run
    
    def isCodeValid_withEmail_(self, code, email):
        try:
            self.py.validate_code(code, email)
            return None
        except InvalidCodeError as e:
            return str(e)
    
    @signature('v@:@@c')
    def setRegisteredCode_andEmail_registerOS_(self, code, email, registerOS):
        self.py.set_registration(code, email, registerOS)
    
    def unpaidHours(self):
        return self.py.unpaid_hours
    
