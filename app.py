import streamlit as st
from openai import OpenAI
from app_config import *
from app_access_db import *



# model = "gpt-3.5-turbo"
model = "gpt-4-turbo"
gpt_base_url = None
# model = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
# gpt_base_url = "http://localhost:1234/v1/"

openai_key = st.secrets["OpenAI_key"]



# ------------------------------------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------------------------------------
with st.sidebar:
    with st.empty():
        st.image("img/irembo-gov.svg", )

    # Today history
    st.subheader(":blue[Approved applications ]")
    st.subheader(run_query("SELECT COUNT(*) FROM application WHERE state = 'APPROVED';" ).values[0][0])
    st.subheader(":blue[Pending applications ]")
    st.subheader(run_query("SELECT COUNT(*) FROM application WHERE state = 'PENDING_PAYMENT';" ).values[0][0])
    st.subheader(":blue[Rejected applications ]")
    st.subheader(run_query("SELECT COUNT(*) FROM application WHERE state = 'REJECTED';" ).values[0][0])

    if openai_key is not None and openai_key != '':
            print('Key was added successfully')
    else:
        st.sidebar.error('No key found please add it in the secrets', icon="❌")
    


# ------------------------------------------------------------------------------------------------
# CHAT
# ------------------------------------------------------------------------------------------------

# st.title('Irembo Business Insights AI Assistant')
# st.write(f'Ask any question that can be answer by the LLM {model}.')
name = "Officer"
st.title('Welcome back, ' + name)



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
            st.text(assistantMessage.response_data)
        else:
            st.code(assistantMessage.response_data, language='markdown')
    if hasattr(assistantMessage.response_data, 'columns'):
        if assistantMessage.response_data.columns.size == 2:
            st.bar_chart(assistantMessage.response_data, x=assistantMessage.response_data.columns[0], y=assistantMessage.response_data.columns[1])
        if assistantMessage.response_data.columns.size == 1:
            st.metric(label=assistantMessage.response_data.columns[0], value=f'{assistantMessage.response_data.values[0][0]}')
        if assistantMessage.response_data.columns.size > 3:
            st.table(assistantMessage.response_data)           


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

# React to user input
if prompt := st.chat_input("Ask me any question about business at Irembo?"):
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