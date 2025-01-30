#import traci
import numpy as np
import random
import timeit
import os
import copy
import tensorflow as tf
import math


class Simulation:
    def __init__(self, Model, Memory, Reward_function, sumo_cmd, gamma, max_steps, green_duration, yellow_duration, num_states, num_actions, training_epochs):
        self._Model = Model
        self._Memory = Memory
        self._reward_function = Reward_function
        #self._TrafficGen = TrafficGen
        self._gamma = gamma
        self._step = 0
        self._sumo_cmd = sumo_cmd
        self._max_steps = max_steps
        self._green_duration = green_duration
        self._yellow_duration = yellow_duration
        self._num_states = num_states
        self._num_actions = num_actions
        self._reward_store_1 = []


        
        self._cumulative_wait_store_1 = []

        
        
        self._training_epochs = training_epochs
        
        #下面的一串都是为了可视化
        
        #self._reward_1_store = [[] for i in range(300)]
 
        
        self._current_total_wait_1_store = [[] for i in range(300)]

        
       
        self._action_store_bus0 = [[] for i in range(300)]
        self._action_store_bus1 = [[] for i in range(300)]
        self._action_store_bus2 = [[] for i in range(300)]
        self._action_store_bus3 = [[] for i in range(300)]
        self._action_store_bus4 = [[] for i in range(300)]
        self._action_store_bus5 = [[] for i in range(300)]
        
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


    def run(self, episode, epsilon):
        """
        Runs an episode of simulation, then starts a training session
        """
        start_time = timeit.default_timer()

        # first, generate the route file for this simulation and set up sumo
        seed=episode #种子=回合数，保证每回合的随机数不一样
        np.random.seed(seed)
        
        #traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits 初始化各个参数
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
                    action_bus0 = self._choose_action_1(current_state_bus0, epsilon)
                    #print(action_bus0)
                    action_activated_bus0 = 1
                    if hold_duration_bus0 >= 18: # max holding time is 180s, which is 36 action steps
                        action_bus0 = 1   
                        action_activated_bus0 = 0
                    else:
                        self._action_store_bus0[episode].append(['bus0',self._step, bus_stop_ID_bus0, action_bus0])
                        
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
                        action_bus1 = self._choose_action_1(current_state_bus1, epsilon)
                        #print(action_bus1)
                        action_activated_bus1 = 1
                        if hold_duration_bus1 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus1 = 1   
                            action_activated_bus1 = 0
                        else:
                            self._action_store_bus1[episode].append(['bus1',self._step, bus_stop_ID_bus1, action_bus1])
                            
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
                        action_bus2 = self._choose_action_1(current_state_bus2, epsilon)
                        #print(action_bus2)
                        action_activated_bus2 = 1
                        if hold_duration_bus2 >=18: # max holding time is 180s, which is 36 action steps
                            action_bus2 = 1   
                            action_activated_bus2 = 0
                        else:
                            self._action_store_bus2[episode].append(['bus2',self._step, bus_stop_ID_bus2, action_bus2])
                            
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
                        action_bus3 = self._choose_action_1(current_state_bus3, epsilon)
                        #print(action_bus3)
                        action_activated_bus3 = 1
                        if hold_duration_bus3 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus3 = 1   
                            action_activated_bus3 = 0
                        else:
                            self._action_store_bus3[episode].append(['bus3',self._step, bus_stop_ID_bus3, action_bus3])
                            
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
                        action_bus4 = self._choose_action_1(current_state_bus4, epsilon)
                        #print(action_bus4)
                        action_activated_bus4 = 1
                        if hold_duration_bus4 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus4 = 1   
                            action_activated_bus4 = 0
                        else:
                            self._action_store_bus4[episode].append(['bus4',self._step, bus_stop_ID_bus4, action_bus4])
                            
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
                        action_bus5 = self._choose_action_1(current_state_bus5, epsilon)
                        #print(action_bus5)
                        action_activated_bus5 = 1
                        if hold_duration_bus5 >= 18: # max holding time is 180s, which is 36 action steps
                            action_bus5 = 1   
                            action_activated_bus5 = 0
                        else:
                            self._action_store_bus5[episode].append(['bus5',self._step, bus_stop_ID_bus5, action_bus5])
                            
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
                self._Memory.add_sample_1((current_state_bus0, action_bus0, reward_bus0, next_state_bus0))
                self._trajectories_for_LLM.append(['bus0', action_start_step_bus0, bus_stop_ID_bus0, current_state_bus0, action_bus0, reward_bus0, next_state_bus0])
                #self._reward_1_store[episode].append(reward_bus0)
                self._sum_reward_1 += reward_bus0
            
            if self._step == action_start_step_bus1 + 5:
                next_state_bus1 = self._get_state_bus1()
                reward_bus1 = self._reward_function.reward_function(current_state_bus1, action_bus1, next_state_bus1)
                self._Memory.add_sample_1((current_state_bus1, action_bus1, reward_bus1, next_state_bus1))
                self._trajectories_for_LLM.append(['bus1', action_start_step_bus1, bus_stop_ID_bus1, current_state_bus1, action_bus1, reward_bus1, next_state_bus1])
                #self._reward_1_store[episode].append(reward_bus1)
                self._sum_reward_1 += reward_bus1
            
            if self._step == action_start_step_bus2 + 5:
                next_state_bus2 = self._get_state_bus2()
                reward_bus2 = self._reward_function.reward_function(current_state_bus2, action_bus2, next_state_bus2)
                self._Memory.add_sample_1((current_state_bus2, action_bus2, reward_bus2, next_state_bus2))
                self._trajectories_for_LLM.append(['bus2', action_start_step_bus2, bus_stop_ID_bus2, current_state_bus2, action_bus2, reward_bus2, next_state_bus2])
                #self._reward_1_store[episode].append(reward_bus2)
                self._sum_reward_1 += reward_bus2
                
            if self._step == action_start_step_bus3 + 5:
                next_state_bus3 = self._get_state_bus3()
                reward_bus3 = self._reward_function.reward_function(current_state_bus3, action_bus3, next_state_bus3)
                self._Memory.add_sample_1((current_state_bus3, action_bus3, reward_bus3, next_state_bus3))
                self._trajectories_for_LLM.append(['bus3', action_start_step_bus3, bus_stop_ID_bus3, current_state_bus3, action_bus3, reward_bus3, next_state_bus3])
                #self._reward_1_store[episode].append(reward_bus3)
                self._sum_reward_1 += reward_bus3
                
            if self._step == action_start_step_bus4 + 5:
                next_state_bus4 = self._get_state_bus4()
                reward_bus4 = self._reward_function.reward_function(current_state_bus4, action_bus4, next_state_bus4)
                self._Memory.add_sample_1((current_state_bus4, action_bus4, reward_bus4, next_state_bus4))
                self._trajectories_for_LLM.append(['bus4', action_start_step_bus4, bus_stop_ID_bus4, current_state_bus4, action_bus4, reward_bus4, next_state_bus4])
                #self._reward_1_store[episode].append(reward_bus4)
                self._sum_reward_1 += reward_bus4
                
            if self._step == action_start_step_bus5 + 5:
                next_state_bus5 = self._get_state_bus5()
                reward_bus5 = self._reward_function.reward_function(current_state_bus5, action_bus5, next_state_bus5)
                self._Memory.add_sample_1((current_state_bus5, action_bus5, reward_bus5, next_state_bus5))
                self._trajectories_for_LLM.append(['bus5', action_start_step_bus5, bus_stop_ID_bus5, current_state_bus5, action_bus5, reward_bus5, next_state_bus5])
                #self._reward_1_store[episode].append(reward_bus5)
                self._sum_reward_1 += reward_bus5
            

        self._save_episode_stats_1()

        
        #traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        print("Training...")
        start_time = timeit.default_timer()
        for train_epoch in range(self._training_epochs):
            '''
            if train_epoch%100==0:
                #self._target_Q_net_1 = tf.keras.models.clone_model_with_weights(self._Model._model_1)
                self._target_Q_net_1 = tf.keras.models.clone_model(self._Model._model_1)
                self._target_Q_net_1.set_weights(self._Model._model_1.get_weights())
            '''
            self._replay()
        training_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time, training_time

    '''
    def _reward_function(self, current_state, action, next_state):
        
        Thoughts:
        To refine the reward function for the bus holding control problem, several key changes are proposed:
        1. Introduce a balanced approach to penalize high variability in time headways, directly addressing the task's objective to balance the headways.
        2. More directly incentivize reductions in passenger waiting times, as this directly impacts passenger satisfaction and system efficiency.
        3. Include a comprehensive system efficiency metric that considers headway balancing, passenger travel time, and waiting time.
        4. Implement dynamic reward scaling based on performance metrics to ensure that improvements in critical areas are adequately incentivized.
        5. Introduce penalties for actions that do not lead to headway improvement or reduction in passenger times, promoting more effective strategy exploration.
        These modifications aim to guide the RL agent toward more efficient bus system performance by balancing headways, reducing waiting and travel times, and improving overall reliability.
        
        # (initial the reward)
        reward = 0
    
        # (import packages and define helper functions)
        import numpy as np
    
        # Helper function to calculate headway difference
        def calculate_headway_difference(forward_headway, backward_headway):
            return np.abs(forward_headway - backward_headway)
    
        # Helper function to calculate the efficiency metric
        def system_efficiency_metric(headway_difference, passenger_waiting_time, on_board_time):
            # Combines headway balance, waiting time, and travel time into a single metric
            return headway_difference + passenger_waiting_time + on_board_time
    
        # Calculate the headway difference for the current and next states
        current_headway_difference = calculate_headway_difference(current_state[0], current_state[1])
        next_headway_difference = calculate_headway_difference(next_state[0], next_state[1])
    
        # Penalize high variability in time headways
        reward -= next_headway_difference * 1.5
    
        # Reward reductions in passenger waiting time and on-board time
        waiting_time_reduction = current_state[3] - next_state[3]
        on_board_time_reduction = current_state[2] - next_state[2]
        reward += (waiting_time_reduction + on_board_time_reduction) * 2
    
        # Calculate system efficiency metric for the next state
        next_system_efficiency = system_efficiency_metric(next_headway_difference, next_state[3], next_state[2])
        # Incentivize improvements in system efficiency
        reward -= next_system_efficiency
    
        # Dynamic reward scaling based on current performance metrics
        if next_system_efficiency > 100:  # Threshold for scaling
            reward *= 1.2  # Scale up rewards for improving underperforming areas
    
        # Penalize repeated ineffective actions
        if action == 0 and next_headway_difference >= current_headway_difference:
            reward -= 5  # Penalize holding when it doesn't contribute to headway improvement
    
        # Encourage releasing the bus if it helps to balance headways more effectively
        if action == 1 and current_state[0] > current_state[1] * 1.5:
            reward += 10
    
        # Regularize reward to stabilize training
        reward = np.clip(reward, -10, 10)
    
        return reward
    '''
    
    def _choose_action_1(self, state, epsilon):
        """
        Decide wheter to perform an explorative or exploitative action, according to an epsilon-greedy policy
        """
        if random.random() < epsilon:
            return random.randint(0, self._num_actions - 1) # random action
        else:
            return np.argmax(self._Model.predict_one_1(state)) # the best action given the current state

    
    
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



    def _replay(self):
        """
        Retrieve a group of samples from the memory and for each of them update the learning equation, then train
        """
        batch_1 = self._Memory.get_samples_1(self._Model.batch_size)
        #DQN
        
        if len(batch_1) > 0:  # if the memory is full enough
            states_1 = np.array([val[0] for val in batch_1])  # extract states from the batch
            next_states_1 = np.array([val[3] for val in batch_1])  # extract next states from the batch
            #val[0]-old_state栏，val[3]-current_state栏（？）

            # prediction
            q_s_a_1 = self._Model.predict_batch_1(states_1)  # predict Q(state), for every sample
            q_s_a_d_1 = self._Model.predict_batch_1(next_states_1)  # predict Q(next_state), for every sample

            # setup training arrays
            x_1 = np.zeros((len(batch_1), self._num_states))
            y_1 = np.zeros((len(batch_1), self._num_actions))

            for i, b in enumerate(batch_1):
                state_1, action_1, reward_1, _ = b[0], b[1], b[2], b[3]  # extract data from one sample
                current_q_1 = q_s_a_1[i]  # get the Q(state) predicted before
                current_q_1[action_1] = reward_1 + self._gamma * np.amax(q_s_a_d_1[i])  # update Q(state, action)
                x_1[i] = state_1
                y_1[i] = current_q_1  # Q(state) that includes the updated action value
                #似乎明白了些什么，普通的qlearning就是把state和current_q值列表列出来，
                #deep q network就是用已有的数据对，搞了个拟合，因此成为连续的了

            self._Model.train_batch_1(x_1, y_1)  # train the NN
        '''
        #DDQN
        if len(batch_1) > 0:  # if the memory is full enough
            states_1 = np.array([val[0] for val in batch_1])  # extract states from the batch
            next_states_1 = np.array([val[3] for val in batch_1])  # extract next states from the batch
            #val[0]-old_state栏，val[3]-current_state栏（？）

            # prediction
            q_s_a_1 = self._Model.predict_batch_1(states_1)  # predict Q(state), for every sample
            q_s_a_d_1 = self._Model.predict_batch_1(next_states_1)  # predict Q(next_state), for every sample
            target_q_s_a_d_1 = self._target_Q_net_1.predict(next_states_1,verbose=0)
            
            #print("target Q", "\n", target_q_s_a_d_1)
            #print("updated Q", "\n", q_s_a_d_1)
            
            # setup training arrays
            x_1 = np.zeros((len(batch_1), self._num_states))
            y_1 = np.zeros((len(batch_1), self._num_actions))

            for i, b in enumerate(batch_1):
                state_1, action_1, reward_1, _ = b[0], b[1], b[2], b[3]  # extract data from one sample
                current_q_1 = q_s_a_1[i]  # get the Q(state) predicted before
                #current_q_1[action_1] = reward_1 + self._gamma * np.amax(q_s_a_d_1[i])  # update Q(state, action)
                max_action_1 = np.argmax(q_s_a_d_1[i])
                current_q_1[action_1] = reward_1 + self._gamma * target_q_s_a_d_1[i][max_action_1]  # update Q(state, action)
                x_1[i] = state_1
                y_1[i] = current_q_1  # Q(state) that includes the updated action value
                #似乎明白了些什么，普通的qlearning就是把state和current_q值列表列出来，
                #deep q network就是用已有的数据对，搞了个拟合，因此成为连续的了

            self._Model.train_batch_1(x_1, y_1)  # train the NN
        '''


    def _save_episode_stats_1(self):
        """
        Save the stats of the episode to plot the graphs at the end of the session
        """
        self._reward_store_1.append(self._sum_reward_1)
    