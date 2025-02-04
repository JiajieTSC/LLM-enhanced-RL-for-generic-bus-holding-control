# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 13:24:21 2022

@author: 73148
"""

from __future__ import absolute_import
from __future__ import print_function

import os
import datetime
import numpy as np
from shutil import copyfile
import matplotlib.pyplot as plt

from training_simulation import Simulation as training_Simulation
from memory import Memory
from model import TrainModel
from visualization import Visualization
from utils import import_train_configuration, set_sumo, set_train_path
import pickle
import runpy
import reward_function

#if __name__ == "__main__":
#if __name__ == "training_main":
config = import_train_configuration(config_file='training_settings.ini') #输入训练过程中的配置信息，包括是否打开gui、黄灯时长、最大step等等
sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps']) #获得sumoconfig文件等命令信息
path = set_train_path(config['models_path_name']) #set the path of model saving

Model = TrainModel(
    config['num_layers'], 
    config['width_layers'], 
    config['batch_size'], 
    config['learning_rate'], 
    input_dim=config['num_states'], 
    output_dim=config['num_actions']
)

Memory = Memory(
    config['memory_size_max'], 
    config['memory_size_min']
)

Visualization = Visualization(
    path, 
    dpi=96
)

Reward_function = reward_function
    
training_Simulation = training_Simulation(
    Model,
    Memory,
    Reward_function,
    sumo_cmd,
    config['gamma'],
    config['max_steps'],
    config['green_duration'],
    config['yellow_duration'],
    config['num_states'],
    config['num_actions'],
    config['training_epochs'],
    #config['total_episodes']
)

episode = 0
timestamp_start = datetime.datetime.now()

while episode < config['total_episodes']:
    with open(path + 'reward_print.txt','a') as re_p:
        print('\n----- Episode', str(episode+1), 'of', str(config['total_episodes']),file=re_p)
    if episode < 50:
        epsilon = 1.0 - (episode/50)  # set the epsilon for this episode according to epsilon-greedy policy
    else:
        epsilon = 0.02
    simulation_time, training_time = training_Simulation.run(episode, epsilon)  # run the simulation 这里调用了simulation class，simulation class里面嵌套调用了generator里面的class
    with open(path + 'reward_print.txt','a') as re_p:
        print("Total reward:", training_Simulation._sum_reward_1, "- Epsilon:", round(epsilon, 2),file=re_p)
        print('Simulation time:', simulation_time, 's - Training time:', training_time, 's - Total:', round(simulation_time+training_time, 1), 's',file=re_p)
    episode += 1
    
    if episode == 50:
        Model.save_model(path+'50')
    if episode == 55:
        Model.save_model(path+'55')
    if episode == 60:
        Model.save_model(path+'60')
    if episode == 65:
        Model.save_model(path+'65')
    if episode == 70:
        Model.save_model(path+'70')
    
with open(path + 'reward_print.txt','a') as re_p:
    print("\n----- Start time:", timestamp_start,file=re_p)
    print("----- End time:", datetime.datetime.now(),file=re_p)
    print("----- Session info saved at:", path,file=re_p)

Model.save_model(path)

copyfile(src='training_settings.ini', dst=os.path.join(path, 'training_settings.ini'))

Visualization.save_data_and_plot(data=training_Simulation._reward_store_1, filename='total_net_reward_1', xlabel='Episode', ylabel='Cumulative reward for agent 1')


plt.rcParams.update({'font.size': 28})
plt.plot(training_Simulation._reward_store_1, color='grey')
plt.ylabel('Total reward')
plt.xlabel('Episode')
plt.legend()
#plt.axis([0,100,-2500,0])
plt.gcf().set_size_inches(20, 11.25)
plt.savefig(path + 'total_reward_agent.png')
plt.close("all")

for i in range(len(training_Simulation._reward_store_1)):
    with open(path + 'reward_store_final.txt','a') as reward_data:
        print(training_Simulation._reward_store_1[i],file=reward_data)

f_save=open(path + 'reward_store.pkl','wb')
pickle.dump(training_Simulation._reward_store_1,f_save)
f_save.close()




