import math
from datetime import timedelta as td
from datetime import time

class Event(object):

    def __getitem__(cls, x):
        return getattr(cls, x)

    def __init__(self, attribute_dictionary, json_data, ind):
        
        self.event_id = ind

        for k, v in attribute_dictionary.items():
            setattr(self, k, v)
        self._set_attributes(json_data, ind)

    def __repr__(self):
        return self.__class__.__name__

    def _set_attributes(self, json_data, ind):
        j = json_data[ind]
        # see if there are x and y coordinates anywhere
        attr_dict = {'x_coord': lambda: j['coordinates']['x'],
                     'y_coord': lambda: j['coordinates']['y'],
                     'team': lambda: j['team']['triCode'],
                     'p1_name': lambda: j['players'][0]['player']['fullName'].lower(),
                     'p1_type': lambda: j['players'][0]['playerType'].lower(),
                     'p1_id': lambda: j['players'][0]['player']['id'],
                     'p2_name': lambda: j['players'][1]['player']['fullName'].lower(),
                     'p2_type': lambda: j['players'][1]['playerType'].lower(),
                     'p2_id': lambda: j['players'][1]['player']['id']
                     }

        for k, v in attr_dict.items():
            try:
                setattr(self, k, v())
            # except if attribute is not provided in json
            except (IndexError, KeyError):
                pass


class OffensivePuck(Event):

    def __init__(self, attribute_dictionary, json_data, ind, net):
        super().__init__(attribute_dictionary, json_data, ind)
        self._dist_angle(net)
        if self.event == 'shot':
            self.type = json_data[ind]['result']['secondaryType']

    def _dist_angle(self, net_positions):
        
        try:
            if str(self.team)+str(self.period) in net_positions.keys():
                tkey = self.team+str(self.period)
                x_dist = net_positions[tkey] - self.x_coord
                y_dist = self.y_coord
    
                # set distance and angle of a shot
                self.distance = round(math.hypot(y_dist, x_dist), 5)
                self.angle = round(math.degrees(math.asin(y_dist /
                                                          self.distance)), 5)
            else:
                self.distance = float('nan')
                self.angle = float('nan')
                
        except AttributeError:
            # more warnings
            self.distance = float('nan')
            self.angle = float('nan')

class DefensivePuck(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class FaceOff(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Stoppage(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)
        self.event = json_data[ind]['result']['description'].lower()
        self._set_specific(json_data, ind)

    def _set_specific(self, json_data, ind):
        if self.event == "goalie stopped":
            try:
                '''try to pull player data from the stoppage play'''
                p = json_data[ind-1]['players'][1]
                self.p1_name = p['player']['fullName'].lower()
                self.p1_type = p['playerType'].lower()
                self.p1_id = p['player']['id']
            except (KeyError, IndexError):
                pass


class PuckTransfer(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Hit(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Penalty(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)
        self.type = json_data[ind]['result']['secondaryType'].lower()
        length = td(minutes=int(json_data[ind]['result']['penaltyMinutes']))
        self.length_seconds = length.total_seconds()
        self.end_time = self.time + self.length_seconds
        
class Injury(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)


class Challenge(Event):

    def __init__(self, attribute_dictionary, json_data, ind):
        super().__init__(attribute_dictionary, json_data, ind)
