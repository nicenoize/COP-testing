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

url = 'https://clinical-outcome.demo.datexis.com/predict?task=dia'
tasks = ['mp', 'los', 'dia', 'pro']
results = pd.DataFrame(columns=['original', 'converted'])
results_original = []
results_converted = []
used_ids = []
short_codes = []

# table: id, text, hospital_expire_flag
diagnoses_task_test = pd.read_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/Outcome Task Files/diagnoses_task/DIAGNOSES_3_DIGIT_FILES/DIA_GROUPS_3_DIGITS_adm_test.csv')
diagnoses_task_test_texts_original = []
diagnoses_task_test_texts_converted = []

for elem in diagnoses_task_test['text']:
  diagnoses_task_test_texts_original.append(elem.replace('\n', ' ').replace('"', ''))

for elem in diagnoses_task_test_texts_original:
  diagnoses_task_test_texts_converted.append(reverse_gender(elem))
headers = {
  'Content-Type': 'application/json'
}
payload='{"text": "patient letter ..."}'
used_text_original = []
used_text_converted = []
# Send POST request with the original and gender-reversed samples
#request_genderchange = requests.post(url, data = multiple_replace(male2female_dict, example_1), auth=('datexis', 'datexis2020'))
#for i in tqdm(range(len(diagnoses_task_test_texts_original))):

for i in tqdm(range(50)):
  response = requests.request("POST", url, headers=headers, data=str(jsonConvert(diagnoses_task_test_texts_original[i])), auth=('datexis', 'datexis2020'))
  results_original.append(response.text)
  used_text_original.append(jsonConvert(diagnoses_task_test_texts_original[i]))
  used_ids.append(diagnoses_task_test['id'][i])
  short_codes.append(diagnoses_task_test['short_codes'][i])

#for j in tqdm(range(len(diagnoses_task_test_texts_converted))):
for j in tqdm(range(50)):
  response = requests.request("POST", url, headers=headers, data=str(jsonConvert(diagnoses_task_test_texts_converted[j])), auth=('datexis', 'datexis2020'))
  results_converted.append(response.text)
  used_text_converted.append(jsonConvert(diagnoses_task_test_texts_converted[j]))


results = pd.DataFrame(({'id':used_ids, 'short_codes': short_codes, 'original':results_original, 'converted':results_converted}))
results['original_codes'] = results['original_codes'].apply(lambda x: x.replace('\n', '').replace('"',""))
results['converted_codes'] = results['converted_codes'].apply(lambda x: x.replace('\n', '').replace('"', ""))

used_texts = pd.DataFrame(({'original':used_text_original, 'converted':used_text_converted}))
results.to_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/results/dia_results.csv')
used_texts.to_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/results/used_texts.csv')


