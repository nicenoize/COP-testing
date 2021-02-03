# Patterns
# API Call:
# https://clinical-outcome.demo.datexis.com/predict?task=mp
# {
#	"text": "patient letter ..."
# }
# task param: mp, los, dia oder pro 
# Basic auth: user: datexis pw: datexis2020
#
from time import sleep
from tqdm import tqdm
import requests
import re
import os, glob
import json
import pandas as pd
from translation import reverse_gender, jsonConvert

url = 'https://clinical-outcome.demo.datexis.com/predict?task=mp'
tasks = ['mp', 'los', 'dia', 'pro']
results = pd.DataFrame(columns=['original', 'converted'])
results_original = []
results_converted = []
used_ids = []

# table: id, text, hospital_expire_flag
mortality_task_test = pd.read_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/Outcome Task Files/mortality_task/MORTALITY_FILES/MP_IN_adm_test.csv')
mortality_task_test_texts_original = []
mortality_task_test_texts_converted = []

for elem in mortality_task_test['text']:
  mortality_task_test_texts_original.append(elem.replace('\n', ' ').replace('"', ''))

for elem in mortality_task_test_texts_original:
  mortality_task_test_texts_converted.append(reverse_gender(elem))

examples = []
examples_female = []
female_reversed = []
examples_male = []
male_reversed = []
reversals = []
female_texts = []
male_texts = []

headers = {
  'Content-Type': 'application/json'
}
payload='{"text": "patient letter ..."}'
used_text_original = []
used_text_converted = []
# Send POST request with the original and gender-reversed samples
#request_genderchange = requests.post(url, data = multiple_replace(male2female_dict, example_1), auth=('datexis', 'datexis2020'))
#for i in tqdm(range(len(mortality_task_test_texts_original))):

for i in tqdm(range(50)):
  response = requests.request("POST", url, headers=headers, data=str(jsonConvert(mortality_task_test_texts_original[i])), auth=('datexis', 'datexis2020'))
  results_original.append(response.text)
  used_text_original.append(jsonConvert(mortality_task_test_texts_original[i]))
  used_ids.append(mortality_task_test['id'][i])

#for j in tqdm(range(len(mortality_task_test_texts_converted))):
for j in tqdm(range(50)):
  response = requests.request("POST", url, headers=headers, data=str(jsonConvert(mortality_task_test_texts_converted[j])), auth=('datexis', 'datexis2020'))
  results_converted.append(response.text)
  used_text_converted.append(jsonConvert(mortality_task_test_texts_converted[j]))


results = pd.DataFrame(({'id':used_ids, 'original':results_original, 'converted':results_converted}))
results['original'] = results['original'].apply(lambda x: x.replace('\n', '').replace('"',""))
results['converted'] = results['converted'].apply(lambda x: x.replace('\n', '').replace('"', ""))
results['original'] = results['original'].astype(float)
results['converted'] = results['converted'].astype(float)
results['diff'] = results['original'] - results['converted']

used_texts = pd.DataFrame(({'original':used_text_original, 'converted':used_text_converted}))
results.to_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/results/mp_results.csv')
used_texts.to_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/results/used_texts.csv')


