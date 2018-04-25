import os
import ConfigParser

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

from SandyBarbourUtilities import *

from four_seasons.globals import *
from four_seasons.xp_ui import *
from four_seasons.xp_utils import log
from four_seasons.XPDref import XPCustomDRefsMgr, XPDref
from four_seasons.zones import ZoneTemperateNorth, ZoneTropical, ZoneTemperateSouth, ZonePolar, ZoneTemperatePatagonia


class FourSeasons:

    seasons = [
        {'value': SEASON_SPRING, 'name': 'Spring', 'help_text': '', 'slug': 'spring'},
        {'value': SEASON_SUMMER, 'name': 'Summer', 'help_text': '', 'slug': 'summer'},
        {'value': SEASON_FALL, 'name': 'Fall', 'help_text': '', 'slug': 'fall'},
        {'value': SEASON_WINTER, 'name': 'Winter', 'help_text': '', 'slug': 'winter'},
        {'value': SEASON_WINTER_SNOW, 'name': 'Winter with Snow',
            'help_text': 'if Winter and temp. <= 0 degrees C', 'slug': 'winter_with_snow'},
        {'value': SEASON_WINTER_DEEP, 'name': 'Deep Winter',
            'help_text': 'if Winter and temp. < 10 degrees C. Only used by TerraMax', 'slug': 'winter_deep'},
    ]

    ZONES = [
        ZoneTemperateNorth('temperate North Hemisphere', 26, -180, 90, 180),
        ZoneTropical('tropical', -25, -180, 25, 180),
        ZoneTemperatePatagonia('Patagonia', -62, -100, -41, -20),
        ZoneTemperateSouth('temperate South Hemisphere', -62, -180, -26, 180),
        # ZonePolar('north polar', 61, -180, 90, 180),
        ZonePolar('antartica', -90, -180, -61, 180),
    ]

    season = None
    season_old = None

    local_date_days_dref = None
    local_date_days_last_value = None

    latitude_dref = None
    latitude_last_value = None

    temperature_ambient_c_dref = None

    rain_percent_dref = None

    longitude_dref = None

    parent = None

    is_quiet = False
    force_refresh = False

    config_filename = os.path.join(os.path.dirname(__file__), 'PI_four_seasons.cfg')
    # log('config_filename', config_filename)
    config = None

    def __init__(self, parent):

        log('init FourSeason')

        self.parent = parent

        self.latitude_dref = XPDref('sim/flightmodel/position/latitude', 'double')
        # for i in range(0, 10000):
        #     if '{}'.format(self.latitude_dref.value) != 'nan':
        #         break

        self.longitude_dref = XPDref('sim/flightmodel/position/longitude', 'double')
        self.local_date_days_dref = XPDref("sim/time/local_date_days", 'int')
        self.temperature_ambient_c_dref = XPDref("sim/weather/temperature_ambient_c", 'float')
        self.rain_percent_dref = XPDref("sim/weather/rain_percent", "float")

        self.config = ConfigParser.ConfigParser()

        if not os.path.exists(self.config_filename):
            self.config.add_section('mode')
            self.config.set('mode', 'automatic_season', '1')
            self.config.set('mode', 'season', '')
            self.config.add_section('terramax')
            self.config.set('terramax', 'enabled', '0')
            self.write_config()

        self.config.read(self.config_filename)
        log('config automatic_season', self.config.get('mode', 'automatic_season'))

        if self.config.get('terramax', 'enabled') == '1':
            self.parent.check_terramax_drefs()

        if self.config.get('mode', 'automatic_season') == '1':
            self.is_quiet = True
            self.calculate_season()
            self.is_quiet = False
        else:
            self.is_quiet = True
            log('manual season from config',int(self.config.get('mode', 'season')))
            self.set_season(int(self.config.get('mode', 'season')))
            self.is_quiet = False

    def write_config(self):
        self.config.write(open(self.config_filename, 'w'))

    def get_season_from_value(self, season_value):
        try:
            return [season for season in self.seasons if season['value'] == season_value][0]
        except IndexError:
            return {'value': None, 'name': '', 'help_text': '', },

    def get_season(self):
        return self.season

    def set_season(self, new_season=None):

        if not new_season:
            return

        log('set_season()')
        self.season_old = self.season
        log('season_old', self.season_old)
        self.season = new_season
        log('season', self.season)

        self.parent.custom_drefs.drefs[DREF_SIG_SEASON].value = self.season

        if self.config.get('terramax', 'enabled') == '1':
            self.parent.set_terramax_values(season=self.season)

        if not self.is_quiet and self.season != self.season_old or self.force_refresh:
            self.force_refresh = False
            command_ref = XPLMFindCommand("sim/operation/reload_scenery")
            XPLMCommandOnce(command_ref)

    def calculate_season(self, set_season=True):

        log('lat={}, lon={}'.format(self.latitude_dref.value, self.longitude_dref.value))
        if self.latitude_dref.value is None:
            return
        zone_found = False
        for zone in self.ZONES:

            if zone.is_within(self.latitude_dref.value, self.longitude_dref.value):

                zone_found = True
                log('within zone {}'.format(zone.name))

                season = zone.get_season(
                    doy=self.local_date_days_dref.value,
                    lat=self.latitude_dref.value,
                    lon=self.longitude_dref.value,
                    temperature=self.temperature_ambient_c_dref.value,
                    precipitation=self.rain_percent_dref.value > 0,
                )
                log('zone.get_season', season)
                break

        if not zone_found:
            log('No appliable zone')
            return None

        if set_season:
            self.set_season(season)

        return season

    def check_local_date(self):
        if not self.local_date_days_last_value or self.local_date_days_dref.value != self.local_date_days_last_value:
            self.local_date_days_last_value = self.local_date_days_dref.value
            self.calculate_season()

    def check_position(self):
        if not self.latitude_last_value or int(self.latitude_dref.value) != self.latitude_last_value:
            self.latitude_last_value = self.latitude_dref.value
            self.calculate_season()


class PythonInterface:

    __version__ = '0.9.0'

    four_seasons = None

    custom_drefs = None

    flightmodel_loop_CB = None

    menu = None
    menu_cb = None
    menu_plugins_item = None
    menu_ref = None
    menu_item_control_panel = None

    window_handler_cb = None
    window_widget = None

    radiobuttons_saved = None

    ui = None

    stopped = False

    def XPluginStart(self):

        SandyBarbourClearDisplay()

        self.Name = "Four Seasons"
        self.Sig = "nm.four_seasons"
        self.Desc = "A plugin driving season changes"

        self.custom_drefs = XPCustomDRefsMgr(self)
        self.custom_drefs.create_dref(DREF_SIG_SEASON, 'int')

        self.four_seasons = FourSeasons(self)

        self.ui = XPUI(python_interface=self)

        # Main menu
        self.menu_plugins_item = XPLMAppendMenuItem(XPLMFindPluginsMenu(), 'Four Seasons', 0, 1)
        self.menu_cb = self.menu_callback
        self.menu_ref = XPLMCreateMenu(
            self, 'Four Seasons', XPLMFindPluginsMenu(), self.menu_plugins_item, self.menu_cb, 0)
        self.menu_item_control_panel = XPLMAppendMenuItem(self.menu_ref, 'Control Panel', 100, 1)

        self.flightmodel_loop_CB = self.flightmodel_loop_callback
        XPLMRegisterFlightLoopCallback(self, self.flightmodel_loop_CB, 1.0, 0)

        return self.Name, self.Sig, self.Desc

    def flightmodel_loop_callback(self, elapsedMe, elapsedSim, counter, refcon):

        if self.stopped:
            return 0

        if self.ui.exists('wnd_control_panel') and self.ui.widgets['wnd_control_panel'].is_visible():
            self.refresh_control_panel()

        plugin_id = XPLMFindPluginBySignature("xplanesdk.examples.DataRefEditor")
        if plugin_id != XPLM_NO_PLUGIN_ID:
            self.custom_drefs.notify_datarefeditor(plugin_id)

        if self.four_seasons.config.get('mode', 'automatic_season') == '1':
            self.four_seasons.check_local_date()

        return 5

    def XPluginStop(self):

        self.stopped = True

        self.custom_drefs.destroy_all()

        if self.flightmodel_loop_CB:
            XPLMUnregisterFlightLoopCallback(self, self.flightmodel_loop_CB, 0)

        if self.ui.exists('wnd_control_panel'):
            self.ui.destroy_widget('wnd_control_panel')

        if self.menu_plugins_item:
            XPLMRemoveMenuItem(XPLMFindPluginsMenu(), self.menu_plugins_item)

        if self.menu_ref:
            XPLMDestroyMenu(self, self.menu_ref)

    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        """"""

    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):

        if inMessage:

            if self.stopped:
                return

            if inMessage == XPLM_MSG_SCENERY_LOADED or inMessage == XPLM_MSG_AIRPORT_LOADED:

                if self.four_seasons is None:
                    self.four_seasons = FourSeasons(self)

                if self.four_seasons.config.get('mode', 'automatic_season') == '1':
                    self.four_seasons.check_local_date()
                    self.four_seasons.check_position()

    def menu_callback(self, menuRef, menu_item):

        if menu_item:
            menu_item_string = str(menu_item)
            # log(menu_item_string)
            if menu_item_string == '100':

                # Start/Sy1 menuitem
                if not self.ui.exists('wnd_control_panel'):
                    self.create_control_panel_window()
                    self.save_control_panel_state()
                    self.ui.widgets['wnd_control_panel'].show()
                else:
                    if not self.ui.widgets['wnd_control_panel'].is_visible():
                        self.save_control_panel_state()
                        self.ui.widgets['wnd_control_panel'].show()
                        self.refresh_control_panel()

                # XPSetKeyboardFocus(self.routeInput)

    def create_control_panel_window(self):

        control_panel_window = self.ui.create_widget(
            XPWidgetWindow,
            name='wnd_control_panel',
            descriptor='Four Seasons Control Panel (Version {})'.format(self.__version__),
            x1=20, y1=500, w=500, h=320, pad_x=20, pad_y=20,
            is_root=True,
            has_close_boxes=True,
            childs_pad_x=1, childs_pad_y=1,
        )

        self.ui.create_widget(
            XPWidgetRadioButton,
            name='btn_automatic_season',
            parent_container=control_panel_window,
            fill='x+',
            state=1 if self.four_seasons.config.get('mode', 'automatic_season') == '1' else 0,
            group='seasons_checks',
        )

        self.ui.create_widget(
            XPWidgetLabel,
            name='lbl_automatic_season',
            descriptor='Determine seasons automatically',
            parent_container=control_panel_window,
            fill='y+,x0',
        )

        self.ui.create_widget(
            XPWidgetLabel,
            name='lbl_status',
            descriptor='',
            parent_container=control_panel_window,
            fill='y+,x0',
        )

        self.ui.create_widget(
            XPWidgetLabel,
            name='lbl_manual_selections', descriptor='Manual selections:',
            parent_container=control_panel_window,
            pad_y=0,
            fill='y/2+,x0',
        )

        control_panel_window.pad_x = control_panel_window.pad_x * 2
        control_panel_window.filler.reset_x()

        # pulsanti stagioni
        for item_idx, season in enumerate(self.four_seasons.seasons):

            # log('btn_manual_season_{}'.format(season['name'].lower()))
            self.ui.create_widget(
                XPWidgetRadioButton,
                name='btn_manual_season_{}'.format(season['slug']),
                tag=season['name'],
                parent_container=control_panel_window,
                fill='x+',
                state=(1 if not self.four_seasons.config.get('mode', 'automatic_season') == '1' and
                        self.four_seasons.get_season() == season['value'] else 0),
                group='seasons_checks',
            )

            self.ui.create_widget(
                XPWidgetLabel,
                name='lbl_manual_season_{}'.format(season['slug']),
                descriptor='{} {}'.format(
                    season['name'], '(' + season['help_text'] + ')' if season['help_text'] else ''),
                parent_container=control_panel_window,
                fill='y+,x0',
            )

        control_panel_window.pad_x = control_panel_window.pad_x / 2
        control_panel_window.filler.reset_x()

        self.ui.create_widget(
            XPWidgetLabel,
            name='lbl_warning',
            descriptor='Note: applying new values the scenery will be reloaded',
            parent_container=control_panel_window,
            fill='y+,x0',
        )

        self.ui.create_widget(
            XPWidgetCheckButton,
            name='btn_terramax',
            parent_container=control_panel_window,
            fill='x+',
            state=1 if self.four_seasons.config.get('terramax', 'enabled') == '1' else 0,
        )

        self.ui.create_widget(
            XPWidgetLabel,
            name='lbl_terramax',
            descriptor='Feed terramax datarefs',
            parent_container=control_panel_window,
            fill='y+,x0',
        )

        self.ui.create_widget(
            XPWidgetPushButton,
            name='btn_force_refresh',
            descriptor='Force Refresh',
            parent_container=control_panel_window,
            x1=130,
        )

        self.ui.create_widget(
            XPWidgetPushButton,
            name='btn_refresh_season',
            descriptor='Refresh Season',
            parent_container=control_panel_window,
            x1=250,
        )

        self.ui.create_widget(
            XPWidgetPushButton,
            name='btn_apply',
            descriptor='Save & Apply',
            parent_container=control_panel_window,
            x1=370,
        )

        # Register our widget handler
        self.ui.widgets['wnd_control_panel'].register_handler(
            python_interface=self, handler_function=self.window_handler_callback)

    def refresh_control_panel(self):

        new_season = self.four_seasons.calculate_season(set_season=False)
        log('new_season', new_season)
        if new_season:
            new_season_string = self.four_seasons.get_season_from_value(new_season)['name']
        else:
            new_season_string = ''

        log('refresh_control_panel season', self.four_seasons.season)

        self.ui.widgets['lbl_status'].set_descriptor(
            'Current: {} - Estimated: {} - Temp: {:5.2f} deg C'.format(
                self.four_seasons.get_season_from_value(self.four_seasons.season)['name'],
                new_season_string,
                self.four_seasons.temperature_ambient_c_dref.value,
            )
        )

    def window_handler_callback(self, inMessage, inWidget, inParam1, inParam2):


        if inMessage == xpMessage_CloseButtonPushed:


            if self.ui.exists('wnd_control_panel'):
                self.ui.widgets['wnd_control_panel'].hide()

            return 1

        # terramax button
        if inMessage == xpMsg_ButtonStateChanged and inParam1 == self.ui.widgets['btn_terramax'].reference:
            if self.ui.widgets['btn_terramax'].value:
                self.four_seasons.config.set('terramax', 'enabled', '1')
                self.set_terramax_values(self.four_seasons.season)
            else:
                self.four_seasons.config.set('terramax', 'enabled', '0')
                self.reset_terramax_values()
                self.destroy_terramax_drefs()

            return 1

        # seasons radiobuttons
        radiobutton_references = [button.reference for button in self.ui.get_widgets_from_group('seasons_checks')]
        if inMessage == xpMsg_ButtonStateChanged and inParam1 in radiobutton_references:
            if inParam2:
                for reference in radiobutton_references:
                    if reference != inParam1:
                        XPSetWidgetProperty(reference, xpProperty_ButtonState, 0)
            else:
                XPSetWidgetProperty(inParam1, xpProperty_ButtonState, 1)

            return 1

        if inMessage == xpMsg_PushButtonPressed:

            if inParam1 == self.ui.widgets['btn_force_refresh'].reference:

                self.four_seasons.force_refresh = True

                if self.ui.widgets['btn_automatic_season'].value:
                    self.four_seasons.calculate_season()
                else:
                    self.four_seasons.set_season(self.four_seasons.season)

                self.four_seasons.force_refresh = False
                return 1

            if inParam1 == self.ui.widgets['btn_refresh_season'].reference:

                if self.ui.widgets['btn_automatic_season'].value:
                    self.four_seasons.calculate_season()
                else:
                    self.four_seasons.set_season(self.four_seasons.season)

                return 1

            if inParam1 == self.ui.widgets['btn_apply'].reference:

                try:

                    state_changed = False
                    for radiobutton in self.radiobuttons_saved:
                        # log('check radiobutton', radiobutton['name'])
                        # log('saved value', radiobutton['value'])
                        # log('new value', self.ui.widgets[radiobutton['name']].value)
                        if radiobutton['value'] != self.ui.widgets[radiobutton['name']].value:
                            state_changed = True

                    log('state_changed', state_changed)
                    if state_changed:

                        automatic_season = self.ui.widgets['btn_automatic_season'].value
                        log('automatic_season', automatic_season)
                        self.four_seasons.config.set(
                            'mode', 'automatic_season', '1' if automatic_season else '0')

                        manual_season_value = None
                        if not automatic_season:

                            manual_season_name = [
                                button.tag for button in
                                self.ui.get_widgets_from_group('seasons_checks') if button.value][0]
                            log('manual_season_name', manual_season_name)

                            for season in self.four_seasons.seasons:
                                if season['name'] == manual_season_name:
                                    manual_season_value = season['value']

                            log('manual_season_value', manual_season_value)

                        self.four_seasons.config.set(
                            'mode', 'season', manual_season_value if not automatic_season else '')

                        self.four_seasons.write_config()
                        self.save_control_panel_state()

                        if automatic_season:
                            self.four_seasons.calculate_season()
                        else:
                            self.four_seasons.set_season(manual_season_value)

                except Exception as e:
                    log(e.message)

                return 1

        return 0

    def save_control_panel_state(self):

        # log('save_control_panel_state')
        self.radiobuttons_saved = [
            {'name': button.name, 'value': button.value} for button in self.ui.get_widgets_from_group('seasons_checks')]

    def check_terramax_drefs(self):

        if not self.custom_drefs.exists(DREF_SIG_TERRAMAX_IS_SUMMER):
            for signature in TERRAMAX_DREF_SIGNATURES:
                self.custom_drefs.create_dref(signature, 'int')

    def destroy_terramax_drefs(self):

        for signature in TERRAMAX_DREF_SIGNATURES:
            self.custom_drefs.destroy_dref(signature)

    def reset_terramax_values(self):

        for signature in TERRAMAX_DREF_SIGNATURES:
            self.custom_drefs.set_value(signature, 0)

    def set_terramax_values(self, season):

        self.check_terramax_drefs()
        self.reset_terramax_values()

        log('set_terramax_values season=', season)

        if season in (SEASON_SPRING, SEASON_SUMMER):
            log('activated is_summer')
            self.custom_drefs.set_value(DREF_SIG_TERRAMAX_IS_SUMMER, 1)
        elif season == SEASON_FALL:
            log('activated is_autumn')
            self.custom_drefs.set_value(DREF_SIG_TERRAMAX_IS_AUTUMN, 1)
        elif season in (SEASON_WINTER, SEASON_WINTER_SNOW):
            log('activated is_mid_winter')
            self.custom_drefs.set_value(DREF_SIG_TERRAMAX_IS_MID_WINTER, 1)
        elif season == SEASON_WINTER_DEEP:
            log('activated is_winter')
            self.custom_drefs.set_value(DREF_SIG_TERRAMAX_IS_WINTER, 1)
