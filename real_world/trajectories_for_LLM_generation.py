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

f_read=open(plot_path + 'passengers_stop_3436.pkl','rb')
passengers_stop_3436=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'passengers_stop_3986.pkl','rb')
passengers_stop_3986=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'common_passengers_save.pkl','rb')
common_passengers_save=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'bus_trajectories_3436.pkl','rb')
bus_trajectories_3436=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'bus_trajectories_3986.pkl','rb')
bus_trajectories_3986=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'stops_boarding_time_3436.pkl','rb')
stops_boarding_time_3436=pickle.load(f_read)
f_read.close()

f_read=open(plot_path + 'stops_boarding_time_3986.pkl','rb')
stops_boarding_time_3986=pickle.load(f_read)
f_read.close()

f_read=open('./data/stops_position_direct_distance_3436_1.pkl','rb')
stop_position_3436=pickle.load(f_read)
f_read.close()

f_read=open('./data/stops_position_direct_distance_3986_1.pkl','rb')
stop_position_3986=pickle.load(f_read)
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

time_headways_3436 = [[] for _ in range(len(passengers_stop_3436))]
arrival_time_3436 = [[] for _ in range(len(passengers_stop_3436))]
time_headways_total_3436 = []
for bus_traj in bus_trajectories_3436:
    for i in range(len(bus_traj)):
        if i == 0:
            continue
        if round(bus_traj[i],2) in stop_position_3436 and round(bus_traj[i-1],2) not in stop_position_3436 and bus_traj[i] != 0:
            stop_index = stop_position_3436.index(round(bus_traj[i],2))
            arrival_time_3436[stop_index].append(i)
for item in arrival_time_3436:
    for i in range(len(item)-1):
        time_headways_3436[arrival_time_3436.index(item)].append(item[i+1]-item[i])
        time_headways_total_3436.append(item[i+1]-item[i])
aveg_time_headway_3436 = sum(time_headways_total_3436) / len(time_headways_total_3436)
SD_time_headway_3436 = np.std(time_headways_total_3436)

time_headways_3986 = [[] for _ in range(len(passengers_stop_3986))]
arrival_time_3986 = [[] for _ in range(len(passengers_stop_3986))]
time_headways_total_3986 = []
for bus_traj in bus_trajectories_3986:
    for i in range(len(bus_traj)):
        if i == 0:
            continue
        if round(bus_traj[i],2) in stop_position_3986 and round(bus_traj[i-1],2) not in stop_position_3986 and bus_traj[i] != 0:
            stop_index = stop_position_3986.index(round(bus_traj[i],2))
            arrival_time_3986[stop_index].append(i)
for item in arrival_time_3986:
    for i in range(len(item)-1):
        time_headways_3986[arrival_time_3986.index(item)].append(item[i+1]-item[i])
        time_headways_total_3986.append(item[i+1]-item[i])
aveg_time_headway_3986 = sum(time_headways_total_3986) / len(time_headways_total_3986)
SD_time_headway_3986 = np.std(time_headways_total_3986)


shared_stop_ID_in_3436 = [11, 13, 14, 15, 16, 17, 18, 20]
shared_stop_pos_3436 = [stop_position_3436[item] for item in shared_stop_ID_in_3436] 
shared_arrival_time = [[] for _ in shared_stop_ID_in_3436]
for bus_traj in bus_trajectories_3436:
    for i in range(1,len(bus_traj)):
        if bus_traj[i]==None:
            pass
        elif round(bus_traj[i],2) in shared_stop_pos_3436 and round(bus_traj[i-1],2) not in shared_stop_pos_3436:
            shared_index = shared_stop_pos_3436.index(round(bus_traj[i],2))
            shared_arrival_time[shared_index].append(i)
        else:
            pass
    for i in range(len(bus_traj)):
        if bus_traj[i] < stop_position_3436[shared_stop_ID_in_3436[0]]-100:
            bus_traj[i] = None
        elif bus_traj[i] > stop_position_3436[shared_stop_ID_in_3436[-1]]+100:
            bus_traj[i] = None
        else:
            bus_traj[i] = bus_traj[i] - stop_position_3436[shared_stop_ID_in_3436[0]]+100
    
    
   
shared_stop_ID_in_3986 = [8, 10, 11, 12, 14, 15, 16, 19]
shared_stop_pos_3986 = [stop_position_3986[item] for item in shared_stop_ID_in_3986] 
for bus_traj in bus_trajectories_3986:
    for i in range(1,len(bus_traj)):
        if bus_traj[i]==None:
            pass
        elif round(bus_traj[i],2) in shared_stop_pos_3986 and round(bus_traj[i-1],2) not in shared_stop_pos_3986:
            shared_index = shared_stop_pos_3986.index(round(bus_traj[i],2))
            shared_arrival_time[shared_index].append(i)
        else:
            pass
    for i in range(len(bus_traj)):
        if bus_traj[i] < stop_position_3986[shared_stop_ID_in_3986[0]]-100:
            bus_traj[i] = None
        elif bus_traj[i] > stop_position_3986[shared_stop_ID_in_3986[-1]]+100:
            bus_traj[i] = None
        else:
            bus_traj[i] = bus_traj[i] - stop_position_3986[shared_stop_ID_in_3986[0]]+100
            
    

shared_time_headways = [[] for _ in shared_stop_ID_in_3436]
shared_time_headways_total = []
aa = 0
for a_time in shared_arrival_time:
    a_time.sort()
    for i in range(len(a_time)-1):
        shared_time_headways[aa].append(a_time[i+1]-a_time[i])
        shared_time_headways_total.append(a_time[i+1]-a_time[i])
    aa += 1

aveg_common_time_headway = sum(shared_time_headways_total)/len(shared_time_headways_total)
SD_common_time_headway = np.std(shared_time_headways_total)

plt.rcParams.update({'font.size': 28})
plt.plot(bus_trajectories_3436[0], color='grey',label='Line 1')
for bus0 in bus_trajectories_3436[1:]:
    plt.plot(bus0, color='grey')
plt.plot(bus_trajectories_3986[0], color='blue',label='Line 52')
for bus0 in bus_trajectories_3986[1:]:
    plt.plot(bus0, color='blue')
plt.ylabel('Distance (m)')
plt.xlabel('Simulation time (s)')
plt.legend()
#plt.axis([0,100,-2500,0])
plt.gcf().set_size_inches(20, 11.25)
plt.savefig(plot_path + 'common_line_trajectory.png')
plt.close("all")


waiting_times_3436 = []
travel_times_3436 = []
for item in passengers_stop_3436:
    for pas, detial in item.items():
        if detial[2] != -1:
            waiting_times_3436.append(detial[2]-detial[0])
        else:
            waiting_times_3436.append(3600*4-detial[0])
        if detial[3] != -1:
            travel_times_3436.append(detial[3]-detial[0])
        else:
            travel_times_3436.append(3600*4-detial[0])
aveg_waiting_time_3436 = sum(waiting_times_3436)/len(waiting_times_3436)
aveg_travel_time_3436 = sum(travel_times_3436)/len(travel_times_3436)
num_passengers_completed_wait_3436 = len(waiting_times_3436)
num_passengers_completed_travel_3436 = len(travel_times_3436)
num_passengers_total_3436 = sum([len(item) for item in passengers_stop_3436])

waiting_times_3986 = []
travel_times_3986 = []
for item in passengers_stop_3986:
    for pas, detial in item.items():
        if detial[2] != -1:
            waiting_times_3986.append(detial[2]-detial[0])
        else:
            waiting_times_3986.append(3600*4-detial[0])
        if detial[3] != -1:
            travel_times_3986.append(detial[3]-detial[0])
        else:
            travel_times_3986.append(3600*4-detial[0])
aveg_waiting_time_3986 = sum(waiting_times_3986)/len(waiting_times_3986)
aveg_travel_time_3986 = sum(travel_times_3986)/len(travel_times_3986)
num_passengers_completed_wait_3986 = len(waiting_times_3986)
num_passengers_completed_travel_3986 = len(travel_times_3986)
num_passengers_total_3986 = sum([len(item) for item in passengers_stop_3986])

waiting_times_common = []
travel_times_common = []
for item in common_passengers_save:
    for pas, detial in item.items():
        if detial[0][2] != -1:
            waiting_times_common.append(detial[0][2]-detial[0][0])
        else:
            waiting_times_common.append(3600*4-detial[0][0])
        if detial[0][3] != -1:
            travel_times_common.append(detial[0][3]-detial[0][0])
        else:
            travel_times_common.append(3600*4-detial[0][0])
aveg_waiting_time_common = sum(waiting_times_common)/len(waiting_times_common)
aveg_travel_time_common = sum(travel_times_common)/len(travel_times_common)
num_passengers_completed_wait_common = len(waiting_times_common)
num_passengers_completed_travel_common = len(travel_times_common)
num_passengers_total_common = sum([len(item) for item in common_passengers_save])



every_stop_trajectories_for_LLM_3436=[[] for _ in range(len(passengers_stop_3436))]
every_stop_trajectories_for_LLM_3986=[[] for _ in range(len(passengers_stop_3986))]
for i in range(len(trajectories_for_LLM)):
    if '3436' in trajectories_for_LLM[i][0]:
        every_stop_trajectories_for_LLM_3436[trajectories_for_LLM[i][2]].append(trajectories_for_LLM[i])
    elif '3986' in trajectories_for_LLM[i][0]:
        every_stop_trajectories_for_LLM_3986[trajectories_for_LLM[i][2]].append(trajectories_for_LLM[i])
    else:
        pass

for stop in every_stop_trajectories_for_LLM_3436:
    stop.sort()
    
holding_duration_3436 = 0
holding_times_3436 = 0
for stop in every_stop_trajectories_for_LLM_3436:
    for i in range(len(stop)):
        if i == 0:
            if stop[i][4] == 0:
                holding_duration_3436 += 5
                holding_times_3436 += 1
        else:
            if stop[i][4] == 0:
                holding_duration_3436 += 5
            if stop[i][0]!=stop[i-1][0]:
                holding_times_3436 += 1

for stop in every_stop_trajectories_for_LLM_3986:
    stop.sort()

holding_duration_3986 = 0
holding_times_3986 = 0
for stop in every_stop_trajectories_for_LLM_3986:
    for i in range(len(stop)):
        if i == 0:
            if stop[i][4] == 0:
                holding_duration_3986 += 5
                holding_times_3986 += 1
        else:
            if stop[i][4] == 0:
                holding_duration_3986 += 5
            if stop[i][0]!=stop[i-1][0]:
                holding_times_3986 += 1

average_holding_time_3436 = holding_duration_3436/holding_times_3436
average_holding_time_3986 = holding_duration_3986/holding_times_3986

overall_aveg_travel_time = round((sum(travel_times_3436)+sum(travel_times_3986))/(len(travel_times_3436)+len(travel_times_3986)),2)
overall_aveg_waiting_time = round((sum(waiting_times_3436)+sum(waiting_times_3986))/(len(waiting_times_3436)+len(waiting_times_3986)),2)

overall_indicators = {
    "test_results_line_1": {
        "SD_time_headways": round(SD_time_headway_3436,2),
        "avg_passenger_travel_time": round(aveg_travel_time_3436,2),
        "avg_passenger_waiting_time": round(aveg_waiting_time_3436,2),
        "avg_holding_time": round(average_holding_time_3436,2)
        },
    "test_results_line_2": {
        "SD_time_headways": round(SD_time_headway_3986,2),
        "avg_passenger_travel_time": round(aveg_travel_time_3986,2),
        "avg_passenger_waiting_time": round(aveg_waiting_time_3986,2),
        "avg_holding_time": round(average_holding_time_3986,2)
        },
    "test_results_shared_part": {
        "SD_time_headways": round(SD_common_time_headway,2),
        "avg_passenger_travel_time": round(aveg_travel_time_common,2),
        "avg_passenger_waiting_time": round(aveg_waiting_time_common,2)
        },
    "test_results_overall": {
        "avg_passenger_travel_time": overall_aveg_travel_time,
        "avg_passenger_waiting_time": overall_aveg_waiting_time
        }
    }

test_dic.update(overall_indicators)


trajectories_for_LLM_direct = [training_dic, test_dic]

f_save=open(path + 'trajectories_for_LLM_direct.pkl','wb')
pickle.dump(trajectories_for_LLM_direct,f_save)
f_save.close()

with open('evaluations_records.txt', 'a') as eva_file:
    print(overall_aveg_travel_time, overall_aveg_waiting_time,\
          round(SD_time_headway_3436,2),round(aveg_travel_time_3436,2),round(aveg_waiting_time_3436,2),round(average_holding_time_3436,2),\
          round(SD_time_headway_3986,2),round(aveg_travel_time_3986,2),round(aveg_waiting_time_3986,2),round(average_holding_time_3986,2),\
          round(SD_common_time_headway,2),round(aveg_travel_time_common,2),round(aveg_waiting_time_common,2),file=eva_file)

with open(path +'evaluations_records_for_this_model.txt', 'w') as ere_file:
    print('---test_results_line_1--- average time headway:',round(aveg_time_headway_3436,2),'SD time headway:',round(SD_time_headway_3436,2),'avergae waiting time:',round(aveg_waiting_time_3436,2),'average travel time:',round(aveg_travel_time_3436,2),'average holding time:',round(average_holding_time_3436,2),file=ere_file)
    print('---test_results_line_2--- average time headway:',round(aveg_time_headway_3986,2),'SD time headway:',round(SD_time_headway_3986,2),'avergae waiting time:',round(aveg_waiting_time_3986,2),'average travel time:',round(aveg_travel_time_3986,2),'average holding time:',round(average_holding_time_3986,2),file=ere_file)
    print('---test_results_shared_part--- average time headway:',round(aveg_common_time_headway,2),'SD time headway:',round(SD_common_time_headway,2),'average waiting time:',round(aveg_waiting_time_common,2),'average travel time:',round(aveg_travel_time_common,2),file=ere_file)
    print('---test_results_overall--- average waiting time:', overall_aveg_waiting_time,'average traveling time :',overall_aveg_travel_time,file=ere_file)
