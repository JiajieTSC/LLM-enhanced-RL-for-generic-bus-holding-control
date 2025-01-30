# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 20:28:28 2024

@author: 73148
"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
#import training_main
#import testing_main
import os

models_path=os.path.join(os.getcwd(), 'models', '')
dir_content = os.listdir(models_path)
lastest_version = [int(name.split("_")[1]) for name in dir_content]
model_path = os.path.join(models_path, 'model_'+str(max(lastest_version)), '')

#os.mkdir(model_path+'./test')
plot_path = os.path.join(model_path,'test', '')

path = model_path
#plot_path = testing_main.plot_path

f_read=open(path + 'reward_store.pkl','rb')
reward_store=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'trajectories_for_LLM.pkl','rb')
trajectories_for_LLM=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'passengers_stop.pkl','rb')
passengers_stop=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'trajectory_bus0.pkl','rb')
trajectory_bus0=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'trajectory_bus1.pkl','rb')
trajectory_bus1=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'trajectory_bus2.pkl','rb')
trajectory_bus2=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'trajectory_bus3.pkl','rb')
trajectory_bus3=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'trajectory_bus4.pkl','rb')
trajectory_bus4=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'trajectory_bus5.pkl','rb')
trajectory_bus5=pickle.load(f_read)
f_read.close()

#print(reward_store)

trajectories_for_LLM_direct = []

training_dic = {
    "training_history": {
        "total_rewards": reward_store
        }
    }


current_states=[]
actions=[]
rewards=[]
next_states=[]
for item in trajectories_for_LLM[-50:]:
    current_states.append(item[3])
    actions.append(item[4])
    rewards.append(item[5])
    next_states.append(item[6])
    
test_dic={
    "test_history": {
        "current_states": current_states,
        "actions": actions,
        "rewards": rewards,
        "next_states": next_states
        }
    }

stops_list = [666,1998,3330,4662,5994,7326,8658,9990]
arriving_steps_bus0 = [[] for i in range(len(stops_list))]
arriving_steps_bus1 = [[] for i in range(len(stops_list))]
arriving_steps_bus2 = [[] for i in range(len(stops_list))]
arriving_steps_bus3 = [[] for i in range(len(stops_list))]
arriving_steps_bus4 = [[] for i in range(len(stops_list))]
arriving_steps_bus5 = [[] for i in range(len(stops_list))]
stop_ID = 0
for stop_pos in stops_list:
    for step in range(len(trajectory_bus0)):
        if trajectory_bus0[step] == stop_pos and trajectory_bus0[step-1] != stop_pos:
            arriving_steps_bus0[stop_ID].append(step)
    for step in range(len(trajectory_bus1)):
        if trajectory_bus1[step] == stop_pos and trajectory_bus1[step-1] != stop_pos:
            arriving_steps_bus1[stop_ID].append(step)
    for step in range(len(trajectory_bus2)):
        if trajectory_bus2[step] == stop_pos and trajectory_bus2[step-1] != stop_pos:
            arriving_steps_bus2[stop_ID].append(step)
    for step in range(len(trajectory_bus3)):
        if trajectory_bus3[step] == stop_pos and trajectory_bus3[step-1] != stop_pos:
            arriving_steps_bus3[stop_ID].append(step)
    for step in range(len(trajectory_bus4)):
        if trajectory_bus4[step] == stop_pos and trajectory_bus4[step-1] != stop_pos:
            arriving_steps_bus4[stop_ID].append(step)
    for step in range(len(trajectory_bus5)):
        if trajectory_bus5[step] == stop_pos and trajectory_bus5[step-1] != stop_pos:
            arriving_steps_bus5[stop_ID].append(step)
    stop_ID += 1
    
#bus time headways variances
arriving_step_stop_line_all=[[] for i in range(len(stops_list))]
for i in range(len(stops_list)):
    arriving_step_stop_line_all[i]=arriving_steps_bus0[i]+arriving_steps_bus1[i]+arriving_steps_bus2[i]+arriving_steps_bus3[i]+arriving_steps_bus4[i]+arriving_steps_bus5[i]
    arriving_step_stop_line_all[i].sort()
    

headways_line_all = []
for i in range(len(stops_list)):
    for ii in range(len(arriving_step_stop_line_all[i])-1):
        headways_line_all.append(arriving_step_stop_line_all[i][ii+1]-arriving_step_stop_line_all[i][ii])
        
time_headways_variance_line_all = np.std(headways_line_all)

total_waiting_time = 0
total_num_boarding_passengers = 0
total_travel_time = 0
total_num_complete_passengers = 0
for i in range(len(passengers_stop)):
    for item in passengers_stop[i]:
        if passengers_stop[i][item][2]!=-1:
            passenger_wait_time = passengers_stop[i][item][2] - passengers_stop[i][item][0]
            total_waiting_time += passenger_wait_time
            total_num_boarding_passengers += 1
        if passengers_stop[i][item][3]!=-1:
            passenger_travel_time = passengers_stop[i][item][3] - passengers_stop[i][item][0]
            total_travel_time += passenger_travel_time
            total_num_complete_passengers += 1
average_waiting_time = total_waiting_time/total_num_boarding_passengers
average_travel_time = total_travel_time/total_num_complete_passengers

holding_duration = [0,0,0,0,0,0]
holding_times = [0,0,0,0,0,0]

every_bus_trajectories_for_LLM=[[],[],[],[],[],[]]
for i in range(len(trajectories_for_LLM)):
    if trajectories_for_LLM[i][0] == 'bus0':
        every_bus_trajectories_for_LLM[0].append(trajectories_for_LLM[i])
    if trajectories_for_LLM[i][0] == 'bus1':
        every_bus_trajectories_for_LLM[1].append(trajectories_for_LLM[i])
    if trajectories_for_LLM[i][0] == 'bus2':
        every_bus_trajectories_for_LLM[2].append(trajectories_for_LLM[i])
    if trajectories_for_LLM[i][0] == 'bus3':
        every_bus_trajectories_for_LLM[3].append(trajectories_for_LLM[i])
    if trajectories_for_LLM[i][0] == 'bus4':
        every_bus_trajectories_for_LLM[4].append(trajectories_for_LLM[i])
    if trajectories_for_LLM[i][0] == 'bus5':
        every_bus_trajectories_for_LLM[5].append(trajectories_for_LLM[i])

for bus in range(6):
    for i in range(len(every_bus_trajectories_for_LLM[bus])):
        if i == 0:
            if every_bus_trajectories_for_LLM[bus][i][4] == 0:
                holding_duration[bus] += 5
                holding_times[bus] += 1
        else:
            if every_bus_trajectories_for_LLM[bus][i][4] == 0:
                holding_duration[bus] += 5
            if every_bus_trajectories_for_LLM[bus][i][2]!=every_bus_trajectories_for_LLM[bus][i-1][2]:
                holding_times[bus] += 1
average_holding_time = sum(holding_duration)/sum(holding_times)

overall_indicators = {
    "SD_time_headways": round(time_headways_variance_line_all,2),
    "avg_passenger_travel_time": round(average_travel_time,2),
    "avg_passenger_waiting_time": round(average_waiting_time,2),
    "avg_holding_time": round(average_holding_time,2)
    }

test_dic.update(overall_indicators)


trajectories_for_LLM_direct = [training_dic, test_dic]

f_save=open(path + 'trajectories_for_LLM_direct.pkl','wb')
pickle.dump(trajectories_for_LLM_direct,f_save)
f_save.close()

with open('evaluations_records.txt', 'a') as eva_file:
    print(round(time_headways_variance_line_all,2), round(average_travel_time,2), round(average_waiting_time,2), round(average_holding_time,2), file=eva_file)

with open(path +'evaluations_records_for_this_model.txt', 'w') as ere_file:
    print("- Standard deviation of time headways:", round(time_headways_variance_line_all,2), file=ere_file)
    print("- Average travel time:", round(average_travel_time,2), file=ere_file)
    print("- Average waiting time:", round(average_waiting_time,2), file=ere_file)
    print("- Average holding time:", round(average_holding_time,2), file=ere_file)
    
plot_cutpoint_bus0=[0]
x=[]
for i in range(len(trajectory_bus0)-1):
    x.append(i)
    if trajectory_bus0[i+1]<trajectory_bus0[i]:
        plot_cutpoint_bus0.append(i)
        
plot_cutpoint_bus1=[320]
for i in range(len(trajectory_bus0)-1):
    if trajectory_bus1[i+1]<trajectory_bus1[i]:
        plot_cutpoint_bus1.append(i)
        
plot_cutpoint_bus2=[320*2]
for i in range(len(trajectory_bus0)-1):
    if trajectory_bus2[i+1]<trajectory_bus2[i]:
        plot_cutpoint_bus2.append(i)
        
plot_cutpoint_bus3=[320*3]
for i in range(len(trajectory_bus0)-1):
    if trajectory_bus3[i+1]<trajectory_bus3[i]:
        plot_cutpoint_bus3.append(i)
        
plot_cutpoint_bus4=[320*4]
for i in range(len(trajectory_bus0)-1):
    if trajectory_bus4[i+1]<trajectory_bus4[i]:
        plot_cutpoint_bus4.append(i)
        
plot_cutpoint_bus5=[320*5]
for i in range(len(trajectory_bus0)-1):
    if trajectory_bus5[i+1]<trajectory_bus5[i]:
        plot_cutpoint_bus5.append(i)

plt.rcParams.update({'font.size': 24})
'''
for ii in range(len(plot_cutpoint_bus0)-1):
    if ii<len(plot_cutpoint_bus0)-2:
        plt.plot(x[plot_cutpoint_bus0[ii]+1:plot_cutpoint_bus0[ii+1]],trajectory_bus0[plot_cutpoint_bus0[ii]+1:plot_cutpoint_bus0[ii+1]],'-', color='grey')
    else:
        plt.plot(x[plot_cutpoint_bus0[ii]+1:plot_cutpoint_bus0[ii+1]],trajectory_bus0[plot_cutpoint_bus0[ii]+1:plot_cutpoint_bus0[ii+1]],'-', label = 'BUS0', color='grey')
'''
for ii in range(len(plot_cutpoint_bus0)-1):
    plt.plot(x[plot_cutpoint_bus0[ii]+1:plot_cutpoint_bus0[ii+1]],trajectory_bus0[plot_cutpoint_bus0[ii]+1:plot_cutpoint_bus0[ii+1]],'-', color='grey')
plt.plot(x[plot_cutpoint_bus0[-1]+1:-1],trajectory_bus0[plot_cutpoint_bus0[-1]+1:-2],'-', label = 'BUS0', color='grey')

for ii in range(len(plot_cutpoint_bus1)-1):
    plt.plot(x[plot_cutpoint_bus1[ii]+1:plot_cutpoint_bus1[ii+1]],trajectory_bus1[plot_cutpoint_bus1[ii]+1:plot_cutpoint_bus1[ii+1]],'-', color='green')
plt.plot(x[plot_cutpoint_bus1[-1]+1:-1],trajectory_bus1[plot_cutpoint_bus1[-1]+1:-2],'-', label = 'BUS1', color='green')
for ii in range(len(plot_cutpoint_bus2)-1):
    plt.plot(x[plot_cutpoint_bus2[ii]+1:plot_cutpoint_bus2[ii+1]],trajectory_bus2[plot_cutpoint_bus2[ii]+1:plot_cutpoint_bus2[ii+1]],'-', color='orange')
plt.plot(x[plot_cutpoint_bus2[-1]+1:-1],trajectory_bus2[plot_cutpoint_bus2[-1]+1:-2],'-', label = 'BUS2', color='orange')
for ii in range(len(plot_cutpoint_bus3)-1):
    plt.plot(x[plot_cutpoint_bus3[ii]+1:plot_cutpoint_bus3[ii+1]],trajectory_bus3[plot_cutpoint_bus3[ii]+1:plot_cutpoint_bus3[ii+1]],'-', color='blue')
plt.plot(x[plot_cutpoint_bus3[-1]+1:-1],trajectory_bus3[plot_cutpoint_bus3[-1]+1:-2],'-', label = 'BUS3', color='blue')
for ii in range(len(plot_cutpoint_bus4)-1):
    plt.plot(x[plot_cutpoint_bus4[ii]+1:plot_cutpoint_bus4[ii+1]],trajectory_bus4[plot_cutpoint_bus4[ii]+1:plot_cutpoint_bus4[ii+1]],'-', color='red')
plt.plot(x[plot_cutpoint_bus4[-1]+1:-1],trajectory_bus4[plot_cutpoint_bus4[-1]+1:-2],'-', label = 'BUS4', color='red')
for ii in range(len(plot_cutpoint_bus5)-1):
    plt.plot(x[plot_cutpoint_bus5[ii]+1:plot_cutpoint_bus5[ii+1]],trajectory_bus5[plot_cutpoint_bus5[ii]+1:plot_cutpoint_bus5[ii+1]],'-', color='purple')
plt.plot(x[plot_cutpoint_bus5[-1]+1:-1],trajectory_bus5[plot_cutpoint_bus5[-1]+1:-2],'-', label = 'BUS5', color='purple')

plt.ylabel('Travel distance (m)')
plt.xlabel('Simulation step (s)')
plt.legend()
#plt.axis([0,100,0,20])
plt.gcf().set_size_inches(20, 11.25)
plt.savefig(plot_path + 'trajectory_bus0to5.png')
plt.close("all")