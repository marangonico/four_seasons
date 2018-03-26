from math import floor

from XPLMDefs import *
from XPLMDataAccess import *
from XPLMPlugin import *
from XPLMProcessing import *
from XPLMUtilities import *

class FourSeasons:

	SEASON_SPRING = 0
	SEASON_SUMMER = 10
	SEASON_FALL	= SEASON_AUTUMN = 20
	SEASON_WINTER = 30
	SEASON_DEEP_WINTER = 35
	
	season = None
	season_old = None
	
	local_date_days_dref = None
	local_date_days_value = None

	latitude_dref = None
	latitude_value = None

	longitude_dref = None
	longitude_value = None

	def __init__(self):

		self.local_date_days_dref = XPLMFindDataRef("sim/time/local_date_days")
		self.local_date_days_value = XPLMGetDatai(self.local_date_days_dref)

		self.latitude_dref = XPLMFindDataRef("sim/flightmodel/position/latitude")
		self.latitude_value = int(XPLMGetDatad(self.latitude_dref))

		#self.longitude_dref = XPLMFindDataRef("sim/flightmodel/position/longitude")
		#self.longitude_value = XPLMGetDatai(self.longitude_dref)

		self.season_old = self.season = self.SEASON_SPRING
	
	def get_season(self):
		return self.season

	def set_season(self, new_season=None):
	
		if not new_season:
			return

		self.season_old = self.season
		self.season = new_season

		if self.season != self.season_old:
			command_ref = XPLMFindCommand("sim/operation/reload_scenery")
			XPLMCommandOnce(command_ref)
		
	def calculate_season(self):

		if self.latitude_value >= 45:
			if self.local_date_days_value >= (335) or self.local_date_days_value <= (59):
				self.set_season(self.SEASON_WINTER)	
			elif self.local_date_days_value >= (60) and self.local_date_days_value <= (151):
				self.set_season(self.SEASON_SPRING)	
			elif self.local_date_days_value >= (152) and self.local_date_days_value <= (243):
				self.set_season(self.SEASON_SUMMER)	
			elif self.local_date_days_value >= (244) and self.local_date_days_value <= (334):
				self.set_season(self.SEASON_FALL)			
		else:
			self.set_season(self.SEASON_SUMMER)

	def check_local_date(self):
		
		actual_local_date_days_value = XPLMGetDatai(self.local_date_days_dref)
		if actual_local_date_days_value != self.local_date_days_value:
			self.local_date_days_value = actual_local_date_days_value
			self.calculate_season()

	def check_position(self):
		
		actual_latitude_value = int(XPLMGetDatad(self.latitude_dref))
		if actual_latitude_value != self.latitude_value:
			self.latitude_value = actual_latitude_value
			self.calculate_season()
		
class PythonInterface:

	season_dref = None

	def XPluginStart(self):
		self.Name = "4 Seasons"
		self.Sig  = "nm.four_seasons"
		self.Desc = "A plugin driving season changes"

		self.four_seasons = FourSeasons()
		
		self.season_signature =  "nm/four_seasons/season"
			
		# floop
		self.floopCB = self.floopCallback
		XPLMRegisterFlightLoopCallback(self, self.floopCB, 1, 0)

		# self.season_DataRefEditor_CB = self.season_DataRefEditor_CallBack
		
		self.season_SetValue_CB = self.season_SetValue_CallBack
		self.season_GetValue_CB = self.season_GetValue_CallBack
		
		#self.FlightLoopCB = self.FlightLoopCallback
        
		self.season_dref = XPLMRegisterDataAccessor(
			self,
			self.season_signature,    #inDataName 
			xplmType_Int,             #inDataType
			1,                        #inIsWritable
			self.season_GetValue_CB, #inReadInt
			self.season_SetValue_CB, #inWriteInt
			None, #inReadFloat
			None, #inWriteFloat
			None, #inReadDouble
			None, #inWriteDouble
			None, #inReadIntArray
			None, #inWriteIntArray
			None, #inReadFloatArray
			None, #inWriteFloatArray
			None, #inReadData
			None, #inWriteData
			None, #inReadRefcon
			None, #inWriteRefcon
		)
        
		self.season_dref = XPLMFindDataRef(self.season_signature)
		
		#XPLMRegisterFlightLoopCallback(self, self.season_DataRefEditor_CB, 1, 0)

	
		return self.Name, self.Sig, self.Desc

	def floopCallback(self, elapsedMe, elapsedSim, counter, refcon):
						
		MSG_ADD_DATAREF = 0x01000000
		plugin_id = XPLMFindPluginBySignature("xplanesdk.examples.DataRefEditor")
		if (plugin_id != XPLM_NO_PLUGIN_ID):
			XPLMSendMessageToPlugin(plugin_id, MSG_ADD_DATAREF, self.season_signature)

		self.four_seasons.check_local_date()
		self.four_seasons.check_position()
			
	def XPluginStop(self):
		XPLMUnregisterDataAccessor(self, self.season_dref)
	
	def XPluginEnable(self):
		return 1
	
	def XPluginDisable(self):
		""""""
	
	def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
		if inMessage == XPLM_MSG_SCENERY_LOADED or inMessage == XPLM_MSG_AIRPORT_LOADED:
			self.four_seasons.check_local_date()
			self.four_seasons.check_position()
			# self.four_seasons.calculate_season()

	def season_GetValue_CallBack(self, inRefcon):
		#return int(self.four_seasons.latitude_value)
		return self.four_seasons.get_season()
		
	def season_SetValue_CallBack(self, inRefcon, inValue):
		self.four_seasons.set_season(inValue)
		

