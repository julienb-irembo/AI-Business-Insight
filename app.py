import streamlit as st
from openai import OpenAI
from app_config import *
from app_access_db import *
import plotly.express as px 
import pandas as pd

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

# Cache the queries
@st.cache_data
def get_application_counts():
    approved = run_query("SELECT COUNT(*) AS count FROM table_vone_application WHERE application_state = 'APPROVED'").values[0][0]
    pending = run_query("SELECT COUNT(*) AS count FROM table_vone_application WHERE application_state = 'PENDING'").values[0][0]
    rejected = run_query("SELECT COUNT(*) AS count FROM table_vone_application WHERE application_state = 'REJECTED'").values[0][0]
    rfa = run_query("SELECT COUNT(*) AS count FROM table_vone_application WHERE application_state = 'RFA'").values[0][0]
    return approved, pending, rejected, rfa

# Get the cached data
approved, pending, rejected, rfa = get_application_counts()

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
    history = ""
    for msg in messages:
        if msg["role"] == "user":
            history += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            assistant_msg = AssistantMessage.from_dict(msg["content"])
            if assistant_msg.sql:
                history += f"Assistant (SQL): {assistant_msg.sql}\n"
            else:
                history += f"Assistant: {assistant_msg.response_data}\n"
    return query_context + history

def askQuestion(model=model, question='', messages=[]):
    if openai_key is None or openai_key == '':
        print('Please provide the key before')
        return 'LLM API is not defined. Please provide the key before'
    else:
        client = OpenAI(api_key=openai_key, base_url=gpt_base_url)
        query_context = build_query_context(messages)

        print('the query context is', query_context)
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
    def __init__(self, prompt: str = "", sql: str = "", message_type: str = "", response_data=None):
        self.sql = sql
        self.response_data = response_data
        self.prompt = prompt
        self.message_type = message_type

    def to_dict(self):
        if isinstance(self.response_data, DataFrame):
            response_data = self.response_data.to_dict()
        else:
            response_data = self.response_data
        return {
            "sql": self.sql,
            "prompt": self.prompt,
            "message_type": self.message_type,
            "response_data": response_data
        }

    @staticmethod
    def from_dict(data):
        response_data = data.get("response_data")
        if isinstance(response_data, dict):
            response_data = DataFrame.from_dict(response_data)
        return AssistantMessage(
            sql=data.get("sql", ""),
            message_type=data.get("message_type", ""),
            prompt=data.get("prompt", ""),
            response_data=response_data
        )

def format_column_name(column_name):
    return column_name.replace("_", " ").title()

def rename_columns(df):
    df.columns = [format_column_name(col) for col in df.columns]
    return df

def suggest_chart_type(df, prompt):
    # Keywords to determine the type of chart
    if "trend" in prompt.lower() or "time series" in prompt.lower():
        return "Line Chart"
    elif "distribution" in prompt.lower() or "proportion" in prompt.lower():
        return "Pie Chart"
    elif "chart" in prompt.lower():
        return "Bar Chart"
    elif df[df.columns[0]].dtype in ['int64', 'float64'] and df[df.columns[1]].dtype in ['int64', 'float64']:
        return "Scatter Plot"
    else:
        return "Bar Chart"

def display_plotly_chart(df, chart_type, prompt):
    if chart_type == "Line Chart":
        fig = px.line(df, x=df.columns[0], y=df.columns[1], title="Trend Over Time")
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=df.columns[0], title="Distribution")
    elif chart_type == "Bar Chart":
        fig = px.bar(df, x=df.columns[0], y=df.columns[1], title="Bar Chart")
    elif chart_type == "Scatter Plot":
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1], title="Scatter Plot")
    elif chart_type == "Pie Chart":
        fig = px.pie(df, names=df.columns[0], values=df.columns[1], title="Pie Chart")

    fig.update_layout(
        xaxis_title=df.columns[0],
        yaxis_title=df.columns[1],
        title_x=0.5
    )
    
    st.plotly_chart(fig, use_container_width=True)

def displayAssistantMessage(assistantMessage: AssistantMessage):
    with st.chat_message("assistant", avatar="img/favicon.png"):
        if assistantMessage.message_type == "not_query":
            st.info(assistantMessage.response_data)
        elif assistantMessage.message_type == "no_data":
            st.info(assistantMessage.response_data, icon="🔍")
        else:
            show_sql = st.checkbox("Show SQL Query", value=False, key=f"show_sql_{assistantMessage.prompt}")
            if show_sql:
                st.code(assistantMessage.sql, language='sql')
            if assistantMessage.response_data.columns.size == 1 and assistantMessage.response_data.values[0].size == 1:
                st.metric(label=assistantMessage.response_data.columns[0], value=f'{assistantMessage.response_data.values[0][0]}')
            elif isinstance(assistantMessage.response_data, str):
                response = rename_columns(assistantMessage.response_data)
                st.write(response)
            elif isinstance(assistantMessage.response_data, pd.DataFrame) and assistantMessage.response_data.columns.size < 3:
                response = rename_columns(assistantMessage.response_data)
                st.write(response)
                
                suggested_chart_type = suggest_chart_type(response, assistantMessage.prompt)
                
                # Add a selectbox for chart type selection with a unique key
                chart_type = st.selectbox(
                    "Select Chart Type",
                    ('Line Chart', 'Bar Chart', 'Histogram', 'Scatter Plot', 'Pie Chart'),
                    index=('Line Chart', 'Bar Chart', 'Histogram', 'Scatter Plot', 'Pie Chart').index(suggested_chart_type),
                    key=f"chart_type_{assistantMessage.prompt}"
                )

                if(suggested_chart_type):
                    display_plotly_chart(response, chart_type, assistantMessage.prompt)
            else:
                response = rename_columns(assistantMessage.response_data)
                st.write(response)

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
        displayAssistantMessage(assistantMessage)

# Displaying chat description
if not st.session_state.messages:
    st.markdown(f'<p style="font-size:18px; text-align:center; margin-top:50px; ">I specialize in providing business insights and assisting with various applications. Feel free to ask me anything related to these topics.</p>', unsafe_allow_html=True)
else:
    st.markdown("#")

# React to user input
if prompt := st.chat_input("Ask me any question about business at Irembo?"):
    description = None

    # Clear the chat container before displaying the new response
    placeholder = st.empty()

    with placeholder.container():
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
                response_data = response.replace('```', '')

                # Display assistant response in chat message container
                assistantMsg = AssistantMessage(sql=response, prompt=prompt, response_data=response_data, message_type="not_query")
                displayAssistantMessage(assistantMsg)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistantMsg.to_dict()})
                status.update(label='Response of last question', state="complete", expanded=True)
            elif is_query:
                try:
                    response_data = run_query(response.replace('```', ''))
                    # Display assistant response in chat message container
                    assistantMsg = AssistantMessage(sql=response, prompt=prompt, response_data=response_data, message_type="query")
                    displayAssistantMessage(assistantMsg)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistantMsg.to_dict()})
                    status.update(label='Response of last question', state="complete", expanded=True)

                except Exception as e:
                    # Set the message to be displayed
                    response_data = "No data was found."

                    # Display assistant response in chat message container
                    assistantMsg = AssistantMessage(sql=response, prompt=prompt, response_data=response_data, message_type="no_data")
                    displayAssistantMessage(assistantMsg)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistantMsg.to_dict()})
                    status.update(label='Response of last question', state="complete", expanded=True)
