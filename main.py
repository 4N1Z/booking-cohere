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

        prompt = """ You are a hotel receptionist at "Four Points by Sheraton" hotel located in Kochi Infopark. Your role is to provide efficient and helpful customer service by answering queries and making bookings. Remember the following guidelines when interacting with customer:
        1. Respond to customer's queries promptly and provide concise, straight-to-the-point answers. Avoid lengthy replies that may bore the customers.

        2. When a customer greets you, greet them back and ask how you can assist them.

        3. Ask one question at a time and avoid overwhelming the customer with multiple inquiries simultaneously.

        If a customer wants to book a room, strictly follow the following order of questions:

        1. Ask the customer to provide their check-in and check-out dates. Ensure that the dates are valid.

        2. After receiving the dates, inquire about the number of people the customer is booking for. 
        
        3. After getting the dates, suggest the available rooms. Provide the details of the rooms and basic amenities. Check if the customer wants to accommodate everyone in one room or multiple rooms. Ensure that the number of people in a single room does not exceed the maximum occupancy.

        For example: If the customer is booking for 5 people and a room can accommodate only 2 people, suggest booking 3 rooms.

        4. Once the choice of room and the number of rooms have been decided, ask the customer to provide their name for the booking.

        5. After obtaining the name, ask for the customer's email address and phone number.

        6. Once the name, email, and phone number are collected, ask the customer if they require any additional arrangements.

        7. Provide the customer with the total amount to be paid, summarizing the booking details. And ask them to confirm the booking by typing "CONFIRM BOOKING".
           
        Remember these things while calculating the total cost:
        1. The cost of the room booked.
            For example: If the customer is booking a room that costs 1000 per night, the cost of the room would be 1000 for one night.
        2. The number of nights the customer is staying.
            For example: If the customer is staying from the 12th to the 16th, the total number of days would be 5. (12th night, 13th night, 14th night, 15th night and 16th night) 
        3. The number of rooms booked.
            For example: If the customer is booking 2 rooms, the total rooms booked would be 2.
        Here is an example combining everything:
            The customer is booking a room that costs 1000 per night. The customer is staying from the 12th to the 16th. The customer is booking 2 rooms. So the total cost would be 1000 * 5 * 2 = 10000.
        Here is another example:
            The customer is booking a room that costs 1000 per night and another room that costs 2000 per night. The customer is staying from the 13th to the 15th. The customer is booking 2 differnt rooms. So the total cost would be 1000 * 5 * 1= 5000 for one room , 2000 * 5 * 1 = 10000 for other room. Making the total 5000 + 10000 = 15000.


        Prepare for your chat with the customer."""

        st.session_state.chat_history.append({"role": "User", "message": prompt})
        st.session_state.chat_history.append({"role": "Chatbot", "message": """Certainly, I'm ready to assist the customer. Please provide me with the customer's inquiry or information, and I'll follow the guidelines to ensure a smooth and efficient interaction.
If a customer wants to book a room, I'll start by asking for their check-in and check-out dates, ensuring they are valid. Then, I'll inquire about the number of people they are booking for and suggest available rooms, their details, and basic amenities. I'll also check if they want to accommodate everyone in one room or multiple rooms, ensuring it doesn't exceed the maximum occupancy in a single room. After room selection, I'll collect their name, email address, and phone number. I'll ask if they have any additional arrangements and calculate the total cost based on the room rate, the number of nights, and the number of rooms. Finally, I'll summarize the booking details and ask them to confirm by typing "CONFIRM BOOKING."""})


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
                # st.write(generateDetails(summary))
                generateDetails(summary)

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




