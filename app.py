import streamlit as st
from openai import OpenAI
from app_config import *
from app_access_db import *
from streamlit_pills import pills



# model = "gpt-3.5-turbo"
model = "gpt-4o"
gpt_base_url = None
# model = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
# gpt_base_url = "http://localhost:1234/v1/"

openai_key = st.secrets["OpenAI_key"]



# ------------------------------------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------------------------------------
logo = "img/irembo-gov.svg"
approved = run_query("SELECT COUNT(*) AS count FROM application a JOIN processing_location pl ON a.processing_location = pl.id JOIN application_service aps ON a.application_service = aps.id JOIN service s ON aps.service = s.id JOIN service_group sg ON aps.service_group = sg.id JOIN service_category sc ON aps.service_category = sc.id JOIN institution i ON aps.institution = i.id JOIN application_requester ar ON a.application_requester = ar.id JOIN application_processor ap ON a.application_processor = ap.id JOIN currency c ON a.application_currency = c.id JOIN application_channel ac ON a.application_channel = ac.id JOIN application_state ast ON a.application_state = ast.id JOIN application_processing_phase apph ON a.application_processing_phase = apph.id JOIN payment_transaction pt ON a.payment_transaction = pt.id WHERE ast.state_code = 'CLOSED_WITH_APPROVAL' AND s.is_service_suspended = FALSE AND sg.is_group_suspended = FALSE;" ).values[0][0]
pending = run_query("SELECT COUNT(*) AS count FROM application a JOIN processing_location pl ON a.processing_location = pl.id JOIN application_service aps ON a.application_service = aps.id JOIN service s ON aps.service = s.id JOIN service_group sg ON aps.service_group = sg.id JOIN service_category sc ON aps.service_category = sc.id JOIN institution i ON aps.institution = i.id JOIN application_requester ar ON a.application_requester = ar.id JOIN application_processor ap ON a.application_processor = ap.id JOIN currency c ON a.application_currency = c.id JOIN application_channel ac ON a.application_channel = ac.id JOIN application_state ast ON a.application_state = ast.id JOIN application_processing_phase apph ON a.application_processing_phase = apph.id JOIN payment_transaction pt ON a.payment_transaction = pt.id WHERE ast.state_code = 'PENDING_APPROVAL' AND s.is_service_suspended = FALSE AND sg.is_group_suspended = FALSE;" ).values[0][0]
rejected = run_query("SELECT COUNT(*) AS count FROM application a JOIN processing_location pl ON a.processing_location = pl.id JOIN application_service aps ON a.application_service = aps.id JOIN service s ON aps.service = s.id JOIN service_group sg ON aps.service_group = sg.id JOIN service_category sc ON aps.service_category = sc.id JOIN institution i ON aps.institution = i.id JOIN application_requester ar ON a.application_requester = ar.id JOIN application_processor ap ON a.application_processor = ap.id JOIN currency c ON a.application_currency = c.id JOIN application_channel ac ON a.application_channel = ac.id JOIN application_state ast ON a.application_state = ast.id JOIN application_processing_phase apph ON a.application_processing_phase = apph.id JOIN payment_transaction pt ON a.payment_transaction = pt.id WHERE ast.state_code = 'CLOSED_WITH_REJECTED' AND s.is_service_suspended = FALSE AND sg.is_group_suspended = FALSE;" ).values[0][0]
rfa = run_query("SELECT COUNT(*) AS count FROM application a JOIN processing_location pl ON a.processing_location = pl.id JOIN application_service aps ON a.application_service = aps.id JOIN service s ON aps.service = s.id JOIN service_group sg ON aps.service_group = sg.id JOIN service_category sc ON aps.service_category = sc.id JOIN institution i ON aps.institution = i.id JOIN application_requester ar ON a.application_requester = ar.id JOIN application_processor ap ON a.application_processor = ap.id JOIN currency c ON a.application_currency = c.id JOIN application_channel ac ON a.application_channel = ac.id JOIN application_state ast ON a.application_state = ast.id JOIN application_processing_phase apph ON a.application_processing_phase = apph.id JOIN payment_transaction pt ON a.payment_transaction = pt.id WHERE ast.state_code = 'PENDING_RESUBMISSION' AND s.is_service_suspended = FALSE AND sg.is_group_suspended = FALSE;" ).values[0][0]




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
    st.markdown('<div style="position: fixed; bottom: 0; text-align: left; padding-bottom: 20px">Version 0.0.1</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------
# CHAT
# ------------------------------------------------------------------------------------------------

image = "img/favicon.png"
name = "Officer"


col1, col2 = st.columns([1, 6]) 
with col1:
    st.image(image, width=80)
with col2:
    st.title('Welcome back, ' + name)


def build_query_context(messages):
    history = "\n".join([f"User: {msg['content']}" if msg["role"] == "user" else f"Assistant: {msg['content']}" for msg in messages])
    return query_context + history

def askQuestion(model=model, question='', messages=[]):
    if openai_key is None or openai_key == '':
        print('Please provide the key before')
        return 'LLM API is not defined. Please provide the key before'
    else:
        client = OpenAI(api_key=openai_key, base_url=gpt_base_url)
        query_context = build_query_context(messages)

        print('the query context is',query_context)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": query_context},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        return completion.choices[0].message.content

class AssistantMessage:
    def __init__(self, sql: str = "", response_data=None):
        self.sql = sql
        self.response_data = response_data

    def to_dict(self):
        if isinstance(self.response_data, DataFrame):
            response_data = self.response_data.to_dict()
        else:
            response_data = self.response_data
        return {
            "sql": self.sql,
            "response_data": response_data
        }

    @staticmethod
    def from_dict(data):
        response_data = data.get("response_data")
        if isinstance(response_data, dict):
            response_data = DataFrame.from_dict(response_data)
        return AssistantMessage(
            sql=data.get("sql", ""),
            response_data=response_data
        )

def displayAssistantMessage(assistantMessage: AssistantMessage, prompt: str):
    with st.chat_message("assistant", avatar="img/favicon.png"):
        if isinstance(assistantMessage.response_data, str):
            st.write(assistantMessage.response_data)
        else:
            st.write(assistantMessage.response_data)
        
        if 'trend' in prompt.lower() or 'chart' in prompt.lower():
            st.bar_chart(assistantMessage.response_data, x=assistantMessage.response_data.columns[0], y=assistantMessage.response_data.columns[1])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        assistantMessage = AssistantMessage.from_dict(message["content"])
        displayAssistantMessage(assistantMessage, '')

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

        # Use the messages history to keep the context
        response = askQuestion(question=prompt, messages=st.session_state.messages)
        is_query = is_query(response)
        print(is_query)
        if not is_query:
            with st.chat_message("assistant", avatar="img/favicon.png"):
                st.markdown(response)
            # Display assistant response in chat message container
            assistanMsg = AssistantMessage(response_data=response)
            st.session_state.messages.append({"role": "assistant", "content": assistanMsg.to_dict()})
            status.update(label='Response of last question', state="complete", expanded=True)
        elif is_query:
            try:
                response_data = run_query(response.replace('```',''))
                # Display assistant response in chat message container
                assistanMsg = AssistantMessage(response_data=response_data)
                displayAssistantMessage(assistanMsg, prompt)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistanMsg.to_dict()})
                status.update(label='Response of last question', state="complete", expanded=True)
            except Exception as e:
                error_message = "Am sorry I can't process your request right now. Please ask me another question."
                with st.chat_message("assistant", avatar="img/favicon.png"):
                    st.error(error_message)
                assistanMsg = AssistantMessage(response_data=error_message)
                st.session_state.messages.append({"role": "assistant", "content": assistanMsg.to_dict()})
                status.update(label='Error', state="error", expanded=True)
