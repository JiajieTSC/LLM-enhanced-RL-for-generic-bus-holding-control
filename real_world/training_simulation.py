import numpy as np
import random
import timeit
import os
import copy
import tensorflow as tf
import math
from bus_update import set_bus, set_stop
import pickle


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
          
    def _passener_arriving_time(self, aveg_lambda):

        # Set the arrival rates for each hour
        lambda_ = aveg_lambda  # average rate of arrivals per hour for each of the 4 hours
        
        arrival_times = []
        
        for i in range(4):  # for each hour
            # Generate inter-arrival times until the cumulative sum exceeds 1 hour
            inter_arrival_times = []
            if lambda_[i] != 0:
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
        seed=episode 
        np.random.seed(seed)
        
        #traci.start(self._sumo_cmd)
        print("Simulating...")

        # inits 
        self._step = 0
        self._sum_reward_1 = 0
        self._trajectories_for_LLM = [] 
        
        # ------------------------------------------
        # -----Info of bus line 3986 (code: 2)------
        # ------------------------------------------
        
        f_read=open('./data/board_bystop_per_hour_3986.pkl','rb')
        board_bystop_per_hour_3986=pickle.load(f_read)
        f_read.close()   
        
        f_read=open('./data/destination_percent_3986.pkl','rb')
        destination_percent_3986=pickle.load(f_read)
        f_read.close()   
        
        self._passengers_stop_3986 = [{} for _ in range(len(board_bystop_per_hour_3986))]
        
        for i in range(len(board_bystop_per_hour_3986)):
            arrive_rates = [np.random.randint(0.9*item, 1.1*item) for item in board_bystop_per_hour_3986[i]]
            arriving_time = self._passener_arriving_time(arrive_rates)
            num_passenger = len(arriving_time)
            if sum(destination_percent_3986[i]) == 0:
                pass
            else:
                destination = np.random.choice(range(len(board_bystop_per_hour_3986)), size=num_passenger, p=destination_percent_3986[i])
                for ii in range(num_passenger):
                    passenger_ID = 'pas_3986_stop%s_%s'%(i,ii)
                    self._passengers_stop_3986[i][passenger_ID] = [arriving_time[ii], destination[ii], -1, -1] #[arriving time, destination stop index, boarding time, alighting time]

        f_read=open('./data/stops_position_direct_distance_3986_1.pkl','rb')
        stop_position_3986=pickle.load(f_read)
        f_read.close()
        
        f_read=open('./data/mid_travel_time_3986.pkl','rb')
        mid_travel_time_3986=pickle.load(f_read)
        f_read.close()
        
        # gamma distribution, theta = mean_value / alpha, mean value is mid_travel_time
        alpha = 50  # chosen shape parameter, larger more centrazlied
        
        self._bus3986 = []
        bus_depart_interval = 300
        num_bus = int(3600*4/bus_depart_interval)
        for i in range(num_bus + 13):
            link_ride_time_3986 = [min(max(int(item * 0.5),int(np.random.gamma(alpha, item/alpha))),int(item * 1.8)) for item in mid_travel_time_3986]
            if i < 14:
                self._bus3986.append(set_bus(2, 0, stop_position_3986[26 - i * 2], link_ride_time_3986, stop_position_3986))
            else:
                self._bus3986.append(set_bus(2, bus_depart_interval * (i - 13), 0, link_ride_time_3986, stop_position_3986))
        
        self._stops_3986 = []
        self._shared_stop_ID_in_3986 = [8, 10, 11, 12, 14, 15, 16, 19]
        for i in range(len(stop_position_3986)):
            if i in self._shared_stop_ID_in_3986:
                self._stops_3986.append(set_stop(0, stop_position_3986[i], self._shared_stop_ID_in_3986))
            else:
                self._stops_3986.append(set_stop(2, stop_position_3986[i], self._shared_stop_ID_in_3986))
            
        # ------------------------------------------
        # -----Info of bus line 3436 (code: 1)------
        # ------------------------------------------

        f_read=open('./data/board_bystop_per_hour_3436.pkl','rb')
        board_bystop_per_hour_3436=pickle.load(f_read)
        f_read.close()   
        
        f_read=open('./data/destination_percent_3436.pkl','rb')
        destination_percent_3436=pickle.load(f_read)
        f_read.close()   
        
        self._passengers_stop_3436 = [{} for _ in range(len(board_bystop_per_hour_3436))]
        
        for i in range(len(board_bystop_per_hour_3436)):
            arrive_rates = [np.random.randint(0.9*item, 1.1*item) for item in board_bystop_per_hour_3436[i]]
            arriving_time = self._passener_arriving_time(arrive_rates)
            num_passenger = len(arriving_time)
            if sum(destination_percent_3436[i]) == 0:
                pass
            else:
                destination = np.random.choice(range(len(board_bystop_per_hour_3436)), size=num_passenger, p=destination_percent_3436[i])
                for ii in range(num_passenger):
                    passenger_ID = 'pas_3436_stop%s_%s'%(i,ii)
                    self._passengers_stop_3436[i][passenger_ID] = [arriving_time[ii], destination[ii], -1, -1] #[arriving time, destination stop index, boarding time, alighting time]
        
        f_read=open('./data/stops_position_direct_distance_3436_1.pkl','rb')
        stop_position_3436=pickle.load(f_read)
        f_read.close()
        
        #stop_position_3436 = [item[1] for item in line_3436_stops_info]
        
        f_read=open('./data/mid_travel_time_3436.pkl','rb')
        mid_travel_time_3436=pickle.load(f_read)
        f_read.close()
        
        # gamma distribution, theta = mean_value / alpha, mean value is mid_travel_time
        alpha = 50  # chosen shape parameter, larger more centrazlied

        
        self._bus3436 = []
        bus_depart_interval = 300
        num_bus = int(3600*4/bus_depart_interval)
        for i in range(num_bus + 13):
            link_ride_time_3436 = [min(max(int(item * 0.5),int(np.random.gamma(alpha, item/alpha))),int(item * 1.8)) for item in mid_travel_time_3436]
            if i < 14:
                self._bus3436.append(set_bus(1, 0, stop_position_3436[26 - i * 2], link_ride_time_3436, stop_position_3436))
            else:
                self._bus3436.append(set_bus(1, bus_depart_interval * (i - 13), 0, link_ride_time_3436, stop_position_3436))
        
        self._stops_3436 = []
        self._shared_stop_ID_in_3436 = [11, 13, 14, 15, 16, 17, 18, 20]
        for i in range(len(stop_position_3436)):
            if i in self._shared_stop_ID_in_3436:
                self._stops_3436.append(set_stop(0, stop_position_3436[i], self._shared_stop_ID_in_3436))
            else:
                self._stops_3436.append(set_stop(1, stop_position_3436[i], self._shared_stop_ID_in_3436))
        
        # ---------------------------------------------------
        # ----- extract passengers can take both lines ------
        # ---------------------------------------------------
        
        self._common_passengers_save = [{} for _ in range(len(self._shared_stop_ID_in_3436))]
        self._common_passengers = [{} for _ in range(len(self._shared_stop_ID_in_3436))]
        for index in range(len(self._shared_stop_ID_in_3436)):
            delete_passengers = []
            for passenger_ID, detial in self._passengers_stop_3436[self._shared_stop_ID_in_3436[index]].items():
                if detial[1] in self._shared_stop_ID_in_3436:
                    self._common_passengers[index][passenger_ID] = [detial, [detial[0], self._shared_stop_ID_in_3986[self._shared_stop_ID_in_3436.index(detial[1])], -1, -1]]
                    delete_passengers.append(passenger_ID)
            for name in delete_passengers:
                del self._passengers_stop_3436[self._shared_stop_ID_in_3436[index]][name]
        
        for index in range(len(self._shared_stop_ID_in_3986)):
            delete_passengers = []
            for passenger_ID, detial in self._passengers_stop_3986[self._shared_stop_ID_in_3986[index]].items():
                if detial[1] in self._shared_stop_ID_in_3986:
                    self._common_passengers[index][passenger_ID] = [detial, [detial[0], self._shared_stop_ID_in_3436[self._shared_stop_ID_in_3986.index(detial[1])], -1, -1]]
                    delete_passengers.append(passenger_ID)
            for name in delete_passengers:
                del self._passengers_stop_3986[self._shared_stop_ID_in_3986[index]][name]
        
        # ---------------------------------------------------
        # -------------- Start the simulation ---------------
        # ---------------------------------------------------
        
        while self._step < self._max_steps:
            for bus0 in self._bus3986:
                # bus0
                if self._step < bus0._departure_time:
                    bus0._trajectory_update(self._step, bus0._boarding_time)
                else:
                    if round(bus0._trajectory[-1],2) <= bus0._stop_position[-1]:
                        #print(round(bus0._trajectory[-1],2))
                        if round(bus0._trajectory[-1],2) not in bus0._stop_position:
                            bus0._trajectory_update(self._step, bus0._boarding_time)
                        elif round(bus0._trajectory[-1],2) in bus0._stop_position and bus0._boarding_time == 0:
                            if bus0._restart == 1:
                                bus0._trajectory_update(self._step, bus0._boarding_time)
                                bus0._restart = 0
                            else:
                                # calculate the boarding time
                                bus0._dwell_stop_ID = bus0._stop_position.index(round(bus0._trajectory[-1],2))
                                bus0._boarding_time = self._stops_3986[bus0._dwell_stop_ID]._get_boarding_time(self._step, bus0._served_line, bus0._dwell_stop_ID, self._passengers_stop_3986, self._common_passengers, self._common_passengers_save, bus0._onboard_passengers)
                                if bus0._boarding_time == 0:
                                    bus0._boarding_time = 1
                                bus0._trajectory_update(self._step, bus0._boarding_time)
                        else:
                            bus0._trajectory_update(self._step, bus0._boarding_time)
                
                
                if bus0._boarding_time > 0:
                    bus0._boarding_time -= 1
                    if bus0._boarding_time == 0:
                        #select action
                        if bus0._dwell_stop_ID == len(stop_position_3986) - 1:
                            bus0._action = 1
                        else:
                            bus0._current_state = self._get_state_bus0(bus0, self._bus3986, self._bus3436, self._stops_3986[bus0._dwell_stop_ID]._served_line)   # record the current state
                            bus0._action = self._choose_action_1(bus0._current_state, epsilon)
                            #print(bus0._action)
                            bus0._action_activated = 1
                        if bus0._hold_duration >= 18: # max holding time is 90s, which is 18 action steps
                            bus0._action = 1   
                            bus0._action_activated = 0
                        
                        if bus0._action == 0: # 0-hold, 1-not hold
                            bus0._boarding_time += 5
                            #bus0._trajectory_update(self._step,bus0._boarding_time)
                            bus0._hold_duration += 1
                        else:
                            #bus0._trajectory_update(self._step,bus0._boarding_time)
                            bus0._hold_duration = 0
                            bus0._restart = 1

                # check if the next state needs to be recorded
                if bus0._action_activated == 1:
                    bus0._action_start_step = self._step
                    bus0._action_activated = 0
                    
            for bus0 in self._bus3436:
                # bus0
                if self._step < bus0._departure_time:
                    bus0._trajectory_update(self._step, bus0._boarding_time)
                else:
                    if round(bus0._trajectory[-1],2) <= bus0._stop_position[-1]:
                        #print(round(bus0._trajectory[-1],2))
                        if round(bus0._trajectory[-1],2) not in bus0._stop_position:
                            bus0._trajectory_update(self._step, bus0._boarding_time)
                        elif round(bus0._trajectory[-1],2) in bus0._stop_position and bus0._boarding_time == 0:
                            if bus0._restart == 1:
                                bus0._trajectory_update(self._step, bus0._boarding_time)
                                bus0._restart = 0
                            else:
                                # calculate the boarding time
                                bus0._dwell_stop_ID = bus0._stop_position.index(round(bus0._trajectory[-1],2))
                                bus0._boarding_time = self._stops_3436[bus0._dwell_stop_ID]._get_boarding_time(self._step, bus0._served_line, bus0._dwell_stop_ID, self._passengers_stop_3436, self._common_passengers, self._common_passengers_save, bus0._onboard_passengers)
                                if bus0._boarding_time == 0:
                                    bus0._boarding_time = 1
                                bus0._trajectory_update(self._step, bus0._boarding_time)
                        else:
                            bus0._trajectory_update(self._step, bus0._boarding_time)
                
                
                if bus0._boarding_time > 0:
                    bus0._boarding_time -= 1
                    if bus0._boarding_time == 0:
                        #select action
                        if bus0._dwell_stop_ID == len(stop_position_3436) - 1:
                            bus0._action = 1
                        else:
                            bus0._current_state = self._get_state_bus0(bus0, self._bus3436, self._bus3986, self._stops_3436[bus0._dwell_stop_ID]._served_line)   # record the current state
                            bus0._action = self._choose_action_1(bus0._current_state, epsilon)
                            #print(bus0._action)
                            bus0._action_activated = 1
                        if bus0._hold_duration >= 18: # max holding time is 90s, which is 36 action steps
                            bus0._action = 1   
                            bus0._action_activated = 0
                        
                        if bus0._action == 0: # 0-hold, 1-not hold
                            bus0._boarding_time += 5
                            #bus0._trajectory_update(self._step,bus0._boarding_time)
                            bus0._hold_duration += 1
                        else:
                            #bus0._trajectory_update(self._step,bus0._boarding_time)
                            bus0._hold_duration = 0
                            bus0._restart = 1

                # check if the next state needs to be recorded
                if bus0._action_activated == 1:
                    bus0._action_start_step = self._step
                    bus0._action_activated = 0


            self._step += 1 # the position of step update is critical. it must be between the action_start record to the next state record detect 
            
            for bus0 in self._bus3986:
                if self._step == bus0._action_start_step + 5:
                    bus0._next_state = self._get_state_bus0(bus0, self._bus3986, self._bus3436, self._stops_3986[bus0._dwell_stop_ID]._served_line)
                    bus0._reward = self._reward_function.reward_function(bus0._current_state, bus0._action, bus0._next_state)
                    #bus0._reward = self._reward_function(bus0._current_state, bus0._action, bus0._next_state)
                    self._Memory.add_sample_1((bus0._current_state, bus0._action, bus0._reward, bus0._next_state))
                    self._trajectories_for_LLM.append(['bus3986_%s'%(self._bus3986.index(bus0)), bus0._action_start_step, bus0._dwell_stop_ID, bus0._current_state, bus0._action, bus0._reward, bus0._next_state])
                    #self._reward_1_store[episode].append(bus0._reward)
                    self._sum_reward_1 += bus0._reward
            for bus0 in self._bus3436:
                if self._step == bus0._action_start_step + 5:
                    bus0._next_state = self._get_state_bus0(bus0, self._bus3436, self._bus3986, self._stops_3436[bus0._dwell_stop_ID]._served_line)
                    bus0._reward = self._reward_function.reward_function(bus0._current_state, bus0._action, bus0._next_state)
                    #bus0._reward = self._reward_function(bus0._current_state, bus0._action, bus0._next_state)
                    self._Memory.add_sample_1((bus0._current_state, bus0._action, bus0._reward, bus0._next_state))
                    self._trajectories_for_LLM.append(['bus3436_%s'%(self._bus3436.index(bus0)), bus0._action_start_step, bus0._dwell_stop_ID, bus0._current_state, bus0._action, bus0._reward, bus0._next_state])
                    #self._reward_1_store[episode].append(bus0._reward)
                    self._sum_reward_1 += bus0._reward

        self._save_episode_stats_1()
        simulation_time = round(timeit.default_timer() - start_time, 1)
        
        print("Training...")
        start_time = timeit.default_timer()
        
        for train_epoch in range(self._training_epochs):
            self._replay()
        
        training_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time, training_time

    
    def _choose_action_1(self, state, epsilon):
        """
        Decide wheter to perform an explorative or exploitative action, according to an epsilon-greedy policy
        """
        if random.random() < epsilon:
            return random.randint(0, self._num_actions - 1) # random action
        else:
            return np.argmax(self._Model.predict_one_1(state)) # the best action given the current state

    
    def _get_state_bus0(self, ego_bus, ego_line_buses, other_line_buses, served_line):
        """
        Retrieve the state of the intersection from sumo, in the form of cell occupancy
        """
        state = np.zeros(self._num_states)
        # forward and backward headway between buses in the same line
        index_ego_bus = ego_line_buses.index(ego_bus)
        if index_ego_bus == 0 or index_ego_bus == len(ego_line_buses) or index_ego_bus == len(ego_line_buses)-1:
            state[0] = 0
            state[1] = 0
        else:
            if ego_line_buses[index_ego_bus-1]._trajectory[-1] > ego_line_buses[0]._trajectory[0] or ego_line_buses[index_ego_bus+1]._trajectory[-1] <= 0:
                state[0] = 0
                state[1] = 0
            else:
                state[0] = ego_line_buses[index_ego_bus-1]._trajectory[-1] - ego_line_buses[index_ego_bus]._trajectory[-1]
                state[1] = ego_line_buses[index_ego_bus]._trajectory[-1] - ego_line_buses[index_ego_bus+1]._trajectory[-1]
            
        # forward and backward headway between buses in the different lines
        if served_line != 0:
            state[2] = 0
            state[3] = 0
        else:
            if ego_bus._served_line == 1:
                stop_index_in_other_line = self._shared_stop_ID_in_3986[self._shared_stop_ID_in_3436.index(ego_bus._dwell_stop_ID)]
                ego_bus_pos_in_other_line = self._stops_3986[stop_index_in_other_line]._stop_pos
            else:
                stop_index_in_other_line = self._shared_stop_ID_in_3436[self._shared_stop_ID_in_3986.index(ego_bus._dwell_stop_ID)]
                ego_bus_pos_in_other_line = self._stops_3436[stop_index_in_other_line]._stop_pos
            
            min_forward_other = 1e11
            min_backward_other = 1e11
            for bus in other_line_buses:
                if len(bus._trajectory) < self._step:
                    pass
                else:
                    if bus._trajectory[-1] >= ego_bus_pos_in_other_line and (bus._trajectory[-1] - ego_bus_pos_in_other_line) < min_forward_other:
                        min_forward_other = bus._trajectory[-1] - ego_bus_pos_in_other_line
                        continue
                    if bus._trajectory[-1] <= ego_bus_pos_in_other_line and (ego_bus_pos_in_other_line - bus._trajectory[-1]) < min_backward_other:
                        min_backward_other = ego_bus_pos_in_other_line - bus._trajectory[-1]
                        continue
            
            state[2] = min_forward_other
            state[3] = min_backward_other
        
        state[4]=len(ego_bus._onboard_passengers)
        state[5]=ego_bus._hold_duration * 5 # cumulative holding time
        #state[3]=self._num_boarding_passengers_bus0
        
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

            self._Model.train_batch_1(x_1, y_1)  # train the NN
        

    def _save_episode_stats_1(self):
        """
        Save the stats of the episode to plot the graphs at the end of the session
        """
        self._reward_store_1.append(self._sum_reward_1)
    
