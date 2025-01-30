# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 16:09:56 2024

@author: 73148
"""

import os
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"


from openai import OpenAI
import analyzer

#if __name__ == "test_connect_API":
#if __name__ == "__main__":
client = OpenAI(api_key='your_key')

prompt_analyzer=analyzer.analyzer_all
user_analyzer=analyzer.user

completion = client.chat.completions.create(
  #model="gpt-3.5-turbo-instruct",
  model="gpt-4-turbo-preview",
  messages=[
    {"role": "system", "content": prompt_analyzer},
    {"role": "user", "content": user_analyzer}
  ],
  max_tokens = 2000,
  temperature = 0.3
)

#print(response['choices'][0]['text'])
analyzer_output=completion.choices[0].message.content
#print(analyzer_output)


with open(analyzer.data_path + 'analyzer_output.txt','w') as write_analyzer:
    #print('# -*- coding: utf-8 -*-')
    print(analyzer_output,file=write_analyzer)
