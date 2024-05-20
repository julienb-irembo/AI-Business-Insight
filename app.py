# Peter Optimization

import streamlit as st
from openai import OpenAI
from config_peter.app_config import *
from config_peter.app_access_db import *
from streamlit_pills import pills
import json
import altair as alt



model = "gpt-3.5-turbo"
#model = "gpt-4o"
# model = "Irembo Data Insights"
gpt_base_url = None
# model = "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
# gpt_base_url = "http://localhost:1234/v1/"

openai_key = st.secrets["OpenAI_key"]



# ------------------------------------------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------------------------------------------
logo = "img/irembo-gov.svg"
# Initialize chat history
if "statitics_approved" not in st.session_state:
    st.session_state.statitics_approved = run_query("SELECT COUNT(*) AS count FROM table_vone_application where application_state ='APPROVED';" ).values[0][0]
    st.session_state.statitics_pending = run_query("SELECT COUNT(*) AS count FROM table_vone_application where application_state ='PENDING';").values[0][0]
    st.session_state.statitics_rejected = run_query("SELECT COUNT(*) AS count FROM table_vone_application where application_state ='REJECTED';").values[0][0]
    st.session_state.statitics_rfa = run_query("SELECT COUNT(*) AS count FROM table_vone_application where application_state ='RFA';").values[0][0]


def dashboard_cards():
    st.markdown(
        f"""
        <div style="display:flex; gap:20px; margin-bottom:20px; margin-top:20px;">
            <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; width:50%; display:grid; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <span style='color: #000000; font-size:13px; text-align:center;'>Approved</span>
                <h1 style='color: #0f996d; font-size:36px; text-align:center;'>{st.session_state.statitics_approved}</h1>
            </div>
            <div style='background-color: #ffffff;  padding: 20px; border-radius: 10px; width:50%; display:grid; justify-content: center; align-items: center;box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <span style='color: #000000; font-size:13px; text-align:center;'>Request for action</span>
                <h1 style='color: #106ddc; font-size:36px; text-align:center;'>{st.session_state.statitics_rfa}</h1>
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
                <h1 style='color: #ffc107; font-size:36px; text-align:center;'>{st.session_state.statitics_pending}</h1>
            </div>
            <div style='background-color: #ffffff;  padding: 20px; border-radius: 10px; width:50%; display:grid; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                <span style='color: #000000; font-size:13px; text-align:center;'>Rejected</span>
                <h1 style='color: #dc3545; font-size:36px; text-align:center;'>{st.session_state.statitics_rejected}</h1>
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

# I'm removing this because we are not suppose to send any information to the LLM during our conversation. Only the initial context, but no data from our DB
#def build_query_context(messages):
#    history = "\n".join([f"User: {msg['content']}" if msg["role"] == "user" else f"Assistant: {msg['content']}" for msg in messages])
#    return query_context + history

def askQuestion(model=model, question='', messages=[]):
    if openai_key is None or openai_key == '':
        print('Please provide the key before')
        return 'LLM API is not defined. Please provide the key before'
    else:
        client = OpenAI(api_key=openai_key, base_url=gpt_base_url)
        # query_context = build_query_context(messages)

        print(f'the query context is {query_context}')
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
    def __init__(self, prompt:str ="", sql: str = "", message_type:str = "", chart="line_chart", x_axis=None, y_axis=None , response_data=None, response_template=None):
        self.sql = sql
        self.response_data = response_data
        self.prompt = prompt
        self.message_type = message_type
        self.response_template = response_template
        self.chart = chart
        self.x_axis = x_axis
        self.y_axis = y_axis

    def to_dict(self):
        if isinstance(self.response_data, DataFrame):
            response_data = self.response_data.to_dict()
        else:
            response_data = self.response_data
        return {
            "sql": self.sql,
            "prompt": self.prompt,
            "message_type": self.message_type,
            "response_data": response_data,
            "response_template": self.response_template,
            "chart": self.chart,
            "x_axis": self.x_axis,
            "y_axis": self.y_axis
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
            response_data=response_data,
            response_template=data.get("response_template", ""),
            chart=data.get("chart", ""),
            x_axis=data.get("x_axis", ""),
            y_axis=data.get("y_axis", "")
        )
    
def format_column_name(column_name):
    return column_name.replace("_", " ").title()

def format_column_name_axis(column_names: []):
    if(isinstance(column_names, str)):
        return format_column_name(column_names)
    else:
        print(f"format_column_name_axis column_names {column_names}")
        result = []
        for i in column_names:
            result.append(format_column_name(i))

        print(f"format_column_name_axis result {result}")
        return result

def rename_columns(df):
    df2 = df
    df2.columns = [format_column_name(col) for col in df2.columns]
    return df2

def displayAssistantMessage(assistantMessage: AssistantMessage):
    with st.chat_message("assistant", avatar="img/favicon.png"):
        # st.markdown(assistantMessage.sql)
        if assistantMessage.message_type == "not_query":
            st.info(assistantMessage.response_data)

        elif assistantMessage.message_type == "no_data":
            st.info(assistantMessage.response_data, icon="🔍")
        
        else:
            #show_sql = st.checkbox("Show SQL Query", value=False, key=f"show_sql_{assistantMessage.prompt}")
            #if show_sql:
            #    st.code(assistantMessage.sql, language='sql')
            # Displaye Metric if the size of the result is only on columna and one value
            if assistantMessage.response_data.columns.size == 1 and len(assistantMessage.response_data.values) ==1 :
                st.metric(label=assistantMessage.response_template, value=f'{assistantMessage.response_data.values[0][0]}')
            
            # Display simple message if the response is a simple text, not a table
            elif isinstance(assistantMessage.response_data, str):
                response = rename_columns(assistantMessage.response_data)
                st.write(response, unsafe_allow_html=True)
            # Display the result table (Here, the result should be a table) 
            else:
                response = rename_columns(assistantMessage.response_data)
                st.info(assistantMessage.response_template)
                st.write(response)
                # Display a diagram if it was part of the request
                if (assistantMessage.chart == 'bar_chart' or assistantMessage.chart == 'line_chart')  and len(assistantMessage.response_data.columns) > 1 and len(assistantMessage.x_axis) == 1 and len(assistantMessage.y_axis) == 1:
                    st.bar_chart(
                        assistantMessage.response_data, 
                        x=format_column_name_axis(assistantMessage.x_axis)[0], 
                        y=format_column_name_axis(assistantMessage.y_axis)[0],
                        
                    )
                elif (assistantMessage.chart == 'bar_chart' or assistantMessage.chart == 'line_chart') and len(assistantMessage.response_data.columns) > 1 and len(assistantMessage.x_axis) == 2 and len(assistantMessage.y_axis) == 1:
                    st.write(
                        alt.Chart(assistantMessage.response_data)
                            .mark_bar()
                            .encode(
                                x = alt.X(format_column_name_axis(assistantMessage.x_axis)[1], sort=None),
                                y = format_column_name_axis(assistantMessage.y_axis)[0],
                                xOffset= format_column_name_axis(assistantMessage.x_axis)[0],
                                color=format_column_name_axis(assistantMessage.x_axis)[0],
                                #column = alt.Column(field=format_column_name_axis(assistantMessage.x_axis)[0], sort=None),
                            )
                        )
                elif (assistantMessage.chart == 'bar_chart' or assistantMessage.chart == 'line_chart') and len(assistantMessage.response_data.columns) > 1 and len(assistantMessage.x_axis) == 1 and len(assistantMessage.y_axis) == 2:
                    st.line_chart(
                        assistantMessage.response_data, 
                        x=format_column_name_axis(assistantMessage.x_axis)[0], 
                        y=format_column_name_axis(assistantMessage.y_axis),
                        color=format_column_name_axis(assistantMessage.x_axis)[0] 
                    )
                    
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "user":
        st.divider()
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
    with st.status('Running', expanded=True) as status:
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            # Use the messages history to keep the context
            response = askQuestion(question=prompt, messages=st.session_state.messages)
            print(f" LLM Reponse is {response}")

            # print(f"reponse with no escape :  {response.replace('```','').replace('\n',' ').replace('\t','  ').replace('\\n','').replace('\\t',' ').replace('\\',' ')}")
            response_object = json.loads(response.replace('```','').replace('\n',' ').replace('\t','  ').replace('\\n','  ').replace('\\t','  ').replace('\\',' '))
            print(f" LLM Reponse Object is {response_object}")

            reponse_type = response_object["type"]
            
            if reponse_type == 'QUESTION':
                print(f" Reponse Object is a QUESTION !!! ")
                response_data = response_object['question']

                # Display assistant response in chat message container
                assistanMsg = AssistantMessage(sql=response_data, prompt=prompt, response_data=response_data, message_type="not_query")
                displayAssistantMessage(assistanMsg)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistanMsg.to_dict()})
                status.update(label='Response of last question', state="complete", expanded=True)
            elif reponse_type == 'SQL':
                try:
                    print(f" Reponse Object is a SQL !!! ")
                    #query = re.sub('[^A-Za-z0-9 \'\]+', '', response_object["sql"])
                    response_data = run_query(response_object["sql"].replace('```','').replace('\n','').replace('\\',''))
                    # Display assistant response in chat message container
                    assistanMsg = AssistantMessage(sql=response_object["sql"], prompt=prompt, response_data=response_data, message_type="query",
                                                    chart=response_object["chart"], x_axis=response_object["x_axis"], y_axis=response_object["y_axis"], 
                                                    response_template=response_object["response_template"])
                    displayAssistantMessage(assistanMsg)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistanMsg.to_dict()})
                    status.update(label='Response of last question', state="complete", expanded=True)

                except Exception as e:
                    print(f" Reponse Object is a SQL. But Error while running the query !!! {e} ")
                    # Set the message to be displayed
                    response_data = "No data was found."

                    # Display assistant response in chat message container
                    assistanMsg = AssistantMessage(sql=response, prompt=prompt, response_data=response_data, message_type="no_data")
                    displayAssistantMessage(assistanMsg)

                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistanMsg.to_dict()})
                    status.update(label='Response of last question', state="complete", expanded=True)
                    
                    # # Display the message in the chat interface with an information icon
                    # with st.chat_message("assistant", avatar="img/favicon.png"):
                    #     st.info(info_message, icon="🔍")
        except Exception as ex:
            print(f"Error {ex}")