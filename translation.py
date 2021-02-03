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
used_ids = []

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
  if( len(male) <= len(female)):
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