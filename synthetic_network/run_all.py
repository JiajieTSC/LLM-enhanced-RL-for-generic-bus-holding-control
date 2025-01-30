# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 19:06:11 2024

@author: 73148
"""
import os
import sys
#ATTENTION!!! reward initial should be removed if not the first time to run the code 
#os.system("python reward_initial_API.py")

previous_sd_time_headways = -1
previous_avg_travel_time = 1e11
previous_avg_wait_time = -1
previous_avg_hold_time = -1

for gpt_response in range(4):
    # run train and test
    training_main_value = os.system("python training_main.py")
    if training_main_value != 0:
        print('error from training_main',training_main_value)
        sys.exit(0)
    testing_main_value = os.system("python testing_main.py")
    if testing_main_value != 0:
        print('error from testing_main',testing_main_value)
        sys.exit(0)
    
    print("run the 'trajectories_for_LLM_generation.py'")
    trajectories_for_LLM_generation_value = os.system("python trajectories_for_LLM_generation.py")
    if trajectories_for_LLM_generation_value != 0:
        print('error from trajectories_for_LLM_generation_value',trajectories_for_LLM_generation_value)
        sys.exit(0)
    
    with open("evaluations_records.txt","r") as er:
        for line in er.readlines():
            curLine = line.strip().split(" ")
    er.close()
    current_sd_time_headways = eval(curLine[0])
    current_avg_travel_time = eval(curLine[1])
    current_avg_wait_time = eval(curLine[2])
    current_avg_hold_time = eval(curLine[3])

    if current_avg_travel_time < 1.1 * previous_avg_travel_time:
        previous_sd_time_headways = current_sd_time_headways
        previous_avg_travel_time = current_avg_travel_time
        previous_avg_wait_time = current_avg_wait_time
        previous_avg_hold_time = current_avg_hold_time
        
        with open("evaluations_records.txt","a") as er_write:
            print('# the line above is valid!',file=er_write)

        # run gpt    
        print("analyzer API")
        analyzer_API_value = os.system("python analyzer_API.py")
        if analyzer_API_value != 0:
            print('error from analyzer_API_value',analyzer_API_value)
            sys.exit(0)
        
        print("reward modify API")
        reward_modify_API_value = os.system("python reward_modify_API.py")
        if reward_modify_API_value != 0:
            print('error from reward_modify_API_value',reward_modify_API_value)
            sys.exit(0)
    else:
        print("reward exploration API")
        reward_exploration_API_value = os.system("python reward_exploration_API.py")
        if reward_exploration_API_value != 0:
            print('error from reward_exploration_API_value',reward_exploration_API_value)
            sys.exit(0)
    

#runpy.run_path('analyzer.py')



