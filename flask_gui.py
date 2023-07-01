from flask import Flask, render_template, request, redirect, url_for
import markdown
import uuid
from graphQL_client import send_messages, get_session_history, send_graphql_request
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import json

app = Flask(__name__)
Bootstrap(app)

@app.template_filter('markdown')
def md_filter(s):
    md = markdown.Markdown(safe_mode='escape')
    return md.convert(s)


@app.route('/')
def home():
    new_uuid = str(uuid.uuid4())
    # Add an empty dictionary for send_messages_response
    send_messages_response = {}
    return render_template('index.html', session_id=new_uuid, send_messages_response=send_messages_response)


@app.route('/', methods=['GET', 'POST'])
def index():
    model_name = ""
    if request.method == 'POST':
        session_id = request.form.get('sessionId')
        system_message = request.form.get('system')
        assistant_message = request.form.get('assistant')
        user_message = request.form.get('user')
        model_name = request.form.get('model')

        send_messages_response = send_messages(session_id, system_message, assistant_message, user_message, model_name)
        session_history_response = get_session_history(session_id)

        # Convert the JSON string to a Python object
        session_history_response = json.loads(session_history_response)

        # Remove duplicates from the session history for 'assistant' and 'user' roles
        unique_assistant_responses = set()
        unique_user_responses = set()
        deduplicated_history = []
        for message in session_history_response:
            if message['role'] == 'assistant' and message['content'] not in unique_assistant_responses:
                unique_assistant_responses.add(message['content'])
                deduplicated_history.append(message)
            elif message['role'] == 'user' and message['content'] not in unique_user_responses:
                unique_user_responses.add(message['content'])
                deduplicated_history.append(message)
            elif message['role'] not in ['assistant', 'user']:
                deduplicated_history.append(message)

        session_history_response = deduplicated_history

        # pass session_id back to the template here
        return render_template('index.html', session_id=session_id, send_messages_response=send_messages_response, session_history_response=session_history_response, model_name=model_name)

    new_uuid = str(uuid.uuid4())
    send_messages_response = {}
    session_history_response = []  # Initialize as empty list
    return render_template('index.html', session_id=new_uuid, send_messages_response=send_messages_response, session_history_response=session_history_response, model_name=model_name)

    new_uuid = str(uuid.uuid4())
    send_messages_response = {}
    session_history_response = []  # Initialize as empty list
    return

if __name__ == "__main__":
    app.run(debug=True, port=8080)

