
from flask import Flask, render_template, request, redirect, url_for
import markdown
import uuid
from graphQL_client import send_messages, get_session_history, send_graphql_request
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
import json
app = Flask(__name__)
Bootstrap(app)

@app.route('/')
def home():
    new_uuid = str(uuid.uuid4())
    return render_template('index.html', session_id=new_uuid)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session_id = request.form.get('sessionId')
        system_message = request.form.get('system')
        assistant_message = request.form.get('assistant')
        user_message = request.form.get('user')
        model_name = request.form.get('model')

        send_messages_response = send_messages(session_id, system_message, assistant_message, user_message, model_name)

        session_history_response = get_session_history(session_id)

        # Convert the JSON string to a Python object
        session_history_response = json.loads(session_history_response )
        
        #print(session_history_response)
        return render_template('index.html', send_messages_response=send_messages_response, session_history_response=session_history_response)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=8080)

