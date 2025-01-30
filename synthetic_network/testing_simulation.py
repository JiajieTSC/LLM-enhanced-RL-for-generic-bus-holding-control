import traci
import numpy as np
import random
import timeit
import os



class Simulation:
    def __init__(self, Model, Reward_function, max_steps, green_duration, yellow_duration, num_states, num_actions):
        self._Model = Model
        self._reward_function = Reward_function
        #self._TrafficGen = TrafficGen
        self._step = 0
        #self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._num_states = num_states
        self._num_actions = num_actions
        self._reward_episode_1 = []
                                                                                                                                                                                                                                                           
        self._action_store_bus0 = []
        self._action_store_bus1 = []
        self._action_store_bus2 = []
        self._action_store_bus3 = []
        self._action_store_bus4 = []
        self._action_store_bus5 = []
        
    def _passener_arriving_time(self):

        # Set the arrival rates for each hour
        aveg_lambda = np.random.randint(40, 180)
        lambda_ = [int(aveg_lambda*0.6), int(aveg_lambda*0.8), int(aveg_lambda*1.2), int(aveg_lambda*0.5)]  # average rate of arrivals per hour for each of the 4 hours
        
        arrival_times = []
        
        for i in range(4):  # for each hour
            # Generate inter-arrival times until the cumulative sum exceeds 1 hour
            inter_arrival_times = []
            while np.sum(inter_arrival_times) < 1:
                inter_arrival_time = np.random.exponential(1/lambda_[i])
                inter_arrival_times.append(inter_arrival_time)
            
            # Calculate arrival times for this hour and add to the list
            arrival_times_hour = np.cumsum(inter_arrival_times) + i  # add i to shift the times to the correct hour
            arrival_times.extend(arrival_times_hour)
        
        # Remove times that exceed 4 hours
        arrival_times = [int(t*3600) for t in arrival_times if t < 4]
        
        return arrival_times

    def run(self, episode):
        """
        Runs the testing simulation
        """
        start_time = timeit.default_timer()

        # first, generate the route file for this simulation and set up sumo
        seed=episode
        np.random.seed(seed)
        
        #traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits
        self._step = 0
        
        self._sum_reward_1 = 0
        
        self._trajectory_bus0 = [0] #line1
        self._trajectory_bus1 = [0] #line2
        self._trajectory_bus2 = [0] #line1
        self._trajectory_bus3 = [0] #line2
        self._trajectory_bus4 = [0] #line1
        self._trajectory_bus5 = [0] #line2
        
        self._boarding_time_record_bus0 = []
        self._boarding_time_record_bus1 = []
        self._boarding_time_record_bus2 = []
        self._boarding_time_record_bus3 = []
        self._boarding_time_record_bus4 = []
        self._boarding_time_record_bus5 = []

        max_hold_0 = 0
        max_hold_1 = 0
        max_hold_2 = 0
        max_hold_3 = 0
        max_hold_4 = 0
        max_hold_5 = 0
        
        boarding_time_bus0 = 0
        boarding_time_bus1 = 0
        boarding_time_bus2 = 0
        boarding_time_bus3 = 0
        boarding_time_bus4 = 0
        boarding_time_bus5 = 0
        
        stops_list = [666,1998,3330,4662,5994,7326,8658,9990]
        self._loop_length = 10656
        bus_speed = 5.55 # m/s
        
        action_activated_bus0 = 0
        action_activated_bus1 = 0
        action_activated_bus2 = 0
        action_activated_bus3 = 0
        action_activated_bus4 = 0
        action_activated_bus5 = 0

        action_start_step_bus0 = -10
        action_start_step_bus1 = -10
        action_start_step_bus2 = -10
        action_start_step_bus3 = -10
        action_start_step_bus4 = -10
        action_start_step_bus5 = -10
        
        hold_duration_bus0 = 0
        hold_duration_bus1 = 0
        hold_duration_bus2 = 0
        hold_duration_bus3 = 0
        hold_duration_bus4 = 0
        hold_duration_bus5 = 0
        
        bus_depart_interval = 320
        
        self._passengers_stop = [{},{},{},{},{},{},{},{}]
        
        arriving_time_stop0 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop0)):
            passenger_ID = 'pas_stop0_%s'%(i)
            self._passengers_stop[0][passenger_ID] = [arriving_time_stop0[i], np.random.choice([1,2,3,4,5,6,7]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]

        arriving_time_stop1 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop1)):
            passenger_ID = 'pas_stop1_%s'%(i)
            self._passengers_stop[1][passenger_ID] = [arriving_time_stop1[i], np.random.choice([0,2,3,4,5,6,7]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]

        arriving_time_stop2 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop2)):
            passenger_ID = 'pas_stop2_%s'%(i)
            self._passengers_stop[2][passenger_ID] = [arriving_time_stop2[i], np.random.choice([0,1,3,4,5,6,7]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]

        arriving_time_stop3 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop3)):
            passenger_ID = 'pas_stop3_%s'%(i)
            self._passengers_stop[3][passenger_ID] = [arriving_time_stop3[i], np.random.choice([0,1,2,4,5,6,7]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]

        arriving_time_stop4 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop4)):
            passenger_ID = 'pas_stop4_%s'%(i)
            self._passengers_stop[4][passenger_ID] = [arriving_time_stop4[i], np.random.choice([0,1,2,3,5,6,7]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]

        arriving_time_stop5 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop5)):
            passenger_ID = 'pas_stop5_%s'%(i)
            self._passengers_stop[5][passenger_ID] = [arriving_time_stop5[i], np.random.choice([0,1,2,3,4,6,7]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]

        arriving_time_stop6 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop6)):
            passenger_ID = 'pas_stop6_%s'%(i)
            self._passengers_stop[6][passenger_ID] = [arriving_time_stop6[i], np.random.choice([0,1,2,3,4,5,7]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]
        
        arriving_time_stop7 = self._passener_arriving_time()
        for i in range(len(arriving_time_stop7)):
            passenger_ID = 'pas_stop7_%s'%(i)
            self._passengers_stop[7][passenger_ID] = [arriving_time_stop7[i], np.random.choice([0,1,2,3,4,5,6]), -1, -1] #[arriving time, destination stop index, boarding time, alighting time]
        
        self._onboard_passengers_bus0 = {}
        self._onboard_passengers_bus1 = {}
        self._onboard_passengers_bus2 = {}
        self._onboard_passengers_bus3 = {}
        self._onboard_passengers_bus4 = {}
        self._onboard_passengers_bus5 = {}
        
        #boarding_passengers_stop = [{}, {}, {}, {}, {}, {}, {}, {}]        
        
        last_boarding_step = [0,0,0,0,0,0,0,0]
        
        self._trajectories_for_LLM = []
        
        while self._step < self._max_steps:

            boarding_passengers_stop = [{}, {}, {}, {}, {}, {}, {}, {}]
            # bus0
            if self._trajectory_bus0[-1] not in stops_list:
                next_pos_bus0 = round(self._trajectory_bus0[-1] + bus_speed,2)
                if next_pos_bus0 > self._loop_length:
                    next_pos_bus0 = next_pos_bus0 - self._loop_length
                self._trajectory_bus0.append(next_pos_bus0)
            elif self._trajectory_bus0[-1] in stops_list and boarding_time_bus0==0:
                # get bording passengers
                bus_stop_ID_bus0 = stops_list.index(self._trajectory_bus0[-1])
                for item in self._passengers_stop[bus_stop_ID_bus0]:
                    #print(self._passengers_stop[bus_stop_ID_bus0][item][0])
                    if self._passengers_stop[bus_stop_ID_bus0][item][0] > last_boarding_step[bus_stop_ID_bus0] and self._passengers_stop[bus_stop_ID_bus0][item][0] <= self._step:
                        self._passengers_stop[bus_stop_ID_bus0][item][2] = self._step
                        boarding_passengers_stop[bus_stop_ID_bus0][item]=self._passengers_stop[bus_stop_ID_bus0][item]
                
                # delete alighting passengers from onboard passengers
                delete_list_bus0 = {}
                for item in self._onboard_passengers_bus0:
                    if self._onboard_passengers_bus0[item][1] == bus_stop_ID_bus0:
                        self._onboard_passengers_bus0[item][3] = self._step
                        delete_list_bus0[item] = self._onboard_passengers_bus0[item]
                        
                for item in delete_list_bus0:
                    self._onboard_passengers_bus0.pop(item)
                        
                for item in boarding_passengers_stop[bus_stop_ID_bus0]:
                    self._onboard_passengers_bus0[item]=boarding_passengers_stop[bus_stop_ID_bus0][item]    
                    
                last_boarding_step[bus_stop_ID_bus0]=self._step
                
                self._num_boarding_passengers_bus0 = len(boarding_passengers_stop[bus_stop_ID_bus0])
                boarding_time_bus0 = 3 * self._num_boarding_passengers_bus0 # bording time 3 s/pax
                self._boarding_time_record_bus0.append([self._step, bus_stop_ID_bus0, boarding_time_bus0])
                self._trajectory_bus0.append(self._trajectory_bus0[-1])
            else:
                boarding_time_bus0 -= 1
                if boarding_time_bus0 > 0:
                    self._trajectory_bus0.append(self._trajectory_bus0[-1])
                else:
                    #select action
                    current_state_bus0 = self._get_state_bus0()   # record the current state
                    action_bus0 = self._choose_action_1(current_state_bus0)
                    #print(action_bus0)
                    action_activated_bus0 = 1
                    if hold_duration_bus0 >= 18: # max holding time is 180s, which is 36 action steps
                        action_bus0 = 1   
                        action_activated_bus0 = 0
                    else:
                        self._action_store_bus0.append(['bus0',self._step, bus_stop_ID_bus0, action_bus0])
                        
                    if action_bus0 == 0: # 0-hold, 1-not hold
                        boarding_time_bus0 += 5
                        self._trajectory_bus0.append(self._trajectory_bus0[-1])
                        hold_duration_bus0 += 1
                    else:
                        self._trajectory_bus0.append(round(self._trajectory_bus0[-1]+bus_speed,2))
                        hold_duration_bus0 = 0
            
            boarding_passengers_stop = [{}, {}, {}, {}, {}, {}, {}, {}]
            # bus1
            if self._step <= bus_depart_interval:
                self._trajectory_bus1.append(0)
            else:
                if self._trajectory_bus1[-1] not in stops_list:
                    next_pos_bus1 = round(self._trajectory_bus1[-1] + bus_speed,2)
                    if next_pos_bus1 > self._loop_length:
                        next_pos_bus1 = next_pos_bus1 - self._loop_length
                    self._trajectory_bus1.append(next_pos_bus1)
                elif self._trajectory_bus1[-1] in stops_list and boarding_time_bus1==0:
                    # get bording passengers
                    bus_stop_ID_bus1 = stops_list.index(self._trajectory_bus1[-1])
                    for item in self._passengers_stop[bus_stop_ID_bus1]:
                        #print(self._passengers_stop[bus_stop_ID_bus1][item][0])
                        if self._passengers_stop[bus_stop_ID_bus1][item][0] > last_boarding_step[bus_stop_ID_bus1] and self._passengers_stop[bus_stop_ID_bus1][item][0] <= self._step:
                            self._passengers_stop[bus_stop_ID_bus1][item][2] = self._step
                            boarding_passengers_stop[bus_stop_ID_bus1][item]=self._passengers_stop[bus_stop_ID_bus1][item]
                    
                    # delete alighting passengers from onboard passengers
                    delete_list_bus1 = {}
                    for item in self._onboard_passengers_bus1:
                        if self._onboard_passengers_bus1[item][1] == bus_stop_ID_bus1:
                            self._onboard_passengers_bus1[item][3] = self._step
                            delete_list_bus1[item] = self._onboard_passengers_bus1[item]
                            
                    for item in delete_list_bus1:
                        self._onboard_passengers_bus1.pop(item)
                            
                    for item in boarding_passengers_stop[bus_stop_ID_bus1]:
                        self._onboard_passengers_bus1[item]=boarding_passengers_stop[bus_stop_ID_bus1][item]    
                        
                    last_boarding_step[bus_stop_ID_bus1]=self._step
                    
                    self._num_boarding_passengers_bus1 = len(boarding_passengers_stop[bus_stop_ID_bus1])
                    boarding_time_bus1 = 3 * self._num_boarding_passengers_bus1 # bording time 3 s/pax
                    self._boarding_time_record_bus1.append([self._step, bus_stop_ID_bus1, boarding_time_bus1])
                    self._trajectory_bus1.append(self._trajectory_bus1[-1])
                else:
                    boarding_time_bus1 -= 1
                    if boarding_time_bus1 > 0:
                        self._trajectory_bus1.append(self._trajectory_bus1[-1])
                    else:
                        #select action
                        current_state_bus1 = self._get_state_bus1()   # record the current state
                        action_bus1 = self._choose_action_1(current_state_bus1)
                        #print(action_bus1)
                        action_activated_bus1 = 1
                        if hold_duration_bus1 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus1 = 1   
                            action_activated_bus1 = 0
                        else:
                            self._action_store_bus1.append(['bus1',self._step, bus_stop_ID_bus1, action_bus1])
                            
                        if action_bus1 == 0: # 0-hold, 1-not hold
                            boarding_time_bus1 += 5
                            self._trajectory_bus1.append(self._trajectory_bus1[-1])
                            hold_duration_bus1 += 1
                        else:
                            self._trajectory_bus1.append(round(self._trajectory_bus1[-1]+bus_speed,2))
                            hold_duration_bus1 = 0
                        
            boarding_passengers_stop = [{}, {}, {}, {}, {}, {}, {}, {}]
            # bus2          
            if self._step <= bus_depart_interval*2:
                self._trajectory_bus2.append(0)
            else:
                if self._trajectory_bus2[-1] not in stops_list:
                    next_pos_bus2 = round(self._trajectory_bus2[-1] + bus_speed,2)
                    if next_pos_bus2 > self._loop_length:
                        next_pos_bus2 = next_pos_bus2 - self._loop_length
                    self._trajectory_bus2.append(next_pos_bus2)
                elif self._trajectory_bus2[-1] in stops_list and boarding_time_bus2==0:
                    # get bording passengers
                    bus_stop_ID_bus2 = stops_list.index(self._trajectory_bus2[-1])
                    for item in self._passengers_stop[bus_stop_ID_bus2]:
                        #print(self._passengers_stop[bus_stop_ID_bus2][item][0])
                        if self._passengers_stop[bus_stop_ID_bus2][item][0] > last_boarding_step[bus_stop_ID_bus2] and self._passengers_stop[bus_stop_ID_bus2][item][0] <= self._step:
                            self._passengers_stop[bus_stop_ID_bus2][item][2] = self._step
                            boarding_passengers_stop[bus_stop_ID_bus2][item]=self._passengers_stop[bus_stop_ID_bus2][item]
                    
                    # delete alighting passengers from onboard passengers
                    delete_list_bus2 = {}
                    for item in self._onboard_passengers_bus2:
                        if self._onboard_passengers_bus2[item][1] == bus_stop_ID_bus2:
                            self._onboard_passengers_bus2[item][3] = self._step
                            delete_list_bus2[item] = self._onboard_passengers_bus2[item]
                            
                    for item in delete_list_bus2:
                        self._onboard_passengers_bus2.pop(item)
                            
                    for item in boarding_passengers_stop[bus_stop_ID_bus2]:
                        self._onboard_passengers_bus2[item]=boarding_passengers_stop[bus_stop_ID_bus2][item]    
                        
                    last_boarding_step[bus_stop_ID_bus2]=self._step
                    
                    self._num_boarding_passengers_bus2 = len(boarding_passengers_stop[bus_stop_ID_bus2])
                    boarding_time_bus2 = 3 * self._num_boarding_passengers_bus2 # bording time 3 s/pax
                    self._boarding_time_record_bus2.append([self._step, bus_stop_ID_bus2, boarding_time_bus2])
                    self._trajectory_bus2.append(self._trajectory_bus2[-1])
                else:
                    boarding_time_bus2 -= 1
                    if boarding_time_bus2 > 0:
                        self._trajectory_bus2.append(self._trajectory_bus2[-1])
                    else:
                        #select action
                        current_state_bus2 = self._get_state_bus2()   # record the current state
                        action_bus2 = self._choose_action_1(current_state_bus2)
                        #print(action_bus2)
                        action_activated_bus2 = 1
                        if hold_duration_bus2 >=18: # max holding time is 180s, which is 36 action steps
                            action_bus2 = 1   
                            action_activated_bus2 = 0
                        else:
                            self._action_store_bus2.append(['bus2',self._step, bus_stop_ID_bus2, action_bus2])
                            
                        if action_bus2 == 0: # 0-hold, 1-not hold
                            boarding_time_bus2 += 5
                            self._trajectory_bus2.append(self._trajectory_bus2[-1])
                            hold_duration_bus2 += 1
                        else:
                            self._trajectory_bus2.append(round(self._trajectory_bus2[-1]+bus_speed,2))
                            hold_duration_bus2 = 0
                            
            boarding_passengers_stop = [{}, {}, {}, {}, {}, {}, {}, {}]
            # bus3
            if self._step <= bus_depart_interval*3:
                self._trajectory_bus3.append(0)
            else:
                if self._trajectory_bus3[-1] not in stops_list:
                    next_pos_bus3 = round(self._trajectory_bus3[-1] + bus_speed,2)
                    if next_pos_bus3 > self._loop_length:
                        next_pos_bus3 = next_pos_bus3 - self._loop_length
                    self._trajectory_bus3.append(next_pos_bus3)
                elif self._trajectory_bus3[-1] in stops_list and boarding_time_bus3==0:
                    # get bording passengers
                    bus_stop_ID_bus3 = stops_list.index(self._trajectory_bus3[-1])
                    for item in self._passengers_stop[bus_stop_ID_bus3]:
                        #print(self._passengers_stop[bus_stop_ID_bus3][item][0])
                        if self._passengers_stop[bus_stop_ID_bus3][item][0] > last_boarding_step[bus_stop_ID_bus3] and self._passengers_stop[bus_stop_ID_bus3][item][0] <= self._step:
                            self._passengers_stop[bus_stop_ID_bus3][item][2] = self._step
                            boarding_passengers_stop[bus_stop_ID_bus3][item]=self._passengers_stop[bus_stop_ID_bus3][item]
                    
                    # delete alighting passengers from onboard passengers
                    delete_list_bus3 = {}
                    for item in self._onboard_passengers_bus3:
                        if self._onboard_passengers_bus3[item][1] == bus_stop_ID_bus3:
                            self._onboard_passengers_bus3[item][3] = self._step
                            delete_list_bus3[item] = self._onboard_passengers_bus3[item]
                            
                    for item in delete_list_bus3:
                        self._onboard_passengers_bus3.pop(item)
                            
                    for item in boarding_passengers_stop[bus_stop_ID_bus3]:
                        self._onboard_passengers_bus3[item]=boarding_passengers_stop[bus_stop_ID_bus3][item]    
                        
                    last_boarding_step[bus_stop_ID_bus3]=self._step
                    
                    self._num_boarding_passengers_bus3 = len(boarding_passengers_stop[bus_stop_ID_bus3])
                    boarding_time_bus3 = 3 * self._num_boarding_passengers_bus3 # bording time 3 s/pax
                    self._boarding_time_record_bus3.append([self._step, bus_stop_ID_bus3, boarding_time_bus3])
                    self._trajectory_bus3.append(self._trajectory_bus3[-1])
                else:
                    boarding_time_bus3 -= 1
                    if boarding_time_bus3 > 0:
                        self._trajectory_bus3.append(self._trajectory_bus3[-1])
                    else:
                        #select action
                        current_state_bus3 = self._get_state_bus3()   # record the current state
                        action_bus3 = self._choose_action_1(current_state_bus3)
                        #print(action_bus3)
                        action_activated_bus3 = 1
                        if hold_duration_bus3 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus3 = 1   
                            action_activated_bus3 = 0
                        else:
                            self._action_store_bus3.append(['bus3',self._step, bus_stop_ID_bus3, action_bus3])
                            
                        if action_bus3 == 0: # 0-hold, 1-not hold
                            boarding_time_bus3 += 5
                            self._trajectory_bus3.append(self._trajectory_bus3[-1])
                            hold_duration_bus3 += 1
                        else:
                            self._trajectory_bus3.append(round(self._trajectory_bus3[-1]+bus_speed,2))
                            hold_duration_bus3 = 0
                            
            boarding_passengers_stop = [{}, {}, {}, {}, {}, {}, {}, {}]
            # bus4
            if self._step <= bus_depart_interval*4:
                self._trajectory_bus4.append(0)
            else:
                if self._trajectory_bus4[-1] not in stops_list:
                    next_pos_bus4 = round(self._trajectory_bus4[-1] + bus_speed,2)
                    if next_pos_bus4 > self._loop_length:
                        next_pos_bus4 = next_pos_bus4 - self._loop_length
                    self._trajectory_bus4.append(next_pos_bus4)
                elif self._trajectory_bus4[-1] in stops_list and boarding_time_bus4==0:
                    # get bording passengers
                    bus_stop_ID_bus4 = stops_list.index(self._trajectory_bus4[-1])
                    for item in self._passengers_stop[bus_stop_ID_bus4]:
                        #print(self._passengers_stop[bus_stop_ID_bus4][item][0])
                        if self._passengers_stop[bus_stop_ID_bus4][item][0] > last_boarding_step[bus_stop_ID_bus4] and self._passengers_stop[bus_stop_ID_bus4][item][0] <= self._step:
                            self._passengers_stop[bus_stop_ID_bus4][item][2] = self._step
                            boarding_passengers_stop[bus_stop_ID_bus4][item]=self._passengers_stop[bus_stop_ID_bus4][item]
                    
                    # delete alighting passengers from onboard passengers
                    delete_list_bus4 = {}
                    for item in self._onboard_passengers_bus4:
                        if self._onboard_passengers_bus4[item][1] == bus_stop_ID_bus4:
                            self._onboard_passengers_bus4[item][3] = self._step
                            delete_list_bus4[item] = self._onboard_passengers_bus4[item]
                            
                    for item in delete_list_bus4:
                        self._onboard_passengers_bus4.pop(item)
                            
                    for item in boarding_passengers_stop[bus_stop_ID_bus4]:
                        self._onboard_passengers_bus4[item]=boarding_passengers_stop[bus_stop_ID_bus4][item]    
                        
                    last_boarding_step[bus_stop_ID_bus4]=self._step
                    
                    self._num_boarding_passengers_bus4 = len(boarding_passengers_stop[bus_stop_ID_bus4])
                    boarding_time_bus4 = 3 * self._num_boarding_passengers_bus4 # bording time 3 s/pax
                    self._boarding_time_record_bus4.append([self._step, bus_stop_ID_bus4, boarding_time_bus4])
                    self._trajectory_bus4.append(self._trajectory_bus4[-1])
                else:
                    boarding_time_bus4 -= 1
                    if boarding_time_bus4 > 0:
                        self._trajectory_bus4.append(self._trajectory_bus4[-1])
                    else:
                        #select action
                        current_state_bus4 = self._get_state_bus4()   # record the current state
                        action_bus4 = self._choose_action_1(current_state_bus4)
                        #print(action_bus4)
                        action_activated_bus4 = 1
                        if hold_duration_bus4 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus4 = 1   
                            action_activated_bus4 = 0
                        else:
                            self._action_store_bus4.append(['bus4',self._step, bus_stop_ID_bus4, action_bus4])
                            
                        if action_bus4 == 0: # 0-hold, 1-not hold
                            boarding_time_bus4 += 5
                            self._trajectory_bus4.append(self._trajectory_bus4[-1])
                            hold_duration_bus4 += 1
                        else:
                            self._trajectory_bus4.append(round(self._trajectory_bus4[-1]+bus_speed,2))
                            hold_duration_bus4 = 0
                            
            boarding_passengers_stop = [{}, {}, {}, {}, {}, {}, {}, {}]
            # bus5
            if self._step <= bus_depart_interval*5:
                self._trajectory_bus5.append(0)
            else:
                if self._trajectory_bus5[-1] not in stops_list:
                    next_pos_bus5 = round(self._trajectory_bus5[-1] + bus_speed,2)
                    if next_pos_bus5 > self._loop_length:
                        next_pos_bus5 = next_pos_bus5 - self._loop_length
                    self._trajectory_bus5.append(next_pos_bus5)
                elif self._trajectory_bus5[-1] in stops_list and boarding_time_bus5==0:
                    # get bording passengers
                    bus_stop_ID_bus5 = stops_list.index(self._trajectory_bus5[-1])
                    for item in self._passengers_stop[bus_stop_ID_bus5]:
                        #print(self._passengers_stop[bus_stop_ID_bus5][item][0])
                        if self._passengers_stop[bus_stop_ID_bus5][item][0] > last_boarding_step[bus_stop_ID_bus5] and self._passengers_stop[bus_stop_ID_bus5][item][0] <= self._step:
                            self._passengers_stop[bus_stop_ID_bus5][item][2] = self._step
                            boarding_passengers_stop[bus_stop_ID_bus5][item]=self._passengers_stop[bus_stop_ID_bus5][item]
                    
                    # delete alighting passengers from onboard passengers
                    delete_list_bus5 = {}
                    for item in self._onboard_passengers_bus5:
                        if self._onboard_passengers_bus5[item][1] == bus_stop_ID_bus5:
                            self._onboard_passengers_bus5[item][3] = self._step
                            delete_list_bus5[item] = self._onboard_passengers_bus5[item]
                            
                    for item in delete_list_bus5:
                        self._onboard_passengers_bus5.pop(item)
                            
                    for item in boarding_passengers_stop[bus_stop_ID_bus5]:
                        self._onboard_passengers_bus5[item]=boarding_passengers_stop[bus_stop_ID_bus5][item]    
                        
                    last_boarding_step[bus_stop_ID_bus5]=self._step
                    
                    self._num_boarding_passengers_bus5 = len(boarding_passengers_stop[bus_stop_ID_bus5])
                    boarding_time_bus5 = 3 * self._num_boarding_passengers_bus5 # bording time 3 s/pax
                    self._boarding_time_record_bus5.append([self._step, bus_stop_ID_bus5, boarding_time_bus5])
                    self._trajectory_bus5.append(self._trajectory_bus5[-1])
                else:
                    boarding_time_bus5 -= 1
                    if boarding_time_bus5 > 0:
                        self._trajectory_bus5.append(self._trajectory_bus5[-1])
                    else:
                        #select action
                        current_state_bus5 = self._get_state_bus5()   # record the current state
                        action_bus5 = self._choose_action_1(current_state_bus5)
                        #print(action_bus5)
                        action_activated_bus5 = 1
                        if hold_duration_bus5 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus5 = 1   
                            action_activated_bus5 = 0
                        else:
                            self._action_store_bus5.append(['bus5',self._step, bus_stop_ID_bus5, action_bus5])
                            
                        if action_bus5 == 0: # 0-hold, 1-not hold
                            boarding_time_bus5 += 5
                            self._trajectory_bus5.append(self._trajectory_bus5[-1])
                            hold_duration_bus5 += 1
                        else:
                            self._trajectory_bus5.append(round(self._trajectory_bus5[-1]+bus_speed,2))
                            hold_duration_bus5 = 0
                            

            # check if the next state needs to be recorded
            if action_activated_bus0 == 1:
                action_start_step_bus0 = self._step
                action_activated_bus0 = 0
                
            if action_activated_bus1 == 1:
                action_start_step_bus1 = self._step
                action_activated_bus1 = 0
                
            if action_activated_bus2 == 1:
                action_start_step_bus2 = self._step
                action_activated_bus2 = 0
            
            if action_activated_bus3 == 1:
                action_start_step_bus3 = self._step
                action_activated_bus3 = 0
            
            if action_activated_bus4 == 1:
                action_start_step_bus4 = self._step
                action_activated_bus4 = 0
                
            if action_activated_bus5 == 1:
                action_start_step_bus5 = self._step
                action_activated_bus5 = 0
                
            self._step += 1 # the position of step update is critical. it must be between the action_start record to the next state record detect 
            
            if self._step == action_start_step_bus0 + 5:
                next_state_bus0 = self._get_state_bus0()
                reward_bus0 = self._reward_function.reward_function(current_state_bus0, action_bus0, next_state_bus0)
                #reward_bus0 = self._reward_function(current_state_bus0, action_bus0, next_state_bus0)
                #self._Memory.add_sample_1((current_state_bus0, action_bus0, reward_bus0, next_state_bus0))
                self._trajectories_for_LLM.append(['bus0', action_start_step_bus0, bus_stop_ID_bus0, current_state_bus0, action_bus0, reward_bus0, next_state_bus0])
                #self._reward_1_store[episode].append(reward_bus0)
                self._sum_reward_1 += reward_bus0
            
            if self._step == action_start_step_bus1 + 5:
                next_state_bus1 = self._get_state_bus1()
                reward_bus1 = self._reward_function.reward_function(current_state_bus1, action_bus1, next_state_bus1)
                #self._Memory.add_sample_1((current_state_bus1, action_bus1, reward_bus1, next_state_bus1))
                self._trajectories_for_LLM.append(['bus1', action_start_step_bus1, bus_stop_ID_bus1, current_state_bus1, action_bus1, reward_bus1, next_state_bus1])
                #self._reward_1_store[episode].append(reward_bus1)
                self._sum_reward_1 += reward_bus1
            
            if self._step == action_start_step_bus2 + 5:
                next_state_bus2 = self._get_state_bus2()
                reward_bus2 = self._reward_function.reward_function(current_state_bus2, action_bus2, next_state_bus2)
                #self._Memory.add_sample_1((current_state_bus2, action_bus2, reward_bus2, next_state_bus2))
                self._trajectories_for_LLM.append(['bus2', action_start_step_bus2, bus_stop_ID_bus2, current_state_bus2, action_bus2, reward_bus2, next_state_bus2])
                #self._reward_1_store[episode].append(reward_bus2)
                self._sum_reward_1 += reward_bus2
                
            if self._step == action_start_step_bus3 + 5:
                next_state_bus3 = self._get_state_bus3()
                reward_bus3 = self._reward_function.reward_function(current_state_bus3, action_bus3, next_state_bus3)
                #self._Memory.add_sample_1((current_state_bus3, action_bus3, reward_bus3, next_state_bus3))
                self._trajectories_for_LLM.append(['bus3', action_start_step_bus3, bus_stop_ID_bus3, current_state_bus3, action_bus3, reward_bus3, next_state_bus3])
                #self._reward_1_store[episode].append(reward_bus3)
                self._sum_reward_1 += reward_bus3
                
            if self._step == action_start_step_bus4 + 5:
                next_state_bus4 = self._get_state_bus4()
                reward_bus4 = self._reward_function.reward_function(current_state_bus4, action_bus4, next_state_bus4)
                #self._Memory.add_sample_1((current_state_bus4, action_bus4, reward_bus4, next_state_bus4))
                self._trajectories_for_LLM.append(['bus4', action_start_step_bus4, bus_stop_ID_bus4, current_state_bus4, action_bus4, reward_bus4, next_state_bus4])
                #self._reward_1_store[episode].append(reward_bus4)
                self._sum_reward_1 += reward_bus4
                
            if self._step == action_start_step_bus5 + 5:
                next_state_bus5 = self._get_state_bus5()
                reward_bus5 = self._reward_function.reward_function(current_state_bus5, action_bus5, next_state_bus5)
                #self._Memory.add_sample_1((current_state_bus5, action_bus5, reward_bus5, next_state_bus5))
                self._trajectories_for_LLM.append(['bus5', action_start_step_bus5, bus_stop_ID_bus5, current_state_bus5, action_bus5, reward_bus5, next_state_bus5])
                #self._reward_1_store[episode].append(reward_bus5)
                self._sum_reward_1 += reward_bus5
        #print("Total reward:", np.sum(self._reward_episode))
        #traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time
    
    '''
    def _reward_function(self, current_state, action, next_state):
        
        Thoughts:
        To improve the bus holding control problem, the reward function needs to:
        1. More heavily penalize deviations from the desired headway to encourage balancing.
        2. Penalize passenger waiting time to reduce it.
        3. Reward actions that decrease overall journey time for passengers.
        4. Introduce dynamic holding penalties based on passenger count and waiting time.
        5. Adjust rewards based on system state to encourage efficient actions.
        6. Implement a better exploration strategy during training.
        7. Regularize rewards to stabilize training.
        8. Ensure simulation fidelity reflects real-world conditions.
        
    
        # (initial the reward)
        reward = 0
    
        # (import packages and define helper functions)
        import numpy as np
    
        # Helper function to calculate headway difference
        def calculate_headway_difference(forward_headway, backward_headway):
            return np.abs(forward_headway - backward_headway)
    
        # Helper function to calculate passenger waiting time penalty
        def calculate_waiting_penalty(boarding_passengers):
            # Assuming a fixed boarding time per passenger
            boarding_time = 3.0 * boarding_passengers
            # Penalty proportional to the boarding time
            return boarding_time
    
        # Calculate the headway difference for the current and next states
        current_headway_difference = calculate_headway_difference(current_state[0], current_state[1])
        next_headway_difference = calculate_headway_difference(next_state[0], next_state[1])
    
        # Calculate the waiting penalty for the next state
        next_waiting_penalty = calculate_waiting_penalty(next_state[3])
    
        # Update the reward based on the headway difference
        # More heavily penalize the increase in headway difference
        reward -= (next_headway_difference - current_headway_difference) * 2
    
        # Update the reward based on the waiting penalty
        # Penalize the increase in waiting time
        reward -= next_waiting_penalty
    
        # Reward for reducing the number of onboard passengers (indicating successful drop-offs)
        reward += (current_state[2] - next_state[2]) * 2
    
        # Dynamic holding penalty: penalize holding action if there are many boarding passengers
        if action == 0:
            reward -= next_state[3] * 0.5
    
        # Encourage releasing the bus if the forward headway is much larger than the backward headway
        if action == 1 and current_state[0] > current_state[1] * 1.5:
            reward += 5
    
        # Regularize reward to prevent large fluctuations
        reward = np.clip(reward, -10, 10)

        return reward
    '''

    def _choose_action_1(self, state):
        """
        Pick the best action known based on the current state of the env
        """
        return np.argmax(self._Model.predict_one_1(state))
    

    def _get_state_bus0(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        # forward and backward headway between buses in the same line
        if self._trajectory_bus5[-1] >= self._trajectory_bus0[-1]:
            state[0]=self._trajectory_bus5[-1]-self._trajectory_bus0[-1]
        else:
            state[0]=self._trajectory_bus5[-1] + self._loop_length - self._trajectory_bus0[-1]
            
        if self._trajectory_bus1[-1] <= self._trajectory_bus0[-1]:
            state[1]=self._trajectory_bus0[-1]-self._trajectory_bus1[-1]
        else:
            state[1]=self._trajectory_bus0[-1] + self._loop_length - self._trajectory_bus1[-1]
        # forward and backward headway between buses in the different lines
        state[2]=len(self._onboard_passengers_bus0)
        #state[3]=self._num_boarding_passengers_bus0
        
        return state
    
    def _get_state_bus1(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        # forward and backward headway between buses in the same line
        if self._trajectory_bus0[-1] >= self._trajectory_bus1[-1]:
            state[0]=self._trajectory_bus0[-1]-self._trajectory_bus1[-1]
        else:
            state[0]=self._trajectory_bus0[-1] + self._loop_length - self._trajectory_bus1[-1]
            
        if self._trajectory_bus2[-1] <= self._trajectory_bus1[-1]:
            state[1]=self._trajectory_bus1[-1]-self._trajectory_bus2[-1]
        else:
            state[1]=self._trajectory_bus1[-1] + self._loop_length - self._trajectory_bus2[-1]
        # forward and backward headway between buses in the different lines
        state[2]=len(self._onboard_passengers_bus1)
        #state[3]=self._num_boarding_passengers_bus1
        
        return state
    
    def _get_state_bus2(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        # forward and backward headway between buses in the same line
        if self._trajectory_bus1[-1] >= self._trajectory_bus2[-1]:
            state[0]=self._trajectory_bus1[-1]-self._trajectory_bus2[-1]
        else:
            state[0]=self._trajectory_bus1[-1] + self._loop_length - self._trajectory_bus2[-1]
            
        if self._trajectory_bus3[-1] <= self._trajectory_bus2[-1]:
            state[1]=self._trajectory_bus2[-1]-self._trajectory_bus3[-1]
        else:
            state[1]=self._trajectory_bus2[-1] + self._loop_length - self._trajectory_bus3[-1]
        # forward and backward headway between buses in the different lines
        state[2]=len(self._onboard_passengers_bus2)
        #state[3]=self._num_boarding_passengers_bus2
        
        return state
    
    def _get_state_bus3(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        # forward and backward headway between buses in the same line
        if self._trajectory_bus2[-1] >= self._trajectory_bus3[-1]:
            state[0]=self._trajectory_bus2[-1]-self._trajectory_bus3[-1]
        else:
            state[0]=self._trajectory_bus2[-1] + self._loop_length - self._trajectory_bus3[-1]
            
        if self._trajectory_bus4[-1] <= self._trajectory_bus3[-1]:
            state[1]=self._trajectory_bus3[-1]-self._trajectory_bus4[-1]
        else:
            state[1]=self._trajectory_bus3[-1] + self._loop_length - self._trajectory_bus4[-1]
        # forward and backward headway between buses in the different lines
        state[2]=len(self._onboard_passengers_bus3)
        #state[3]=self._num_boarding_passengers_bus3
        
        return state
    
    def _get_state_bus4(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        # forward and backward headway between buses in the same line
        if self._trajectory_bus3[-1] >= self._trajectory_bus4[-1]:
            state[0]=self._trajectory_bus3[-1]-self._trajectory_bus4[-1]
        else:
            state[0]=self._trajectory_bus3[-1] + self._loop_length - self._trajectory_bus4[-1]
            
        if self._trajectory_bus5[-1] <= self._trajectory_bus4[-1]:
            state[1]=self._trajectory_bus4[-1]-self._trajectory_bus5[-1]
        else:
            state[1]=self._trajectory_bus4[-1] + self._loop_length - self._trajectory_bus5[-1]
        # forward and backward headway between buses in the different lines
        state[2]=len(self._onboard_passengers_bus4)
        #state[3]=self._num_boarding_passengers_bus4
        
        return state
    
    def _get_state_bus5(self):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        # forward and backward headway between buses in the same line
        if self._trajectory_bus4[-1] >= self._trajectory_bus5[-1]:
            state[0]=self._trajectory_bus4[-1]-self._trajectory_bus5[-1]
        else:
            state[0]=self._trajectory_bus4[-1] + self._loop_length - self._trajectory_bus5[-1]
            
        if self._trajectory_bus0[-1] <= self._trajectory_bus5[-1]:
            state[1]=self._trajectory_bus5[-1]-self._trajectory_bus0[-1]
        else:
            state[1]=self._trajectory_bus5[-1] + self._loop_length - self._trajectory_bus0[-1]
        # forward and backward headway between buses in the different lines
        state[2]=len(self._onboard_passengers_bus5)
        #state[3]=self._num_boarding_passengers_bus5
        
        return state
