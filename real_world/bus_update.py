# -*- coding: utf-8 -*-
"""
Created on Wed May 22 21:00:03 2024

@author: Administrator
"""

class set_bus:
    def __init__(self, served_line, departure_time, initial_pos, link_ride_time, stop_position):
        self._served_line = served_line # 1-3436, 2-3986
        self._departure_time = departure_time
        self._link_ride_time = link_ride_time # a list
        self._stop_position = stop_position
        self._trajectory = [initial_pos]
        self._boarding_time = 0
        # self._dwell_stop_ID = None
        self._dwell_stop_ID = self._stop_position.index(initial_pos)
        self._action_activated = 0
        self._current_state = [None, None, None, None]
        self._next_state = [None, None, None, None]
        self._action = None
        self._reward = None
        self._hold_duration = 0
        self._action_start_step = None
        self._reward = None
        self._onboard_passengers = {}
        self._restart = 0
        self._speed = None
        self._action_start_step = -100

        

    def _get_speed(self, current_pos):
        for i in range(len(self._stop_position)-1):
            if current_pos > self._stop_position[i] and current_pos < self._stop_position[i+1]:
                speed = (self._stop_position[i+1] - self._stop_position[i]) / self._link_ride_time[i]
                break
            elif current_pos == self._stop_position[i]:
                speed = (self._stop_position[i+1] - self._stop_position[i]) / self._link_ride_time[i]
                break
            else: # at last stop
                speed = 5
                i += 1
                
        return speed, i
    
    def _trajectory_update(self, current_step, boarding_time):
        if current_step < self._departure_time:
                self._trajectory.append(0)
        else:
            self._speed, previous_stop_index = self._get_speed(round(self._trajectory[-1],2))
            # if round(self._trajectory[-1],2) < self._stop_position[previous_stop_index+1] and round(self._trajectory[-1],2) > self._stop_position[previous_stop_index]:
            if round(self._trajectory[-1],2) not in self._stop_position:
                self._trajectory.append(self._trajectory[-1] + self._speed)
            else:
                if boarding_time == 0:
                    self._trajectory.append(self._trajectory[-1] + self._speed)
                else:
                    self._trajectory.append(self._trajectory[-1])
                    
                    
class set_stop:
    def __init__(self, served_line, stop_pos, shared_stop_ID):
        self._served_line = served_line # 0-both, 1-3436, 2-3986
        self._stop_pos = stop_pos
        self._last_boarding_step = 0
        #self._last_boarding_step_common = 0
        self._boarding_time_record = []
        self._unable_board_passengers = {}
        self._shared_stop_ID = shared_stop_ID

    def _get_boarding_time(self, current_step, bus_served_line, bus_stop_ID, passengers_stop, common_passengers, common_passengers_save, onboard_passengers):
        boarding_passengers_stop = {}
        common_boarding_passengers_stop = {}
        boarding_passengers_stop.update(self._unable_board_passengers)
        self._unable_board_passengers = {}
        # Determine boarding passengers
        for item, details in passengers_stop[bus_stop_ID].items():
            if self._last_boarding_step < details[0] <= current_step:
                details[2] = current_step
                boarding_passengers_stop[item] = details
        if bus_stop_ID in self._shared_stop_ID:
            shared_stop_index = self._shared_stop_ID.index(bus_stop_ID)
            #common_passengers_get_board = []
            for item, details in common_passengers[shared_stop_index].items():
                if self._last_boarding_step < details[0][0] <= current_step:
                    details[bus_served_line-1][2] = current_step
                    boarding_passengers_stop[item] = details[bus_served_line-1]
                    common_boarding_passengers_stop[item] = details[bus_served_line-1]
                    #passengers_stop[bus_stop_ID][item] = details[bus_served_line-1]
                    #common_passengers_save[shared_stop_index][item] = [details[bus_served_line-1], bus_served_line]
                    #common_passengers_get_board.append(item)
            #for name in common_passengers_get_board:
                #del common_passengers[shared_stop_index][name]

            
        # Determine alighting passengers
        delete_list = {}
        for item, details in onboard_passengers.items():
            if details[1] == bus_stop_ID:
                details[3] = current_step
                delete_list[item] = details

        self._num_alighting_passengers_bus0 = len(delete_list)

        # Remove alighting passengers from onboard passengers
        for item in delete_list:
            onboard_passengers.pop(item)
            
        if len(onboard_passengers) + len(boarding_passengers_stop) <= 120:
            # Add boarding passengers to onboard passengers
            onboard_passengers.update(boarding_passengers_stop)
        else:
            #print('capacity warning:', len(onboard_passengers), '+', len(boarding_passengers_stop), '=', len(onboard_passengers) +len(boarding_passengers_stop))
            availability = 120 - len(onboard_passengers)
            # Convert dictionary items to a list
            items = list(boarding_passengers_stop.items())
            # Get the last n items
            last_n_items = items[-availability:]
            # Remove the last n items from the source dictionary
            for key, _ in last_n_items:
                del boarding_passengers_stop[key]
            # Update self._unable_board_passengers with the last n items
            self._unable_board_passengers.update(last_n_items)
        
        if bus_stop_ID in self._shared_stop_ID:
            for item, detials in common_boarding_passengers_stop.items():
                if item in boarding_passengers_stop:
                    passengers_stop[bus_stop_ID][item] = detials
                    common_passengers_save[shared_stop_index][item] = [detials, bus_served_line]
                    del common_passengers[shared_stop_index][item]

        self._last_boarding_step = current_step
        self._num_boarding_passengers_bus0 = len(boarding_passengers_stop)
        boarding_time = int(max(3 * self._num_boarding_passengers_bus0, 1.8 * self._num_alighting_passengers_bus0))  # boarding time 3 s/pax, alighting time 1.8 s/pax
        self._boarding_time_record.append([current_step, boarding_time])

        return boarding_time
