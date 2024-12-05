import streamlit as st
from textblob import TextBlob
import time
from streamlit_lottie import st_lottie
import requests
from dotenv import load_dotenv
import os
import demoji
import pandas as pd

load_dotenv()


###############################get requests ######################################

def function_request_comments(my_api_link):
  req = requests.get(my_api_link)
  if(req.status_code != 200):
    return None
  return req.json()
  
  
def request_lottie(url):
  r = requests.get(url)
  if(r.status_code != 200):
    return None
  return r.json()

################################################################################



##########################################Progress bar #########################################  
  
def show_first_progress_bar(value1): 
  value1 = value1*100
  value1 = round(value1, 2)
  
  progress_text = "Positive = " + str(value1) + "%"
  my_bar = st.progress(0, text=progress_text)

  for percent_complete in range(round(value1)):
      time.sleep(0.0001)
      my_bar.progress(percent_complete + 1, text=progress_text)  
 
      
def show_second_progress_bar(value2):
  
  value2 = value2*100
  value2 = round(value2, 2)
  
  progress_text = "Neutral = " + str(value2) + "%"
  my_bar = st.progress(0, text=progress_text)

  for percent_complete in range(round(value2)):
      time.sleep(0.0001)
      my_bar.progress(percent_complete + 1, text=progress_text)
      
      
def show_third_progress_bar(value3):
  
  value3 = value3*100
  value3 = round(value3, 2)
  
  progress_text = "Negative = " + str(value3) + "%"
  my_bar = st.progress(0, text=progress_text)

  for percent_complete in range(round(value3)):
      time.sleep(0.0001)
      my_bar.progress(percent_complete + 1, text=progress_text)


#######################################################################################################


def generate_video_id(url_input):
   
  url_input = url_input.strip(); 
  
  if( ("https://" in url_input) and (url_input.index("https://") == 0) ):
    url_input = url_input[8:]
  elif( ("http://" in url_input) and (url_input.index("http://") == 0) ):
    url_input = url_input[7:]
    
  if( ("www." in url_input) and (url_input.index("www.") == 0) ):
    url_input = url_input[4:]
  
  print(url_input)
  video_id = ""
  
  if(("youtube" in url_input)):
    video_id = url_input[20:]
    
  elif(("youtu.be" in url_input)):
    video_id = url_input[9:]
  
  print(video_id)
  return video_id
  
  

def generate_api_link(my_video_id):
  
  api_link = "https://www.googleapis.com/youtube/v3/commentThreads?"
  api_link += "key=" + os.getenv('GOOGLE_API_KEY')
  api_link += "&videoId=" + my_video_id
  api_link += "&part=snippet&part=replies"
  return api_link


def evaluate_comments(response):
  list_comments = []
  for comment_object in response['items']:
    
    single_comment = (comment_object['snippet']['topLevelComment']['snippet']['textOriginal'])  
    if(len(demoji.findall(single_comment).values()) != 0):
      for comment in demoji.findall(single_comment).values():
        single_comment += " (" + comment + ") "   
    list_comments.append(single_comment)
    
    if(comment_object['snippet']['totalReplyCount'] == 1):
      single_reply = (comment_object['replies']['comments'][0]['snippet']['textOriginal'])
      if(len(demoji.findall(single_reply).values()) != 0):
        for reply in demoji.findall(single_reply).values():
          single_reply += " (" + reply + ") "
      list_comments.append(single_reply)          
        
  return list_comments


def sentiment_analysis(list_of_comments):
  pol_sub = []
  for comment in list_of_comments:
    text = TextBlob(comment)
    pol_sub.append([text.sentiment.polarity, text.sentiment.subjectivity])
  return pol_sub


def display_graphs(list_of_pol_sub):
  chart_data = pd.DataFrame(
    list_of_pol_sub,
    columns=['Polarity', 'Subjectivity'])
  st.area_chart(chart_data)
    
  chart_data2 = pd.DataFrame(
    list_of_pol_sub,
    columns=['Polarity', 'Subjectivity'])
  st.bar_chart(chart_data2)
    

def calculate_percentages(list_of_pol_sub):
  n = len(list_of_pol_sub)
  pos = 0
  neg = 0
  neu = 0
  for row in list_of_pol_sub:
    if(row[0] > 0):
      pos += 1 
    elif(row[0] < 0):
      neg += 1 
    elif(row[0] == 0):
      neu += 1 

  array = []
  array.append(pos/n)
  array.append(neu/n)
  array.append(neg/n)
  return array
  

def display_table(list_of_comments, list_of_pol_sub):
  
  with st.expander("View individual comment analysis"):
    
    n = len(list_of_comments)
    
    for i in range(n):
      with st.container():
        
        st.caption("Comment: " + list_of_comments[i])
        st.caption("Polarity: " + str(round(list_of_pol_sub[i][0], 2)) + " Subjectivity: " + str(round(list_of_pol_sub[i][1], 2)))
        if(list_of_pol_sub[i][0] > 0):
            st.caption("Analysis: " + "Positive")
          
        elif(list_of_pol_sub[i][0] < 0):
          st.caption("Analysis: " + "Negative")
        
        elif(list_of_pol_sub[i][0] == 0):
          st.caption("Analysis: " + "Neutral")
          
        st.divider()




###################################################### control functions #################################################
  
def function_control(url_input):
  
  my_video_id = generate_video_id(url_input)
  my_api_link = generate_api_link(my_video_id)
  response = function_request_comments(my_api_link)
  
  if(response == None):
    st.error('Please enter valid url')
    return
  
  list_of_comments = (evaluate_comments(response))
  list_of_pol_sub = (sentiment_analysis(list_of_comments))
  array_of_percentages = calculate_percentages(list_of_pol_sub)
  
  show_first_progress_bar(array_of_percentages[0])
  show_second_progress_bar(array_of_percentages[1])
  show_third_progress_bar(array_of_percentages[2])
  st.divider()
  display_graphs(list_of_pol_sub)
  st.divider()
  display_table(list_of_comments, list_of_pol_sub)


################################################# front end ################################################






with st.container():
  left_column, right_column = st.columns((1,5))

  with left_column:
    lottie_animation = request_lottie("https://assets9.lottiefiles.com/private_files/lf30_xk0j3gld.json")
    st_lottie(lottie_animation, height= 75)
  
  with right_column:
    st.write("""
          # Comment Sense
          ##### Analyze with just a click
          """)
  
  st.divider()
    
    


url_input = st.text_input("Enter URL")

if st.button('Analyze'):
  if(url_input == ""):
    st.error('Please enter video URL')
  else:
    st.divider()
    function_control(url_input)
  
  # comments_json_file = function_comments()
  
  # for comment_object in comments_json_file['items']:
  #   print(comment_object['snippet']['topLevelComment']['snippet']['textOriginal'])


#######################################main function####################################




https://www.hackerrank.com/tests/9f33d02h0pg/login?b=eyJ1c2VybmFtZSI6InZpc2hhbC5zaGFybWExMTcwNEBnbWFpbC5jb20iLCJwYXNzd29yZCI6ImJkZWZhNWIyIiwiaGlkZSI6dHJ1ZSwiYWNjb21tb2RhdGlvbnMiOnsiYWRkaXRpb25hbF90aW1lX3BlcmNlbnQiOjB9fQ==
