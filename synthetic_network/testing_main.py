from __future__ import absolute_import
from __future__ import print_function

import os
import numpy as np
from shutil import copyfile
import matplotlib.pyplot as plt

from testing_simulation import Simulation as testing_Simulation
#from generator import TrafficGenerator
from model import TestModel
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path
import pickle
#import training_main
import reward_function

#if __name__ == "__main__":
#if __name__ == "testing_main":
config = import_test_configuration(config_file='testing_settings.ini')
#sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
#model_path, plot_path = set_test_path(config['models_path_name'], config['model_to_test']) #这里要根据训练文件夹修改testing_settings配置文件里的model_to_test = n的信息
#plot_path = training_main.path + 'test'

models_path=os.path.join(os.getcwd(), 'models', '')
dir_content = os.listdir(models_path)
lastest_version = [int(name.split("_")[1]) for name in dir_content]
model_path = os.path.join(models_path, 'model_'+str(max(lastest_version)), '')

os.mkdir(model_path+'./test')
plot_path = os.path.join(model_path,'test', '')
Model = TestModel(
    input_dim=config['num_states'],
    model_path=model_path
)
'''
TrafficGen = TrafficGenerator(
    config['max_steps'], 
    config['n_cars_generated']
)
'''
Visualization = Visualization(
    plot_path, 
    dpi=96
)

Reward_function = reward_function
    
testing_Simulation = testing_Simulation(
    Model,
    Reward_function,
    config['max_steps'],
    config['green_duration'],
    config['yellow_duration'],
    config['num_states'],
    config['num_actions']
)
with open(plot_path + 'test_print.txt','a') as t_p:
    print('\n----- Test episode',file=t_p)
simulation_time = testing_Simulation.run(config['episode_seed'])  # run the simulation
with open(plot_path + 'test_print.txt','a') as t_p:
    print('Simulation time:', simulation_time, 's',file=t_p)

    print("----- Testing info saved at:", plot_path,file=t_p)



copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))




f_save=open(plot_path + 'trajectory_bus0.pkl','wb')
pickle.dump(testing_Simulation._trajectory_bus0,f_save)
f_save.close()

f_save=open(plot_path + 'trajectory_bus1.pkl','wb')
pickle.dump(testing_Simulation._trajectory_bus1,f_save)
f_save.close()

f_save=open(plot_path + 'trajectory_bus2.pkl','wb')
pickle.dump(testing_Simulation._trajectory_bus2,f_save)
f_save.close()

f_save=open(plot_path + 'trajectory_bus3.pkl','wb')
pickle.dump(testing_Simulation._trajectory_bus3,f_save)
f_save.close()

f_save=open(plot_path + 'trajectory_bus4.pkl','wb')
pickle.dump(testing_Simulation._trajectory_bus4,f_save)
f_save.close()

f_save=open(plot_path + 'trajectory_bus5.pkl','wb')
pickle.dump(testing_Simulation._trajectory_bus5,f_save)
f_save.close()

f_save=open(plot_path + 'control_state_action_bus0.pkl','wb')
pickle.dump(testing_Simulation._action_store_bus0,f_save)
f_save.close()

f_save=open(plot_path + 'control_state_action_bus1.pkl','wb')
pickle.dump(testing_Simulation._action_store_bus1,f_save)
f_save.close()

f_save=open(plot_path + 'control_state_action_bus2.pkl','wb')
pickle.dump(testing_Simulation._action_store_bus2,f_save)
f_save.close()

f_save=open(plot_path + 'control_state_action_bus3.pkl','wb')
pickle.dump(testing_Simulation._action_store_bus3,f_save)
f_save.close()

f_save=open(plot_path + 'control_state_action_bus4.pkl','wb')
pickle.dump(testing_Simulation._action_store_bus4,f_save)
f_save.close()

f_save=open(plot_path + 'control_state_action_bus5.pkl','wb')
pickle.dump(testing_Simulation._action_store_bus5,f_save)
f_save.close()

f_save=open(plot_path + 'boarding_time_record_bus0.pkl','wb')
pickle.dump(testing_Simulation._boarding_time_record_bus0,f_save)
f_save.close()

f_save=open(plot_path + 'boarding_time_record_bus1.pkl','wb')
pickle.dump(testing_Simulation._boarding_time_record_bus1,f_save)
f_save.close()

f_save=open(plot_path + 'boarding_time_record_bus2.pkl','wb')
pickle.dump(testing_Simulation._boarding_time_record_bus2,f_save)
f_save.close()

f_save=open(plot_path + 'boarding_time_record_bus3.pkl','wb')
pickle.dump(testing_Simulation._boarding_time_record_bus3,f_save)
f_save.close()

f_save=open(plot_path + 'boarding_time_record_bus4.pkl','wb')
pickle.dump(testing_Simulation._boarding_time_record_bus4,f_save)
f_save.close()

f_save=open(plot_path + 'boarding_time_record_bus5.pkl','wb')
pickle.dump(testing_Simulation._boarding_time_record_bus5,f_save)
f_save.close()

f_save=open(plot_path + 'trajectories_for_LLM.pkl','wb')
pickle.dump(testing_Simulation._trajectories_for_LLM,f_save)
f_save.close()

f_save=open(plot_path + 'passengers_stop.pkl','wb')
pickle.dump(testing_Simulation._passengers_stop,f_save)
f_save.close()

