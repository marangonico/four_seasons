from decimal import Decimal as D

from XPLMDataAccess import *
from XPLMDefs import *
from XPLMDisplay import *
from XPLMGraphics import *
from XPLMMenus import *
from XPLMPlugin import *
from XPLMProcessing import *
from XPLMUtilities import *
from XPStandardWidgets import *
from XPWidgetDefs import *
from XPWidgets import *

from xp_utils import log

MSG_ADD_DATAREF = 0x01000000


class XPCustomDRef(object):

    xplm_types = {
        'int': xplmType_Int,
        'float': xplmType_Float,
        'double': xplmType_Double,
    }

    dref = None
    data_type = None
    signature = None
    value = 0
    writeable = False

    read_int_cb = None
    read_float_cb = None
    read_double_cb = None

    python_interface = None

    def __init__(self, python_interface, signature, data_type, initial_value=None, writeable=False):

        self.python_interface = python_interface

        self.signature = signature
        self.data_type = data_type
        self.writeable = writeable

        if data_type == 'int':
            self.value = initial_value if initial_value is not None else int(0)
            self.read_int_cb = self.read_value_cb
        elif data_type == 'float':
            self.value = initial_value if initial_value is not None else float(0)
            self.read_float_cb = self.read_value_cb
        elif data_type == 'double':
            self.value = initial_value if initial_value is not None else float(0)
            self.read_double_cb = self.read_value_cb
        else:
            log('type not supported')
            return None

        self.register()

    def register(self):

        self.dref = XPLMRegisterDataAccessor(
            self.python_interface,
            self.signature,  # inDataName
            self.xplm_types[self.data_type],  # inDataType
            1 if self.writeable else 0,  # inIsWritable
            self.read_int_cb,  # inReadInt
            None,  # inWriteInt
            self.read_float_cb,  # inReadFloat
            None,  # inWriteFloat
            self.read_double_cb,  # inReadDouble
            None,  # inWriteDouble
            None,  # inReadIntArray
            None,  # inWriteIntArray
            None,  # inReadFloatArray
            None,  # inWriteFloatArray
            None,  # inReadData
            None,  # inWriteData
            0,  # inReadRefcon
            0,  # inWriteRefcon
        )

        # log('dref_register={}:{}'.format(self.signature, self.dref))

    def unregister(self):
        if self.dref:
            XPLMUnregisterDataAccessor(self.python_interface, self.dref)

    def read_value_cb(self, inRefCon):
        return self.value

    def notify_datarefeditor(self, plugin_id):
        XPLMSendMessageToPlugin(plugin_id, MSG_ADD_DATAREF, self.signature)

    def __repr__(self):
        return 'sig:{} - value:{} - dref:{} - data_type:{}'.format(
            self.signature, self.value, self.dref, self.data_type)


class XPCustomDRefsMgr(object):

    drefs = {}

    python_interface = None

    def __init__(self, python_interface=None):

        self.python_interface = python_interface
        super(XPCustomDRefsMgr, self).__init__()

    def create_dref(self, signature, data_type, writeable=False):
        self.drefs[signature] = XPCustomDRef(
            self.python_interface, signature, data_type=data_type, writeable=writeable)
        return self.drefs[signature]

    def get_value(self, signature):
        return self.drefs[signature].value

    def set_value(self, signature, value):
        self.drefs[signature].value = value

    def exists(self, signature):
        return signature in self.drefs

    def notify_datarefeditor(self, plugin_id):
        for signature in self.drefs:
            XPLMSendMessageToPlugin(plugin_id, MSG_ADD_DATAREF, signature)

    def unregister_all(self):
        for signature in self.drefs:
            log('unregister dref', signature)
            self.drefs[signature].unregister()

    def destroy_dref(self, signature):
        log('destroy_dref', signature)
        self.drefs[signature].unregister()
        self.drefs.pop(signature)

    def destroy_all(self):
        self.unregister_all()
        self.drefs = {}


# custom_drefs_mgr = XPCustomDRefsMgr()


class XPDref:
    '''
    Easy Dataref access
    
    Copyright (C) 2011  Joan Perez i Cauhe
    '''

    dr_get = None
    dr_set = None
    cast = None
    dref = None
    is_decimal = False

    last_value = None

    dref_mapping = {
        'int': {
            'dr_get': XPLMGetDatai,
            'dr_set': XPLMSetDatai,
            'cast': int, },
        'float': {
            'dr_get': XPLMGetDataf,
            'dr_set': XPLMSetDataf,
            'cast': float, },
        'double': {
            'dr_get': XPLMGetDatad,
            'dr_set': XPLMSetDatad,
            'cast': float, },
    }

    def __init__(self, signature, dref_type, is_decimal=False):

        if dref_type not in self.dref_mapping:
            print "ERROR: invalid DataRef type " + dref_type
            return

        # signature = signature.strip()

        self.dr_get = self.dref_mapping[dref_type]['dr_get']
        self.dr_set = self.dref_mapping[dref_type]['dr_set']
        self.cast = self.dref_mapping[dref_type]['cast']

        self.dref = XPLMFindDataRef(signature)
        if not self.dref:
            print "Can't find DataRef " + signature
            return

        self.is_decimal = is_decimal

        # force the initial value
        _ = self.value

    def set(self, value):
        self.dr_set(self.dref, self.cast(value))

    def get(self):
        return self.dr_get(self.dref)

    # def __getattr__(self, name):
    #     if name == 'value':
    #         return self.get()
    #     else:
    #         raise AttributeError
    #
    # def __setattr__(self, name, value):
    #     if name == 'value':
    #         self.set(value)
    #     else:
    #         self.__dict__[name] = value

    @property
    def value(self):
        if self.is_decimal:
            return self.decimal_value
        else:
            return self.get()

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def decimal_value(self):
        return D(self.get()).quantize('0.00')

# class XPDrefArray:
#     '''
#     Easy Dataref access
#
#     Copyright (C) 2011  Joan Perez i Cauhe
#     '''
#
#     index = 0
#     count = 0
#     last = 0
#
#     rset = None
#     rget = None
#     dref = None
#
#     is_array = False
#
#     def __init__(self, signature, dref_type="float"):
#
#         signature = signature.strip()
#
#         if '[' in signature:
#             # We have an array
#             self.isarray = True
#             range_array = signature[signature.find('[') + 1:signature.find(']')].split(':')
#             signature = signature[:signature.find('[')]
#             if len(range_array) < 2:
#                 range_array.append(range_array[0])
#
#             self.init_array_dref(range_array[0], range_array[1], dref_type)
#
#         elif dref_type == "int":
#             self.dr_get = XPLMGetDatai
#             self.dr_set = XPLMSetDatai
#             self.cast = int
#         elif dref_type == "float":
#             self.dr_get = XPLMGetDataf
#             self.dr_set = XPLMSetDataf
#             self.cast = float
#         elif dref_type == "double":
#             self.dr_get = XPLMGetDatad
#             self.dr_set = XPLMSetDatad
#             self.cast = float
#         else:
#             print "ERROR: invalid DataRef type", dref_type
#
#         self.dref = XPLMFindDataRef(signature)
#         if not self.dref:
#             print "Can't find " + signature + " DataRef"
#
#     def init_array_dref(self, first, last, dref_type):
#
#         self.index = int(first)
#         self.count = int(last) - int(first) + 1
#         self.last = int(last)
#
#         if dref_type == "int":
#             self.rget = XPLMGetDatavi
#             self.rset = XPLMSetDatavi
#             self.cast = int
#         elif dref_type == "float":
#             self.rget = XPLMGetDatavf
#             self.rset = XPLMSetDatavf
#             self.cast = float
#         elif dref_type == "bit":
#             self.rget = XPLMGetDatab
#             self.rset = XPLMSetDatab
#             self.cast = float
#         else:
#             print "ERROR: invalid DataRef type", dref_type
#         pass
#
#     def set(self, value):
#         if self.isarray:
#             self.rset(self.dref, value, self.index, len(value))
#         else:
#             self.dr_set(self.dref, self.cast(value))
#
#     def get(self):
#         if self.isarray:
#             values = []
#             self.rget(self.dref, values, self.index, self.count)
#             return values
#         else:
#             return self.dr_get(self.dref)
#
#     def __getattr__(self, name):
#         if name == 'value':
#             return self.get()
#         else:
#             raise AttributeError
#
#     def __setattr__(self, name, value):
#         if name == 'value':
#             self.set(value)
#         else:
#             self.__dict__[name] = value
