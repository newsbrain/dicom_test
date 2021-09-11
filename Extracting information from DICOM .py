#!/usr/bin/env python
# coding: utf-8

# # Extrcting Information from DICOM Files

# ## Task description
# <br>
# <a href="https://s3.amazonaws.com/viz_data/DM_TH.tgz" target="_blank">This link</a> leads to a tar file containing multiple DICOM files of several patients.
# In a nutshell - every DICOM file is a single image. A single scan (or "series") is composed of several images, and a single "study" is composed of several series. The DICOM hierarchy is nicely described in the attached image.
# <br>
# <br>
# 
# You might find the pydicom module very handy, as well as the following tags:
# <br>
# PatientName 
# <br>
# 
# StudyInstanceUID (unique identifier per study)
# <br>
# 
# SeriesInstanceUID (unique identifier per series)
# <br>
# 
# PatientAge
# <br>
# 
# PatientSex
# <br>
# 
# InstitutionName 
# <br>
# 

# ## Task list
# <br>
# 
# Your task is to write a python script that receives the URL and:
# <br>
# 
# - downloads the file 
# <br>
# 
# - arranges the files according to the DICOM hierarchy in an appropriate directory structure (patient/study/series). Note that patient names were replaced with IDs to protect their privacy. 
# <br>
# <br>
# 
# - performs the following tasks or answers the following questions:
# <br>
# 
# 1) generate a list of patients, their age and sex
# 
# 2) how long does a CT scan take on average? 
# 
# 3) how many different hospitals do the data come from?
# 
# ____________
# 
# Any additional analysis  / visualization you can think that can be useful for data understanding? 
# 
# 

# # The Task

# ## Importing libraries 
# 

# In[1]:


import pandas as pd #for any data manipulation, dataframes, etc
import numpy as np #for datatypes manipulations
import plotly.express as px #for visualisation
import matplotlib.pyplot as plt #for displaying DICOM images 
import os #for getting access to local folders, etc
import requests #for making requests from web
from bs4 import BeautifulSoup #to scrape information from web pages
from archive import extract #a library for extracting archives

#importing pydicom library for working with DICOM files

from pydicom import dcmread


# In[2]:


path = os.getcwd() #saving path for easy use throughout the Notebook
head = 10  #defaulting Pandas' head() to display 10 rows instead of 5


# In[3]:


path


# ## Learning how to read data from DICOM images using pydicom, exploring possible ways and obstacles to complete the task

# Using the files from the provided link, let's use one of the downloaded images to get:
# <br>
# - PatientName 
# - StudyInstanceUID (unique identifier per study)
# - SeriesInstanceUID (unique identifier per series)
# - PatientAge
# - PatientSex
# - InstitutionName
# 
# To help us through the task we will be using <a href="https://pydicom.github.io/pydicom/stable/old/pydicom_user_guide.html" target="_blank">pydicom User Guide</a>.

# Although getting meta information from archived files on Amazon without downloading it seems to be a complected task, let's try a fast and simple approach first, and then decide if we really want to waste time on it.

# In[4]:


url = 'https://s3.amazonaws.com/viz_data/DM_TH.tgz'


# In[5]:


fl_name = 'images_ct.tgz'


# In[6]:


def image_downloader(link):
    r = requests.get(url)
    if r.status_code == 200:
       print ('It worked!')
    else:
       print ('Boo!')    
    with open(fl_name, 'wb') as f:
        f.write(r.content) 
    try:
        extract(fl_name, "out/%s.raw" % (fl_name), ext=".tgz")
    except:
        # could not extract
        print('Sorry, something went wrong')


# In[7]:


image_downloader(url)


# In[8]:


test_image = dcmread(path+'/out/images_ct.tgz.raw/dicom_0405.dcm') #reading file 
test_dict = {
'test_org': test_image.InstitutionName,
'test_name':  test_image.PatientName,
'test_id_study':  test_image.StudyInstanceUID,
'test_id_series': test_image.SeriesInstanceUID,
'test_id_age': test_image.PatientAge,
'tets_gender': test_image.PatientSex
}
for item, values in test_dict.items():
    print(item,': ', values)


# As we were told patient's privacy was protected  by changing it to what it looks like StudyInstanceUID (we only see one example now, so can't be sure). Years are stored in a 4 characters string where first 3 characters are age and the 4th character indicates it is an age - "Y". Sex is stored in a one character string - F for female, and, as we can assume, M for male. 
# <br>
# As for InstitutionName, it is just a string that represents it, we do not see real names as we can assume, again, to protect privacy. StudyInstanceUID and  SeriesInstanceUID are long strings that do not tell us any information now, but might be helpful for the future analyses to group images by study id and series id.

# In[9]:


px.imshow(test_image.pixel_array) #trying plotly express for visualisation


# In[10]:


# testing images printing with good old Matplotlib
plt.imshow(test_image.pixel_array, cmap='bone') 
plt.show()


# In[11]:


print(test_image) #checking what kind of other information files might have


# The elements are described in <a href="https://pydicom.github.io/pydicom/stable/old/base_element.html?highlight=study%20time#core-elements-in-pydicom" target="_blank">pydicom documentation</a>
# <br>
# We can see that apart from UIDs for series and the whole study, we can use Study Date and Study and Series time to double check if we aggregated our data correctly within a DataFrame - providing the time and dates are not fake here for privacy protection. The file's attributes even provide study and series description, what body part was examined, and a lot of medical parameters and measurements. 
# 

# ## Downloading and arranging data from the images

# ### Plan:
# 
# 1. Creating a list of file names
# 2. Arranging images according to their names
# 3. Loop through each image to insert its elements into a dictionary
# 
# 

# In[12]:


#making sure our folder is still stored locally, verifying its name.
import pathlib
sorted(pathlib.Path('.').glob('images_ct.*'))


# In[13]:


folder = path+'/out/images_ct.tgz.raw/'
images = os.listdir(folder)
reading_files = [dcmread(folder+'/'+s,force=True) for s in images] # a list of all 


# In[14]:


test_image.dir("pat") #getting elemenents list form a file


# In[15]:


test_image.dir("pat")[3] #checking if it is possible to extract a specific element 


# In[16]:


reading_files[1].dir("pat") #checking all above per list item


# In[17]:


type(reading_files[1].SeriesTime) #what is the data type for time 


# In[18]:


print('Our folder has {} files'.format(len(reading_files)))


# In[19]:


images_list = []


# In[20]:


for i in range(len(images)):
    try:
        organization =  dcmread(folder+images[i], force=True).InstitutionName
    except:
        organization = ''
    try:
        age = dcmread(folder+images[i], force=True).PatientAge
    except:
        age = ''
    try:
        name = dcmread(folder+images[i], force=True).PatientName
    except:
        name = ''
    try:
        sex = dcmread(folder+images[i], force=True).PatientSex
    except: 
        sex = ''
    try:
        id_study = dcmread(folder+images[i], force=True).StudyInstanceUID
    except:
        id_study = ''
    try:
        id_series = dcmread(folder+images[i], force=True).SeriesInstanceUID
    except:
        id_series = ''
    try:
        series_time = dcmread(folder+images[i], force=True).SeriesTime
    except:
        series_time = ''
    images_dict = {
        'organization': organization,
        'name':  name,
        'id_study':  id_series,
        'id_series': id_series,
        'age': age,
        'sex': sex,
        'series_time': series_time
        }
    images_list.append(images_dict)


# In[21]:


df = pd.DataFrame(images_list)
df.info()


# We got 406 rows from 406 images, so it looks like we did not loose any data. But we might have some broken files or non DICOM files in the set, so it is probably better to check for empty rows and nulls.

# In[22]:


df.sample(5)


# # Generate a list of patients, their age and sex 

# In[23]:


print('We have {} patients in the dataset'.format(df.name.nunique()))


# During data extraction we have seen that some files are not DICOM files, so we might have empty rows and the number of patients is even smaller.

# In[24]:


df.drop_duplicates(subset=['name', 'age', 'sex'])


# As we thought, we have only 6 patients, let's drop empty row to get a clean lits of patients

# In[25]:


list_of_patients = df.drop_duplicates(subset=['name', 'age', 'sex'])


# In[26]:


list_of_patients = list_of_patients.query('name!=""') #filtering out empty rows


# In[27]:


list_of_patients


# # How long does CT <b>scan (not study)</b>  takes on average?

# We need to drop rows with empty data here to make the conversion possible. There are many fields in the files meta information and it is hard to understand which one is the duration. But it looks like it is SeriesTime which is most likely to be in Milliseconds.
# 
# <b>Please, advise if this is the correct field.</b>

# In[28]:


clean_df = df.query('name!="" & series_time !=""')


# In[29]:


clean_df['series_time'] = clean_df['series_time'].astype(float)


# I do not like using .loc, so please ignore the warnings: here it does not mean anything that can break a code.

# In[30]:


clean_df.drop_duplicates(inplace=True)


# In[31]:


print('We have {} distinct scans in the dataset'.format(clean_df.id_series.nunique()))


# In[32]:


print('Scan takes on average  {} in our dataset'.format(clean_df['series_time'].mean()))


# In[33]:


print('If we understood correctly that the field is in Milliseconds, that is {:.2f} minutes'.format(2.4995))


# ## How many different hospitals are in the data?
# 

# In[34]:


print('We have {} hospitals in our data'.format(df.organization.nunique()))


# But in reality we might have lost some data, so let's list them all:

# In[35]:


print('Here are all the hospitals {}'.format(df.organization.unique()))


# As we can see, some files have no data on hospitals names. So, although we migh have 4 distinct hospitals, we only know 3 names.

# # Next, use a DICOM viewer suitable for your OS to view the scans (e.g. horos). anything seems particularly interesting? You're obviously not expected to make a medical diagnosis, just spend 5-10 minutes browsing through the scans and share your general impressions. 
# 
# 

# 1. Some studies have hundreds of images, some - a few dozens. Is number of photos decided by doctors in hospitals and not automated?
# 2. When playing the series of images in Horos, it is possible to notice some kind of pattern (or patterns) in the photos. Are the patterns  used for algorithms? 
# 3. Applying different color scheme gives different (or a new?) pattern. Is coloring important for algorithms?
# 4. The strongest impression is that I do not understand anything looking at the photos even for an hour :-)

# In[ ]:




