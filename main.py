import streamlit as st
from typing import Literal
from dataclasses import dataclass
import cohere 
from summarization import summarizer, generateDetails


co = cohere.Client(st.secrets["COHERE_API_KEY"]) 

# Streamlit header
st.set_page_config(page_title="Booking LLM - An LLM-powered chat bot")
st.title("Booking LLM")
st.write("To confirm your booking, type 'Confirm Booking'")

# laoding styles.css
def load_css():
    with open("static/styles.css", "r")  as f:
        css = f"<style>{f.read()} </style>"
        st.markdown(css, unsafe_allow_html = True)


docs =  [
    {           
      "title": "Four Points by Sheraton Kochi Infopark",
      "snippet": "Four Points by Sheraton Kochi Infopark, located in Kakkanad, Kochi, Kerala, offers a luxurious stay with spacious rooms and exceptional amenities. Experience modern elegance and convenience in the heart of the city. Book now and explore nearby attractions, museums, and shopping districts."
    },
    {
      "title": "THe name of the hotel is ",
      "snippet": "Four Points by Sheraton Kochi Infopark, located in Kakkanad, Kochi, Kerala, offers a luxurious stay with spacious rooms and exceptional amenities. Experience modern elegance and convenience in the heart of the city. Book now and explore nearby attractions, museums, and shopping districts."
    },
    {
      "title": "Twin/Twin Deluxe Guest Room",
      "snippet": "The Twin/Twin Deluxe Guest Room features 2 beds, air-conditioning, complimentary high-speed internet, and a 49in/124cm LED TV. Accommodating up to 3 guests, it offers a comfortable stay at a rate of ₹7400."
    },
    {
      "title": "1-Bedroom Suite with Executive Lounge Access",
      "snippet": "Indulge in luxury with the 1-Bedroom Suite offering a King Bed, access to the Executive Lounge, and amenities like complimentary high-speed internet and 2 TVs. Located on a high floor, enjoy a relaxing stay at ₹11600."
    },
    {
      "title": "1-Bedroom Suite with Executive Lounge Access, Shower and Tub Combination",
      "snippet": "Experience ultimate comfort in the 1-Bedroom Suite with a King Bed, Executive Lounge Access, and both shower and tub combination. Enjoy amenities like high-speed internet, 2 TVs, and a luxurious stay for ₹12600."
    },
    {
        "title": "CONFIRM BOOKING",
        "snippet" : "Give THe summary of the booking details so far",
        "Url" : "Also if confirm booking show this link https://bento.me/aniz",
        "message" : "Summarize the conversation so far and ask for confirmation"
    },
  ]

def initialize_session_state() :
    
    # Initialize a session state to track whether the initial message has been sent
    if "initial_message_sent" not in st.session_state:
        st.session_state.initial_message_sent = False

    # Initialize a session state to store the input field value
    if "input_value" not in st.session_state:
        st.session_state.input_value = ""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
        # prompt = """You are a Hotel Receptionist at "Four Points by Sheraton" hotel located Kochi Infopark. You answer all queries about the hotel and also make bookings at the hotel. There is a user, who has some questions about this topic that relate to booking room at the hotel.
        # The receptionist is able to answer the user's questions. The receptionist is able to keep the conversation focused on the topic  and the questions being asked that provide relevant information to the user. The closer the receptionist can get to answering the user's questions, the more helpful the receptionist will be to the user.The receptionist moves to next question and without showing previous confirmed information, just the next question to make it more succint.
        # Receptionist answer to user questions should not contain the user previously saved answers, just ask the next question only.
        # Receptionist do not bore the customers with long replies. The receptionist provide answers which are simple and straight to the point.
        
        # - receptionist will greet the user with a welcome message when the customer says Hi.
        # - receptionist behaves in a friendy manner. Behaves in a postive attitude.
        # - receptionist after asking questions never add anything else after the question mark of that question. We will wait for user input.
        # - receptionist never answers for user. receptionist always wait for user input.
        # - receptionist can't add the expected user response to question in his answer.
        # - receptionist never adds anything else such as an answer after the question mark of questions he asks.
        # - receptionist never adds a response after you ask a question. Wait for user input always.
        # - receptionist Never ask all questions at the same time.

        # These are the questions receptionist need to ask. The receptionist need to ask always all of them. Always ask one question at a time.
        # 1 - What is your name?
        # 2 - When are you arriving? receptionist need to ask the start and end date for the staying in the hotel. It's required so user need to fill in both dates. AI assitant also need to confirm that date is a valid date if not ask for a valid date to user again. Save date with timestamp.
        # 3 - How many people are there? Do not ask specifically if there are children or not. Just ask how many people are there. If there are children, user will say it. Save the number of people.
        # 4 - What type of room do you want? receptionist needs to offer all the kinds of room available in the hotel.
        # 5 - Ask user if he wants something extra to be arranged.

        # After asking all the questions, receptionist need to confirm the booking. If user says yes, then confirm the booking by displaying the booking details back to user in a formatted way. If user says no, then cancel the booking and start over. 
        # Next chat onwards will be receptionist's chat with the customer. """

        prompt = """You are a AI assistant of "Four Points Hotel" located at Kochi Infopark. You will answer any queries related to the hotel. You should always through out the conversation act accordingly. Take note that, you have been provided with documents and citations, 'documents:'. Do not speak outside this context.
            You should help customers to book rooms at the hotel. Gather all the necessary information such as name, date of check-in and check-out, number of people, type of room, and any extras they may want to add to their stay. 
            Ask these questions one after another. DO NOT ASK EVERYTHING AT ONCE. Get the information one at a time.
            Finally when it is time to book, ask the customer to confirm the booking. If they say yes, then confirm the booking by displaying the booking details back to them in a formatted way. If they say no, then cancel the booking and start over.
            If you don't know the answer to any query, just say you don't know. DO NOT try to make up an answer.
            If the question is not related to the context, politely respond that you are tuned to only answer questions that are related to the context. GIVE SHORT AND CONSICE ANSWER ONLY :"""

        st.session_state.chat_history.append({"role": "User", "message": prompt})
        st.session_state.chat_history.append({"role": "Chatbot", "message": "Yes understood, I will act accordingly, and will be polite, short and to the point."})


#Callblack function which when activated calls all the other
#functions 

def on_click_callback():

    load_css()
    customer_prompt = st.session_state.customer_prompt

    if customer_prompt:
        
        st.session_state.input_value = ""
        st.session_state.initial_message_sent = True

        with st.spinner('Generating response...'):  

            llm_response = co.chat( 
                message=customer_prompt,
                documents=docs,
                model='command',
                temperature=0.5,
                # return_prompt=True,
                chat_history=st.session_state.chat_history,
                prompt_truncation = 'auto',
                # stream=True,
            ) 

            if "confirm booking" in customer_prompt.lower():
                summary = summarizer(st.session_state.chat_history)
                # print(summary)
                # Add content to the sidebar
                st.sidebar.title("Summary")
                st.sidebar.write(summary)
                st.write(generateDetails(summary))

                # CREATE A NLP TO EXTRACT THE DETAILS FROM THE SUMMARY
                # llm_response.text = llm_response.text +  "  https://bento.me/aniz"
                
        st.session_state.chat_history.append({"role": "User", "message": customer_prompt})
        st.session_state.chat_history.append({"role": "Chatbot", "message": llm_response.text})

            

def main():

    initialize_session_state()
    chat_placeholder = st.container()
    prompt_placeholder = st.form("chat-form")

    with chat_placeholder:
        for chat in st.session_state.chat_history[2:]:
            if chat["role"] == "User":
                msg = chat["message"]
            else:
                msg = chat["message"]

            div = f"""
            <div class = "chatRow 
            {'' if chat["role"] == 'Chatbot' else 'rowReverse'}">
                <img class="chatIcon" src = "app/static/{'elsa.png' if chat["role"] == 'Chatbot' else 'admin.png'}" width=32 height=32>
                <div class = "chatBubble {'adminBubble' if chat["role"] == 'Chatbot' else 'humanBubble'}">&#8203; {msg}</div>
            </div>"""
            st.markdown(div, unsafe_allow_html=True)
            
        
    with st.form(key="chat_form"):
        cols = st.columns((6, 1))
        
        # Display the initial message if it hasn't been sent yet
        if not st.session_state.initial_message_sent:
            cols[0].text_input(
                "Chat",
                placeholder="Hello, how can I assist you?",
                label_visibility="collapsed",
                key="customer_prompt",
            )  
        else:
            cols[0].text_input(
                "Chat",
                value=st.session_state.input_value,
                label_visibility="collapsed",
                key="customer_prompt",
            )

        cols[1].form_submit_button(
            "Ask",
            type="secondary",
            on_click=on_click_callback,
        )


    st.session_state.input_value = cols[0].text_input


if __name__ == "__main__":
    main()




