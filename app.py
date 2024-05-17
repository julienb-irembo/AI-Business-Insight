import streamlit as st
from openai import OpenAI
from app_config import *
from app_access_db import *
import streamlit_authenticator as stauth
from streamlit_pills import pills
import yaml
from yaml.loader import SafeLoader
with open('auth.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# model = "gpt-3.5-turbo"
model = "gpt-4-turbo"
gpt_base_url = None
# model = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
# gpt_base_url = "http://localhost:1234/v1/"

openai_key = st.secrets["OpenAI_key"]

#---- USER AUTHENTICATION ---
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)
name, authentication_status, username = authenticator.login('main', fields = {'Form name': 'Login'})
profile_picture_url = "https://via.placeholder.com/150"

if authentication_status == False:
   st.error("Username/password is incorrect")

if authentication_status == None:
   st.error("Please enter your username and password")


if authentication_status:
 email = config['credentials']['usernames'][username]['email']
  
# ------------------------------------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------------------------------------
 logo = "img/irembo-gov.svg"
 approved = run_query("SELECT COUNT(*) AS approved_applications_count FROM application JOIN application_state ON application.application_state = application_state.id WHERE application_state.state_code = 'CLOSED_WITH_APPROVAL';" ).values[0][0]
 pending = run_query("SELECT COUNT(*) AS pending_applications_count FROM application JOIN application_state ON application.application_state = application_state.id WHERE application_state.state_code = 'PENDING_APPROVAL';" ).values[0][0]
 rejected = run_query("SELECT COUNT(*) AS pending_applications_count FROM application JOIN application_state ON application.application_state = application_state.id WHERE application_state.state_code = 'CLOSED_WITH_REJECTED';" ).values[0][0]
 rfa = run_query("SELECT COUNT(*) AS pending_applications_count FROM application JOIN application_state ON application.application_state = application_state.id WHERE application_state.state_code = 'PENDING_RESUBMISSION';" ).values[0][0]




 def dashboard_cards():
    st.markdown(
        f"""
        <div style="display:flex; gap:20px; margin-bottom:20px; margin-top:20px;">
            <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; width:50%; display:grid; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <span style='color: #000000; font-size:13px; text-align:center;'>Approved</span>
                <h1 style='color: #0f996d; font-size:36px; text-align:center;'>{approved}</h1>
            </div>
            <div style='background-color: #ffffff;  padding: 20px; border-radius: 10px; width:50%; display:grid; justify-content: center; align-items: center;box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <span style='color: #000000; font-size:13px; text-align:center;'>Request for action</span>
                <h1 style='color: #106ddc; font-size:36px; text-align:center;'>{rfa}</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="display:flex; gap:20px;">
            <div style='background-color: #ffffff;  padding: 20px; border-radius: 10px; width:50%; display:grid; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <span style='color: #000000;font-size:13px; text-align:center;'>Pending</span>
                <h1 style='color: #ffc107; font-size:36px; text-align:center;'>{pending}</h1>
            </div>
            <div style='background-color: #ffffff;  padding: 20px; border-radius: 10px; width:50%; display:grid; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <span style='color: #000000; font-size:13px; text-align:center;'>Rejected</span>
                <h1 style='color: #dc3545; font-size:36px; text-align:center;'>{rejected}</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
 with st.sidebar:
    st.markdown(f'<img src="https://rtn.rw/wp-content/uploads/2019/07/irembo-300x83.png" style="position: fixed; top: 0;width:180px ;text-align: left; padding-top: 20px;"/>', unsafe_allow_html=True)
    st.markdown('#')
    # Today history
    st.header(":blue[Application statistics]")
    dashboard_cards()

    if openai_key is not None and openai_key != '':
            print('Key was added successfully')
    else:
        st.sidebar.error('No key found please add it in the secrets', icon="❌")
    st.markdown("#")
    profile_container = st.container()
    with profile_container:
           col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
            st.image(profile_picture_url, width=50)

    with col2:
            st.markdown(f"""
                <div style="display: flex; flex-direction: column;">
                    <div style="font-size: 18px; color: darkblue; font-weight: bold;">{name}</div>
                    <div style="font-size: 14px; color: gray;">{email}</div>
                </div>
            """, unsafe_allow_html=True)

    with col3:
            authenticator.logout("Logout", "main")
    st.markdown('<div style="position: fixed; bottom: 0; text-align: left; padding-bottom: 20px">Version 0.0.1</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------------------------
# CHAT
# ------------------------------------------------------------------------------------------------

# st.title('Irembo Business Insights AI Assistant')
# st.write(f'Ask any question that can be answer by the LLM {model}.')

 st.title(f'Welcome back, {name}')



 def askQuestion(model=model, question=''):
    if(openai_key == None or openai_key==''):
        print('Please provide the key before')
        return 'LLM API is not defined. Please provide the key before'
    else:
        client = OpenAI(api_key=openai_key, base_url=gpt_base_url)
        model = model
        completion = client.chat.completions.create(
            model=model,
            # messages=query_context,  
            messages=[
                {"role": "system", "content": f'{query_context}'},
                {"role": "user", "content": f'{question}'}
            ],
            temperature=0
        )              
        return completion.choices[0].message.content

 class AssistantMessage:
    def __init__(self):
        self.sql : str
        self.response_data : DataFrame



 def displayAssistantMessage( assistantMessage: AssistantMessage ):
    with st.chat_message("assistant", avatar="img/favicon.png"):
        if isinstance(assistantMessage.response_data, str):
            st.write(assistantMessage.response_data)
        else:
            st.write(assistantMessage.response_data)
    # if hasattr(assistantMessage.response_data, 'columns'):
    #     if assistantMessage.response_data.columns.size == 2:
    #         st.bar_chart(assistantMessage.response_data, x=assistantMessage.response_data.columns[0], y=assistantMessage.response_data.columns[1])
    #     if assistantMessage.response_data.columns.size == 1:
    #         st.metric(label=assistantMessage.response_data.columns[0], value=f'{assistantMessage.response_data.values[0][0]}')
    #     if assistantMessage.response_data.columns.size > 3:
    #         st.table(assistantMessage.response_data)           

# Initialize chat history
 if "messages" not in st.session_state:
     st.session_state.messages = []

# Display chat messages from history on app rerun
 for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        displayAssistantMessage(message["content"])

# Displaying chat description
 if not st.session_state.messages:
        st.markdown(f'<p style="font-size:18px; text-align:center; margin-top:50px; ">I specialize in providing business insights and assisting with various applications. Feel free to ask me anything related to these topics.</p>', unsafe_allow_html=True)
 else:
    st.markdown("#")

# React to user input
 if prompt := st.chat_input("Ask me any question about business at Irembo?"):
     description = None
     with st.status('Running', expanded=True) as status:
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = askQuestion(question=prompt)
        is_query = is_query(response)
        print(is_query)
        if not is_query:
            with st.chat_message("assistant", avatar="img/favicon.png"):
                st.markdown(response)
            # Display assistant response in chat message container
            assistanMsg = AssistantMessage()
            assistanMsg.response_data = response
            st.session_state.messages.append({"role": "assistant", "content": assistanMsg})
            status.update(label='Response of last question', state="complete", expanded=True)
        elif is_query:
            try:
                response_data = run_query(response.replace('```',''))
                # Display assistant response in chat message container
                assistanMsg = AssistantMessage()
                assistanMsg.response_data = response_data
                displayAssistantMessage(assistanMsg)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistanMsg})
                status.update(label='Response of last question', state="complete", expanded=True)
            except Exception as e:
                error_message = "Am sorry I can't process your request right now. Please ask me another question."
                with st.chat_message("assistant", avatar="img/favicon.png"):
                    st.error(error_message)
                assistanMsg = AssistantMessage()
                assistanMsg.response_data = error_message
                st.session_state.messages.append({"role": "assistant", "content": assistanMsg})
                status.update(label='Error', state="error", expanded=True)
