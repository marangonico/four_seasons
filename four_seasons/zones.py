from math import radians, sqrt, sin, cos, atan2

from globals import *
from xp_utils import log

HEMISPHERE_NORTH = 1
HEMISPHERE_SOUTH = 2

EARTH_R = 6372.8

DOYS_RANGE = {
    'jan': range(1, 32),
    'feb': range(32, 60),
    'mar': range(60, 91),
    'apr': range(91, 121),
    'may': range(121, 152),
    'jun': range(152, 182),
    'jul': range(182, 213),
    'ago': range(213, 244),
    'sep': range(244, 274),
    'oct': range(274, 305),
    'nov': range(305, 335),
    'dec': range(335, 366),
}


def geocalc(lat1, lon1, lat2, lon2):

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    dlon = lon1 - lon2
    y = sqrt(
        (cos(lat2) * sin(dlon)) ** 2
        + (cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)) ** 2
        )
    x = sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(dlon)
    c = atan2(y, x)
    return EARTH_R * c


class Period(object):

    name = ''
    doys_range = ()
    season = None
    snow_coverage_distance = 0

    def __init__(self, name, season, snow_coverage_distance=0, doys_range=None):
        self.name = name
        self.season = season
        self.snow_coverage_distance = snow_coverage_distance

        if doys_range:
            self.doys_range = doys_range
        else:
            # assuming name == month
            self.doys_range = DOYS_RANGE[name]


class Zone(object):

    name = ''

    lat1 = None
    lon1 = None
    lat2 = None
    lon2 = None

    hemisphere = None

    def __init__(self, name, lat1, lon1, lat2, lon2):

        self.name = name
        self.lat1 = int(lat1)
        self.lon1 = int(lon1)
        self.lat2 = int(lat2)
        self.lon2 = int(lon2)

        assert self.lat1 <= self.lat2
        assert self.lon1 <= self.lon2

        self.hemisphere = HEMISPHERE_NORTH if lat1 >= 0 else HEMISPHERE_SOUTH

    def is_within(self, lat, lon):
        # log('zone.is_within() lat={} lon={}'.format(lat, lon))
        #
        if '{}'.format(lat) == 'nan':
            return None
        return int(lat) in range(self.lat1, self.lat2 + 1) and int(lon) in range(self.lon1, self.lon2 + 1)

    def get_season(self, doy, lat, lon, temperature, precipitation=False):
        """"""

    def __repr__(self):
        return '{} ({},{} to {},{})'.format(self.name, self.lat1, self.lon1, self.lat2, self.lon2)


class ZoneTropical(Zone):

    def get_season(self, doy, lat, lon, temperature, precipitation=False):
        return SEASON_SUMMER


class ZonePolar(Zone):

    def get_season(self, doy, lat, lon, temperature, precipitation=False):
        return SEASON_WINTER


class ZoneTemperate(Zone):

    periods = {}
    reference_pole_lat = 0
    reference_pole_lon = 0

    def get_season(self, doy, lat, lon, temperature, precipitation=False):

        try:

            log('zone', self.name)
            log('doy', doy)
            for period in self.periods:
                # log('checking period', period.name)
                # log('period doys range', period.doys_range)
                if doy in period.doys_range:
                    season = period.season

                    log('month', period.name)
                    log('temperature', temperature)
                    log('precipitation', precipitation)

                    if geocalc(
                            self.reference_pole_lat, self.reference_pole_lon, lat, lon) < period.snow_coverage_distance:

                        if temperature <= 0:
                            log('within snow coverage. threshold={}, dist={}'.format(
                                period.snow_coverage_distance,
                                geocalc(self.reference_pole_lat, self.reference_pole_lon, lat, lon)))

                            season = SEASON_WINTER

                    if season == SEASON_WINTER:
                        if temperature < -10:
                            log('applying winter deep')
                            season = SEASON_WINTER_DEEP
                        elif temperature <= 0:
                            if precipitation:
                                log('snow precipitation')
                                season = SEASON_WINTER_SNOW

                    return season

        except Exception as e:
            log(e.message)

        log('no period!!')


class ZoneTemperateNorth(ZoneTemperate):

    reference_pole_lat = 90
    reference_pole_lon = 0

    def __init__(self, name, lat1, lon1, lat2, lon2):

        self.periods = [
            Period('jan', SEASON_WINTER, 5600),
            Period('feb', SEASON_WINTER, 5400),
            Period('mar', SEASON_SPRING, 5200),
            Period('apr', SEASON_SPRING, 4800),
            Period('may', SEASON_SPRING, 4400),
            Period('jun', SEASON_SUMMER, 2300),
            Period('jul', SEASON_SUMMER, 1800),
            Period('ago', SEASON_SUMMER, 1200),
            Period('sep', SEASON_FALL, 2000),
            Period('oct', SEASON_FALL, 3200),
            Period('nov', SEASON_FALL, 4800),
            Period('dec', SEASON_WINTER, 5400),
        ]

        super(ZoneTemperateNorth, self).__init__(name, lat1, lon1, lat2, lon2)


class ZoneTemperateSouth(ZoneTemperate):

    reference_pole_lat = -90
    reference_pole_lon = 0

    def __init__(self, name, lat1, lon1, lat2, lon2):

        self.periods = [
            Period('jul', SEASON_WINTER, 0),
            Period('ago', SEASON_WINTER, 0),
            Period('sep', SEASON_SPRING, 0),
            Period('oct', SEASON_SPRING, 0),
            Period('nov', SEASON_SPRING, 0),
            Period('dec', SEASON_SUMMER, 0),
            Period('jan', SEASON_SUMMER, 0),
            Period('feb', SEASON_SUMMER, 0),
            Period('mar', SEASON_FALL, 0),
            Period('apr', SEASON_FALL, 0),
            Period('may', SEASON_FALL, 0),
            Period('jun', SEASON_WINTER, 0),
        ]

        super(ZoneTemperateSouth, self).__init__(name, lat1, lon1, lat2, lon2)


class ZoneTemperatePatagonia(ZoneTemperate):

    reference_pole_lat = -90
    reference_pole_lon = 0

    def __init__(self, name, lat1, lon1, lat2, lon2):

        self.periods = [
            Period('jul', SEASON_WINTER, 5300),
            Period('ago', SEASON_WINTER, 4500),
            Period('sep', SEASON_SPRING, 0),
            Period('oct', SEASON_SPRING, 0),
            Period('nov', SEASON_SPRING, 0),
            Period('dec', SEASON_SUMMER, 0),
            Period('jan', SEASON_SUMMER, 0),
            Period('feb', SEASON_SUMMER, 0),
            Period('mar', SEASON_FALL, 0),
            Period('apr', SEASON_FALL, 0),
            Period('may', SEASON_FALL, 0),
            Period('jun', SEASON_WINTER, 4500),
        ]

        super(ZoneTemperatePatagonia, self).__init__(name, lat1, lon1, lat2, lon2)

