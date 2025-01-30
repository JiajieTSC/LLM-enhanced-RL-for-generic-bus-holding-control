# LLM-enhanced-RL-for-generic-bus-holding-control

This repository contains the code for the paper *"Large Language Model-Enhanced Reinforcement Learning for Generic Bus Holding Control Strategies"*. It includes the bus system simulation, the data used in the paper, and all code for the LLM-enhanced RL paradigm.

## Folder Description

- The `synthetic_network` folder contains the numerical test for Case Study 1, with the data encoded in the code.
- The `real_world` folder contains the data and code for the numerical tests of Case Studies 2 and 3. These two tests share the same code framework. Before training and testing the model, update the data path accordingly.

## Running the Algorithm

1. Replace `your_key` with your OpenAI API key in all scripts containing "API" in their names.
2. Set the refinement rule and the number of iterations in the script named `run_all` as you like.
3. Run the `run_all` script to start the paradigm.
