import cohere
import streamlit as st
import os
import requests
import webbrowser
from bs4 import BeautifulSoup
import json
import re

co = cohere.Client('oT6jA28iJxq79ZT1ihQrDhjwCdkMsIFGfFEbX7PL') 

# co = cohere.Client(os.environ["COHERE_API_KEY"]) 
def formattingForSummarizer(text):
    for each in text :
        if (each == "'") :
            text = text.replace(each, "")
        if(each == "`"):
            text = text.replace(each, "")    
    
    text = text.replace('\n', ' ').replace('\r', '').replace('\t', ' ')
    return text


def summarizer (text):

    CleanText = formattingForSummarizer(str(text))
    # prompt_template = "Summarize the given content into 5 paragraph response of `MORE THAN 200 WORDS` each. The content is : " + ' ' + CleanText 
    summarizer_prompt  = "You are the manager of a hotel and you're task is to summarize the given content: that is the details of booking into the format needed for billing.. "
    response = co.summarize( 
          text=CleanText,
          length='long',
          format='bullets',
          model='summarize-xlarge',
          additional_command= summarizer_prompt,
          temperature=0.3,
        ) 
    print(response.summary)
    return response.summary

def generateKBase(largeData):

    rqdFormat =  [
        {
        "title": " ",
        "snippet": " "
        },
    ]
    FormatPrompt = "You should extract the given details text: " + largeData +" into this  \n: "+ " "+ str(rqdFormat) + "\n JSON FORMAT and populate the corresponding values from text : The snippet can contain the large amount of tokens.Don't shortent the content" 
    response = co.generate(
        # text,
        model='command-nightly',
        prompt=FormatPrompt,
        temperature=0.3,
        return_likelihoods =  None,
        # finish_reason= COMPLETE,
        # token_likelihoods= None,
    )
    print(response.generations[0].text)
    # sendAPIReg(response.generations[0].text)



def generateDetails(text):

    JSONFormat = {
        "name": " ",
        "number": 1234567890,
        "email": " ",
        "destination": "KOCHI",
        "check_in_date": " ",
        "check_out_date": " ",
        "unique_id": "abc123"
    }

    JSONFormatPrompt = "You should extract the given details from the text: " + text +" into this  \n: "+ " "+ str(JSONFormat) + "\n JSON FORMAT and populatea corresponding values from text : .If you couldn't find all the answer to the fileds then do fill it with dummy values instead. Use this format for datess instead: YYYY-MM-DD. DONOT LEAVE ANY FILED BLANK AND NO OTHER OUTPUT REQUIRED. The text is :" + text + 'DONT GENERTATE ANY REPLY OTHER THAN THE JSON STRING'
    response = co.generate(
        # text,
        model='command-nightly',
        prompt=JSONFormatPrompt,
        temperature=0.3,
        return_likelihoods =  None,
    )
    # st.write("The API Response to send : ")
    # st.write(response.generations[0].text)
    print(response.generations[0].text) 
    sendAPIReg(response.generations[0].text)

def ifJSONComplete(text):
    required_fields = ["name", "number", "email", "destination", "check_in_date", "check_out_date", "unique_id"]
    incoming_json = text
    
    for field in required_fields:
        if field not in incoming_json or not incoming_json[field]:
            return False
        
    print("________________JSON is complete____________")
    return True


# Function to take only the JSON from input string
def getJSONReponse(input_string):
    
    start_index = input_string.find('{')
    end_index = input_string.find('}') + 1
    json_string = input_string[start_index:end_index]

    json_data = json.loads(json_string)
    print("\nExtracted JSON: \n")
    print(json.dumps(json_data, indent=2))

    # Convert the extracted content to JSON
    # try:
    #     json_data = json.loads(json_string)
    #     print("\nExtracted JSON: \n")
    #     print(json.dumps(json_data, indent=2))  # Print formatted JSON
    # except json.JSONDecodeError as e:
    #     print("Error decoding JSON:", e)

    return json_data


def sendAPIReg(reponse_string):

    payload = getJSONReponse(reponse_string) 

    if (ifJSONComplete(payload)):

        api_endpoint = "https://travel-llm-api.vercel.app/checkout/"
        # Make a POST request to the API endpoint
        response = requests.post(api_endpoint, data=payload)

        # Check the status code of the response
        if response.status_code == 201:
            api_response = json.loads(response.text)
            link = api_response.get("link", None)
            print(link)
            webbrowser.open(link)
            # print("API Response: \n ", response.text)
        else:
            # API call failed, print the error status code and response content
            print("API Error:", response.status_code, response.text)
    else :
        print("_______JSON is not complete_______")


def main():
    text = """The customer wants to book a 1-bedroom suite for 2 days
The check-in date is from 13th September
The suite costs ₹12600 and comes with a king bed, executive lounge access, a shower/tub combination, and amenities like high-speed internet and 2 TVs.
Nothing was mentioned about extras."""

    # generateKBase(data)

    JSONFormat = {
        "name": "TEST DATA ",
        "number": 1234567890,
        "email": "1232@gmail.com ",
        "destination": " TRVM",
        "check_in_date": "2002-02-4",
        "check_out_date": "2002-02-6",
        "unique_id": "abc123"
    }


    # sendAPIReg(JSONFormat)
    generateDetails(text)

# Add the summary
if __name__ == "__main__":
    main()

