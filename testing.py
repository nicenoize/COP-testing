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

url = 'https://clinical-outcome.demo.datexis.com/predict?task=mp'
tasks = ['mp', 'los', 'dia', 'pro']
results = pd.DataFrame(columns=['original', 'converted'])
results_original = []
results_converted = []

# Translation dictionaries
male2female_dict = {
    'Mr.': 'Ms.',
    'MALE': 'FEMALE',
    'Male': 'Female',
    'male': 'female',
    'Man': 'Woman',
    'man': 'woman',
    'M': 'F',
    'm': 'f',
    'He': 'She',
    'he': 'she',
    'Him': 'Her',
    'him': 'her',
    'His': 'Her',
    'his': 'her',
    'yoM': 'yoF',
}

yo_male2female = {
  'yoM': 'yoF'
}

female2male_dict = dict(map(reversed, male2female_dict.items()))
yo_female2male = dict(map(reversed, yo_male2female.items()))

def jsonConvert(text):
  json = '{"text": "' + text + '"}'
  return json

def multiple_replace(dict, text):
  # Create a regular expression  from the dictionary keys
  regex = re.compile("(%s)" % "|".join(map(re.escape, male2female_dict.keys())))
  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: male2female_dict[mo.string[mo.start():mo.end()]], text)

def reverse_gender(text):
  male = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in male2female_dict.keys()), text)
  female = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in female2male_dict.keys()), text)

  # Translate male to female and vice-versa
  if( len(male) > len(female)):
    text = male2female(text)
    return text
  if( len(male) < len(female)):
    text = female2male(text)
    return text


# Only match full words
def replace_male(match):
  return male2female_dict[match.group(0)]

def replace_female(match):
  return female2male_dict[match.group(0)]

def male2female(text):
  return re.sub('|'.join(r'\b%s\b' % re.escape(s) for s in male2female_dict), replace_male, text)

def female2male(text):
  return re.sub('|'.join(r'\b%s\b' % re.escape(s) for s in female2male_dict), replace_female, text)


example_1 = open("/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/example.txt", 'r').read()
example_2 = open("/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/185749.txt", 'r').read()
example_3 = open("/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/167745.txt", 'r').read()
example_4 = open("/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/159924.txt", 'r').read()
example_5 = open("/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/152015.txt", 'r').read()
example_6 = open("/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/175190.txt", 'r').read()

# table: id, text, hospital_expire_flag
mortality_task_test = pd.read_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/Outcome Task Files/mortality_task/MORTALITY_FILES/MP_IN_adm_test.csv')
mortality_task_test_texts_original = []
mortality_task_test_texts_converted = []

for elem in mortality_task_test['text']:
  mortality_task_test_texts_original.append(elem.replace('\n', ' '))

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

folder_path = '/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/data'
for filename in glob.glob(os.path.join(folder_path, '*.txt')):
  with open(filename, 'r') as f:
    text = f.read()
    examples.append(text)

folder_path = '/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/data/female'
for filename in glob.glob(os.path.join(folder_path, '*.txt')):
  with open(filename, 'r') as f:
    text = f.read()
    examples_female.append(text)

folder_path = '/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/data/male'
for filename in glob.glob(os.path.join(folder_path, '*.txt')):
  with open(filename, 'r') as f:
    text = f.read()
    examples_male.append(text)

#examples = [example_1, example_2, example_3, example_4, example_5, example_6]

# Check for gender in given example
male_patterns = ['\bmale', '\bman', '\b[0-9][0-9]yoM', '\byo M']
female_patterns = ['\bfemale', '\bwoman', '\b[0-9][0-9]yoF', '\byo F', '\bF']

# Check each example for occurrences of female & male words
for text in examples:
  male = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in male2female_dict.keys()), text)
  female = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in female2male_dict.keys()), text)

  # Translate male to female and vice-versa
  if( len(male) > len(female) ):
    text = male2female(text)
    # Replace 62yoM
    #text = multiple_replace(yo_male2female, text)
    reversals.append(text)
  if( len(male) < len(female) ):
    text = female2male(text)
    # Replace 62yoF
    #ätext = multiple_replace(yo_female2male, text)
    reversals.append(text)

# Female examples
for text in examples_female:
  male = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in male2female_dict.keys()), text)
  female = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in female2male_dict.keys()), text)

  # Translate male to female and vice-versa
  if( len(male) > len(female) ):
    text = male2female(text)
    # Replace 62yoM
    #text = multiple_replace(yo_male2female, text)
    female_reversed.append(text)
    female_texts.append(male2female(text))
  if( len(male) < len(female) ):
    text = female2male(text)
    # Replace 62yoF
    #text = multiple_replace(yo_female2male, text)
    female_reversed.append(text)

# Male examples
for text in examples_male:
  male = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in male2female_dict.keys()), text)
  female = re.findall('|'.join(r'\b%s\b' % re.escape(s) for s in female2male_dict.keys()), text)

  # Translate male to female and vice-versa
  if( len(male) > len(female) ):
    text = male2female(text)
    # Replace 62yoM
    #text = multiple_replace(yo_male2female, text)
    male_reversed.append(text)
    female_texts.append(male2female(text))
  if( len(male) < len(female) ):
    text = female2male(text)
    # Replace 62yoF
    #text = multiple_replace(yo_female2male, text)
    male_reversed.append(text)


headers = {
  'Content-Type': 'application/json'
}
payload='{"text": "patient letter ..."}'
response = requests.request("POST", url, headers=headers, data=str(jsonConvert(examples_female[0].replace('\n', ' '))), auth=('datexis', 'datexis2020'))
# Send POST request with the original and gender-reversed samples
request_original = requests.post(url, data = jsonConvert(examples_female[0].replace('\n', ' ')), auth=('datexis', 'datexis2020'), headers=headers)
#request_genderchange = requests.post(url, data = multiple_replace(male2female_dict, example_1), auth=('datexis', 'datexis2020'))
for i in tqdm(range(len(mortality_task_test_texts_original))):
  response = requests.request("POST", url, headers=headers, data=str(jsonConvert(mortality_task_test_texts_original[i])), auth=('datexis', 'datexis2020'))
  results_original.append(response.text)

for j in tqdm(range(len(mortality_task_test_texts_converted))):
  response = requests.request("POST", url, headers=headers, data=str(jsonConvert(mortality_task_test_texts_converted[i])), auth=('datexis', 'datexis2020'))
  results_converted.append(response.text)

results = pd.DataFrame(({'original':results_original, 'converted':results_converted})
)
results.to_csv('/Users/nicenoize/Documents/DATEXIS/Clinical Outcome Predcition/Testing/results/results.csv')

# # Loop over all tasks:
# for task in tasks:
#   request_original = requests.post(url+task, data = example_1, auth=('datexis', 'datexis2020'))
#   request_genderchange = requests.post(url+task, data = multiple_replace(male2female_dict, example_1), auth=('datexis', 'datexis2020'))

# Patterns
# 55yo male
# 79-year-old woman
# 64 yo w
# year old man
# year old non-diabetic white male
# 51-year-old gentleman
# 36-year-old male
# Pt is a 69yoF
# Pt is a [**Age over 90 **] yo F
# yo male
# Regex expressions:
male_pattern = '\bmale'
man_pattern =  '\bman'
yoM_pattern = '\b[0-9][0-9]yoM'
yo_M_pattern = '\byo M'
M_pattern = '\bM'

female_pattern = '\bfemale'
woman_pattern = '\bwoman'
yoF_pattern = '\b[0-9][0-9]yoF'
yo_F_pattern = '\byo F'
F_pattern = '\bF'

