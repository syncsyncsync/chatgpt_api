from flask import Flask, request, render_template
from chatgpt import chat_with_models
from graphQL_client import send_messages

app = Flask(__name__, template_folder='templates', static_folder='static')

chat_models = [
    "gpt-4", "gpt-4-0314", "gpt-4-32k", "gpt-4-32k-0314",
    "gpt-3.5-turbo", "gpt-3.5-turbo-0301"
]

# @app.route('/', methods=['GET', 'POST'])
# def chat():
#     if request.method == 'POST':
#         messages = []
#         messages.append({"role": "user", "content": request.form['user_input']})
#         selected_model = request.form['model']
#         response = chat_with_models(selected_model, messages)
#         return render_template('index.html', response=response, models=chat_models)
#     return render_template('index.html', models=chat_models)


@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        messages = []
        user_message = request.form['user_input']
        messages.append({"role": "user", "content": user_message})
        selected_model = request.form['model']
        
        # Call the send_messages function from graphQL_client.py
        send_messages_response = send_messages(user_message=user_message)
        
        # Adjust the format of the response to match the GraphQL client response
        response = {"choices": [{"message": {"role": "assistant", "content": send_messages_response["assistantMessage"]["content"]}}]}
        
        return render_template('index.html', response=response, models=chat_models)
    return render_template('index.html', models=chat_models)

if __name__ == '__main__':
    app.run(debug=True, port=8080)

