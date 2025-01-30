# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 12:59:29 2024

@author: 73148
"""


import os
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"


from openai import OpenAI
import reward_exploration

#if __name__ == "test_connect_API":
#if __name__ == "__main__":
client = OpenAI(api_key='your_key')

prompt_reward_exploration=reward_exploration.reward_exploration_final
user_reward_exploration=reward_exploration.user_reward_exploration

completion = client.chat.completions.create(
  #model="gpt-3.5-turbo-instruct",
  model="gpt-4-turbo-preview",
  messages=[
    {"role": "system", "content": prompt_reward_exploration},
    {"role": "user", "content": user_reward_exploration}
  ],
  max_tokens = 2000,
  temperature = 0.3
)

#print(response['choices'][0]['text'])
reward_exploration_output=completion.choices[0].message.content
#print(reward_modify_output)

with open(reward_exploration.data_path + 'reward_exploration_output.txt','w') as write_reward_exploration:
    #print('# -*- coding: utf-8 -*-')
    print(reward_exploration_output,file=write_reward_exploration)
    
file = open(reward_exploration.data_path + 'reward_exploration_output.txt','r')
reward_function_lines = file.readlines()
reward_function = ''
for item in reward_function_lines:
    if "```python" in item or "```" in item:
        pass
    else:
        reward_function = reward_function + item
file.close()

with open('reward_function.py','w') as write_reward:
    #print('# -*- coding: utf-8 -*-')
    print(reward_function,file=write_reward)



