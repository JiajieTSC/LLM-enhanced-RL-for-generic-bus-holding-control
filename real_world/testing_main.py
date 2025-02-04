from __future__ import absolute_import
from __future__ import print_function

import os
import numpy as np
from shutil import copyfile
import matplotlib.pyplot as plt

from testing_simulation import Simulation as testing_Simulation
from model import TestModel
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path
import pickle
import reward_function

#if __name__ == "__main__":
#if __name__ == "testing_main":
config = import_test_configuration(config_file='testing_settings.ini')

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

plt.rcParams.update({'font.size': 28})
for bus0 in testing_Simulation._bus3986:
    plt.plot(bus0._trajectory, color='grey')
plt.ylabel('Distance (m)')
plt.xlabel('Simulation time (s)')
plt.legend()
#plt.axis([0,100,-2500,0])
plt.gcf().set_size_inches(20, 11.25)
plt.savefig(plot_path + 'trajectory_3986.png')
plt.close("all")

plt.rcParams.update({'font.size': 28})
for bus0 in testing_Simulation._bus3436:
    plt.plot(bus0._trajectory, color='grey')
plt.ylabel('Distance (m)')
plt.xlabel('Simulation time (s)')
plt.legend()
#plt.axis([0,100,-2500,0])
plt.gcf().set_size_inches(20, 11.25)
plt.savefig(plot_path + 'trajectory_3436.png')
plt.close("all")


bus_trajectories_3986 = []
for bus0 in testing_Simulation._bus3986:
    bus_trajectories_3986.append(bus0._trajectory)
f_save=open(plot_path + 'bus_trajectories_3986.pkl','wb')
pickle.dump(bus_trajectories_3986,f_save)
f_save.close()

bus_trajectories_3436 = []
for bus0 in testing_Simulation._bus3436:
    bus_trajectories_3436.append(bus0._trajectory)
f_save=open(plot_path + 'bus_trajectories_3436.pkl','wb')
pickle.dump(bus_trajectories_3436,f_save)
f_save.close()


stops_boarding_time_3986 = []
for stop in testing_Simulation._stops_3986:
    stops_boarding_time_3986.append(stop._boarding_time_record)
f_save=open(plot_path + 'stops_boarding_time_3986.pkl','wb')
pickle.dump(stops_boarding_time_3986,f_save)
f_save.close()

stops_boarding_time_3436 = []
for stop in testing_Simulation._stops_3436:
    stops_boarding_time_3436.append(stop._boarding_time_record)
f_save=open(plot_path + 'stops_boarding_time_3436.pkl','wb')
pickle.dump(stops_boarding_time_3436,f_save)
f_save.close()


f_save=open(plot_path + 'trajectories_for_LLM.pkl','wb')
pickle.dump(testing_Simulation._trajectories_for_LLM,f_save)
f_save.close()


f_save=open(plot_path + 'passengers_stop_3986.pkl','wb')
pickle.dump(testing_Simulation._passengers_stop_3986,f_save)
f_save.close()

f_save=open(plot_path + 'passengers_stop_3436.pkl','wb')
pickle.dump(testing_Simulation._passengers_stop_3436,f_save)
f_save.close()

f_save=open(plot_path + 'common_passengers_save.pkl','wb')
pickle.dump(testing_Simulation._common_passengers_save,f_save)
f_save.close()
