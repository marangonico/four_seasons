from XPLMDefs import *
from XPLMDataAccess import *
from XPLMMenus import *
from XPLMPlugin import *
from XPLMProcessing import *
from XPLMUtilities import *
from XPStandardWidgets import *
from XPWidgetDefs import *
from XPWidgets import *

from XPLMDisplay import *
from XPLMGraphics import *

from xp_utils import log


class XPFiller(object):

    x = 0
    y = 0

    def __init__(self, container):

        self.container = container
        self.reset_x()
        self.reset_y()

        super(XPFiller, self).__init__()

    def reset_x(self):
        self.x = self.container.x1 + self.container.pad_x

    def reset_y(self):
        self.y = self.container.y1 - self.container.pad_y - 10 if self.container.has_title else 0

    def fill(self, widget, fill=''):

        fill_directives = fill.split(',')

        if 'x+' in fill_directives:
            self.x += (widget.w + widget.pad_x * 2)
        if 'y+' in fill_directives:
            self.y -= (widget.h + widget.pad_y * 2)
        if 'y/2+' in fill_directives:
            self.y -= (widget.h + widget.pad_y)
        if 'x-' in fill_directives:
            self.x -= (widget.w + widget.pad_x * 2)
        if 'y-' in fill_directives:
            self.y += (widget.h + widget.pad_y * 2)
        if 'x0' in fill_directives:
            self.reset_x()
        if 'y0' in fill_directives:
            self.reset_y()

    # def align(self, widget, align=''):
    #
    #     align_directives = align.split(',')
    #     if 'right' in align_directives:
    #         self.x += (widget.w + widget.pad_x * 2)


class XPWidget(object):

    xp_widget_class = None

    filler = None
    uses_filler = False

    has_title = False

    name = ''
    descriptor = ''
    tag = ''

    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0

    w = 0
    h = 0

    default_w = 0
    default_h = 20

    reference = 0
    parent_container = None
    parent_container_id = 0

    handler_cb = None

    pad_x = 0
    pad_y = 0

    offset_y = 0

    childs_pad_x = 0
    childs_pad_y = 0

    is_root = False
    visible = True

    group = None

    align = ''

    def __init__(
            self, name=None, descriptor='', x1=None, y1=None, w=None, h=None,
            visible=True, is_root=False, parent_container=None, properties=[], group=None, **kwargs):

        self.name = name
        self.descriptor = descriptor
        self.tag = kwargs.get('tag', '')

        self.group = group

        self.visible = visible
        self.is_root = is_root

        self.align = kwargs.get('align', '')

        self.parent_container = parent_container
        if parent_container:

            self.pad_x = kwargs.get('pad_x', parent_container.childs_pad_x)
            self.pad_y = kwargs.get('pad_y', parent_container.childs_pad_y)

            if not x1:
                self.x1 = parent_container.filler.x + self.pad_x
            else:
                self.x1 = parent_container.x1 + parent_container.pad_x + x1 + self.pad_x

            if not y1:
                self.y1 = parent_container.filler.y - self.pad_y
            else:
                self.y1 = parent_container.y1 - parent_container.pad_y - y1 - self.pad_y

            self.parent_container_id = parent_container.reference

        else:

            self.pad_x = kwargs.get('pad_x', 0)
            self.pad_y = kwargs.get('pad_y', 0)

            self.x1 = x1 + self.pad_x
            self.y1 = y1 - self.pad_y
            self.parent_container_id = 0

            self.childs_pad_x = kwargs.get('childs_pad_x', 0)
            self.childs_pad_y = kwargs.get('childs_pad_y', 0)

        self.w = w if w else self.default_w
        self.h = h if h else self.default_h

        # log('x1', self.x1)
        # log('y1', self.y1)
        # log('w', self.w)
        # log('h', self.h)

        self.x2 = self.x1 + self.w
        self.y2 = self.y1 - self.h

        # log('XPWidget.__init__() name', name)

        self.reference = XPCreateWidget(
            self.x1, self.y1 - self.offset_y, self.x2, self.y2 - self.offset_y,
            1 if self.visible else 0, descriptor, 1 if self.is_root else 0,
            self.parent_container_id, self.xp_widget_class,
        )

        # log('XPWidget reference', self.reference)

        for prop in properties:
            XPSetWidgetProperty(self.reference, prop['name'], prop['value'])

        if self.parent_container:
            self.parent_container.notify_child(self, kwargs.get('fill', ''))

        if self.uses_filler and not self.filler:
            self.filler = XPFiller(self)

    def notify_child(self, child, fill=''):
        self.filler.fill(child, fill)

    def destroy(self, python_interface=None, destroy_children=True):
        """"""
        XPDestroyWidget(python_interface, self.reference, 1 if destroy_children else 0)

    def set_property(self, property_name, value):
        XPSetWidgetProperty(self.reference, property_name, value)

    def get_property(self, property_name):
        return XPGetWidgetProperty(self.reference, property_name, None)

    def register_handler(self, python_interface=None, handler_function=None):

        self.handler_cb = handler_function
        XPAddWidgetCallback(python_interface, self.reference, self.handler_cb)

    def hide(self):
        XPHideWidget(self.reference)

    def show(self):
        XPShowWidget(self.reference)

    def is_visible(self):
        return XPIsWidgetVisible(self.reference)

    def set_descriptor(self, descriptor):
        self.descriptor = descriptor
        XPSetWidgetDescriptor(self.reference, self.descriptor)


class XPWidgetCheckRadioButtons(XPWidget):

    @property
    def state(self):
        return self.get_property(xpProperty_ButtonState)

    @property
    def value(self):
        return self.state == 1

    @value.setter
    def value(self, value):
        self.set_property(xpProperty_ButtonState, 1 if value else 0)


class XPWidgetWindow(XPWidget):
    """"""
    xp_widget_class = xpWidgetClass_MainWindow

    uses_filler = True
    has_title = True

    def __init__(self, **kwargs):

        super(XPWidgetWindow, self).__init__(**kwargs)
        if kwargs.get('has_close_boxes', False):
            self.set_property(xpProperty_MainWindowHasCloseBoxes, 1)


class XPWidgetCheckButton(XPWidgetCheckRadioButtons):
    """"""

    xp_widget_class = xpWidgetClass_Button

    default_w = 20

    def __init__(self, **kwargs):

        super(XPWidgetCheckButton, self).__init__(**kwargs)
        self.set_property(xpProperty_ButtonType, xpRadioButton)
        self.set_property(xpProperty_ButtonBehavior, xpButtonBehaviorCheckBox)
        self.set_property(xpProperty_ButtonState, kwargs.get('state', 0))


class XPWidgetRadioButton(XPWidgetCheckRadioButtons):
    """"""

    xp_widget_class = xpWidgetClass_Button

    default_w = 20

    def __init__(self, **kwargs):

        super(XPWidgetRadioButton, self).__init__(**kwargs)
        self.set_property(xpProperty_ButtonType, xpRadioButton)
        self.set_property(xpProperty_ButtonBehavior, xpButtonBehaviorRadioButton)
        self.set_property(xpProperty_ButtonState, kwargs.get('state', 0))


class XPWidgetPushButton(XPWidget):
    """"""

    xp_widget_class = xpWidgetClass_Button

    default_w = 100
    default_h = 60

    def __init__(self, **kwargs):

        super(XPWidgetPushButton, self).__init__(**kwargs)
        self.set_property(xpProperty_ButtonType, xpPushButton)
        self.set_property(xpProperty_ButtonBehavior, xpButtonBehaviorPushButton)
        self.set_property(xpProperty_ButtonState, kwargs.get('value', 0))


class XPWidgetLabel(XPWidget):
    """"""
    xp_widget_class = xpWidgetClass_Caption

    default_w = 150
    offset_y = -2

    @property
    def caption(self):
        return self.get_property(xpProperty_ButtonState)

    @property
    def value(self):
        return self.state == 1

    @value.setter
    def value(self, value):
        self.set_property(xpProperty_ButtonState, 1 if value else 0)


class XPUI(object):
    """"""

    widgets = {}

    python_interface = None

    def __init__(self, python_interface=None):

        self.python_interface = python_interface
        super(XPUI, self).__init__()

    def create_widget(
            self, widget_class=None, name=None, descriptor='', x1=None, y1=None, w=None, h=None,
            visible=True, is_root=False, parent_container=None, properties=[], group=None, **kwargs):

        # log('create_widget name', name)

        self.widgets[name] = widget_class(
            name=name, descriptor=descriptor, x1=x1, y1=y1, w=w, h=h, visible=visible, is_root=is_root,
            parent_container=parent_container, properties=properties, group=group, **kwargs)

        return self.widgets[name]

    def exists(self, name=None):
        return name in self.widgets

    def destroy_widget(self, name=None, destroy_children=True):
        self.widgets[name].destroy(python_interface=self.python_interface, destroy_children=destroy_children)
        self.widgets.pop(name)

    def get_widgets_from_group(self, group):
        return [widget for key, widget in self.widgets.items() if widget.group and widget.group == group]
