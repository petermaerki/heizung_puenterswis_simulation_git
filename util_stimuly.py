DAY_S = 24 * 3600.0


"""
        self.warmwasserbedarf_haus_W = 255
        self.heizbedarf_haus_W = 5000
"""


class StimuliWintertag:
    def __init__(self):
        self.umgebungstemperatur_C = -10.0
        self.start_s = -2 * DAY_S
        self.duration_s = 5 * DAY_S
        self.timestep_s = 5 * 60.0

    def do_plot(self, time_s) -> bool:
        return True
        # return time_s > 0


class StimuliFruehlingstag:
    def __init__(self):
        self.umgebungstemperatur_C = 15.0
        self.start_s = -2 * DAY_S
        self.duration_s = 5 * DAY_S
        self.timestep_s = 5 * 60.0

    def do_plot(self, time_s) -> bool:
        return True
        # return time_s > 0


class StimuliSommertag:
    def __init__(self):
        self.umgebungstemperatur_C = 25.0
        self.start_s = -2 * DAY_S
        self.duration_s = 5 * DAY_S
        self.timestep_s = 5 * 60.0

    def do_plot(self, time_s) -> bool:
        return True
        # return time_s > 0
