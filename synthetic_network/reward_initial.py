# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 20:01:29 2024

@author: 73148
"""

reward_initial_prompt = '''
# REWARD INITIAL

You are now a proficient reward designer for a reinforcement learning (RL) agent. You need to write proper reward functions for the agent. The agent will be trained for a bus holding control problem to improve the performance of the bus system. The detailed description of the task is as below.

## Background

In bus transit systems, due to the heterogeneous bus dwell time and traffic disturbance, the buses easily get bunch where two or more buses get too close even though the departure times of the buses are well-designed, particularly affecting bus services. Buses can be held at bus stops to adjust the headways to avoid bus bunching and balance the bus headways. However, unreasonable and excessive holding control for bus will increase the total travel time for passengers.

## Task description

- Objective: Balance the time headways of buses and minimize the **average travel time** of bus passengers. Since there is a strong correlation and consistent performance between time headway and space headway, balancing the time headways can be regarded as balancing the space headways.

## Basic definition:

- Time headway: the interval of arriving time between successive buses at the same bus stop. 
- Space headway: the space between successive buses. 
- Travel time of passenger: the time from the passenger arriving at the bus stop to his/her alighting time at the destination bus stop. It is the waiting time at the bus stop plus the time onboard the bus.

## Agent definition

- Overview of the agent:  The agent will be activated and decide an action every time a dwell bus is ready to continue the trip after the boarding process of passengers or at the end of last holding action. The action will last for 5 seconds, or say, the action step is 5 seconds.
- Agent's action: It is a binary variable. The value of '0' represents holding the bus at the stops for the next action step; the value of '1' represents not holding the bus, and the bus can continue its trip.
- Agent's state: It is a list [s0, s1, s2]. Each element in this list is introduced below:
    - s0: It is the forward space headway (meters) between the current bus and the forward bus.
    - s1: It is the backward space headway (meters) between the current bus and the backward bus.
    - s2: It is the number of onboard passengers of the current bus. Passengers can not board or alight when the bus is held, so the number of onboarding passengers is unchanged during holding control.

## Input parameters of the reward function

- Agent's action, denoted as `action` in the code.
- Agent's state at the beginning of the action, denoted as `current_state` in the code.
- Agent's state at the end of the action, denoted as `next_state` in the code. Please be aware that the s2 in `next_state` are the same as the s2 in `current_state` since passengers boarding and alighting is not allowed during holding control.

## General simulation environment information

- Simulation environment and settings: It is a loop corridor consisting of 8 uniformly distributed bus stops and 6 buses. The length of the corridor is 10656 meters. All buses have a constant speed v = 5.55 m/s and the travel time excluding dwelling and holding between two consecutive bus stops is 4 minutes (i.e., the distance between two adjacent stops is 1332 meters). The buses travel cyclically in this corridor. The maximum holding time T = 90 s.
- Arriving time of passengers: The passengers' arrival time at each bus stop follows the Poisson process. Please be aware the arrival time of passengers is exogenous inputs which can not be changed by the agent control.
- Positions of bus stops: The distances (meters) of the 8 bus stops from the origin are 666, 1998, 3330, 4662, 5994, 7326, 8658, and 9990, respectively.
- Passengers are not allowed to board and alight during holding control.

## Reward function requirements

You should write a reward function to achieve the **Task description**. The information you can use to formulate the reward function has been listed in the **Input parameters of the reward function**. 

## Output Requirements

- The reward function should be written in Python 3.8.16.
- Output the code block only. **Do not output anything else outside the code block**.
- You should include **sufficient comments** in your reward function to explain your thoughts, the objective and **implementation details**. The implementation can be specified to a specific line of code.
- Ensure the reward value will not be extremely large or extremely small which makes the reward meaningless.
- If you need to import packages (e.g. math, numpy) or define helper functions, define them at the beginning of the function. Do not use unimported packages and undefined functions.

## Output format

Strictly follow the following format. **Do not output anything else outside the code block**.

    def reward_function(current_state, action, next_state):
        # Thoughts:
        # ...
        # (initial the reward)
        reward = 0
        # (import packages and define helper functions)
        import numpy as np
        ...
        return reward
'''

user_reward_initial="Now write a reward function. Then in each iteration, I will use the reward function to train the RL agent and test it in the environment. I will give you possible reasons for the failure found during the testing, and you should modify the reward function accordingly. **Do not output anything else outside the code block. Please double check the output code. Ensure there is no error. The variables or function used should be defined already.**"

with open('reward_initial_prompt.txt', 'w') as rip:
    print(reward_initial_prompt,file = rip)
    print(user_reward_initial,file=rip)