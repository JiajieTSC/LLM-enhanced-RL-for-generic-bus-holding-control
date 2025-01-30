# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 12:06:22 2024

@author: 73148
"""

import pickle
import os
#import testing_main

analyzer1 = '''
You are now a proficient reward designer for a reinforcement learning (RL) agent. The agent is designed for a bus holding control problem to improve the performance of the bus system. The detailed description of the task is in the following section. I now have a reward function for the agent to complete the described task. I have trained the RL agent for several times and tested it in the simulation environment. I will give you the information on the training and test results, i.e. trajectory of training rewards, trajectories of actions, rewards, and states during the test. You should help me write a proper analysis of possible reasons for inefficiency from both the training and test performances and your suggestions on the reward function improvement. 

## Background

In bus transit systems, due to the heterogeneous bus dwell time and traffic disturbance, the buses easily get bunch where two or more buses get too close even though the departure times of the buses are well-designed, particularly affecting bus services. Buses can be held at bus stops to adjust the headways to avoid bus bunching.

## Task description

- Objective: Balance the time headways of buses and minimize the average travel time of bus passengers. Since there is a strong correlation and consistent performance between time headway and space headway, balancing the time headways can be regarded as balancing the space headways.

## Basic definition:

- Time headway: the interval of arriving time between successive buses at the same bus stop. 
- Space headway: the space between successive buses. 
- Travel time of passenger: the time from the passenger arriving at the bus stop to his/her alighting time at the destination bus stop. It is the waiting time of passengers at the bus stop plus the time onboard the bus.

## Agent definition

- Overview of the agent:  The agent will be activated and decide an action every time a dwell bus is ready to continue the trip after the boarding process of passengers or at the end of last holding action. The action will last for 5 seconds, or say, the action step is 5 seconds.
- Agent's action: It is a binary variable. The value of '0' represents holding the bus at the stops for the next action step; the value of '1' represents not holding the bus, and the bus can continue its trip.
- Agent's state: It is a list [s0, s1, s2]. Each element in this list is introduced below:
    - s0: It is the forward space headway (meters) between the current bus and the forward bus.
    - s1: It is the backward space headway (meters) between the current bus and the backward bus.
    - s2: It is the number of onboard passengers of the current bus. Passengers can not board the bus when the bus is held, so the number of onboarding passengers is unchanged during holding control.
    
## Input parameters of the reward function

- Agent's action, denoted as `action` in the code.
- Agent's state at the beginning of the action, denoted as `current_state` in the code.
- Agent's state at the end of the action, denoted as `next_state` in the code. Please be aware that the s2 in `next_state` are the same as the s2 in `current_state` since passengers boarding and alighting is not allowed during holding control.

## General simulation environment information

- Simulation environment and settings: It is a loop corridor consisting of 8 uniformly distributed bus stops and 6 buses. The length of the corridor is 10656 meters. All buses have a constant speed v = 5.55 m/s and the travel time excluding dwelling and holding between two consecutive bus stops is 4 minutes (i.e., the distance between two adjacent stops is 1332 meters). The buses travel cyclically in this corridor. The boarding times per passenger are set to 3.0 s/pax. The maximum holding time T = 90 s.
- Arriving time of passengers: The passengers' arrival time at each bus stop follows the Poisson process. Please be aware the arrival time of passengers is exogenous inputs which can not be changed by the agent control.
- Positions of bus stops: The distances (meters) of the 8 bus stops from the origin are 666, 1998, 3330, 4662, 5994, 7326, 8658, and 9990, respectively.
- Passengers are not allowed to board and alight during holding control.

## Input format

### Training and test trajectories

The trajectories are shown as a list, where each entry is a dictionary representing a trajectory. The first entry is the trajectory of total rewards at each training episode. The second entry contains the trajectory of states, actions, and step rewards during the test as well as the final results of the test.

Each item of "test_history" is a list representing statistics of each single action step. When the "test_history" is too long, it will be truncated to the last 50 steps.

The format is:
[
    {
        "training_history": {
            "total_rewards": [total_reward1, total_reward_2, ...]
        }
    },
    {
        "test_history": {
            "current_states": [current_state1, current_state2, ...],
            "actions": [action1, action2, ...],
            "rewards": [reward1, reward2, ...],
            "next_states": [next_states1, next_states2, ...]
        },
        "SD_time_headways": SD_time_headways,
        "avg_passenger_travel_time": avg_passenger_travel_time,
        "avg_passenger_waiting_time": avg_passenger_waiting_time,
        "avg_holding_time": avg_holding_time
    }
]

where "SD_time_headways" is the standard deviation of bus time headways during the test. "avg_passenger_travel_time" is the average travel time of passengers. "avg_passenger_waiting_time" is the average waiting time of passengers at bus stops. "avg_holding_time" is the average holding time of buses.

## Output Requirements

Please write a proper analysis of the training performance (i.e., the convergence) and the test performance. Please try to give some suggestions on the reward improvement. You should not not be limited to the task description above, but also come up with other inefficient cases based on the training and test results.

**The analysis and suggestions should be concise.**
'''
analyzer2 = '''
## Training and test results
### Training and test trajectories

{trajectories_for_LLM_direct}

Now according to the **Training and test results**, please write your analysis and suggestions on the reward function improvement.
'''
models_path=os.path.join(os.getcwd(), 'models', '')
dir_content = os.listdir(models_path)
lastest_version = [int(name.split("_")[1]) for name in dir_content]
data_path = os.path.join(models_path, 'model_'+str(max(lastest_version)), '')


#f_read=open(plot_path + 'trajectories_for_LLM_direct.pkl','rb')
#path = testing_main.model_path
f_read=open(data_path + 'trajectories_for_LLM_direct.pkl','rb')
trajectories_for_LLM_direct=pickle.load(f_read)
f_read.close()


user = analyzer2.format(trajectories_for_LLM_direct=trajectories_for_LLM_direct)

analyzer_all = analyzer1


with open(data_path + 'analyzer_prompt.txt', 'w') as ap:
    print(analyzer_all,file = ap)
    print(user,file=ap)
    

