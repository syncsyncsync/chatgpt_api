import os
import argparse
import requests
import json

openai_api_key = os.getenv("OPENAI_API_KEY")

def send_graphql_request(query, variables=None):
    url = "http://localhost:5000/graphql"
    headers = {
        "Content-Type": "application/json",
    }
    data = json.dumps({"query": query, "variables": variables})
    print(variables)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(response.text)
        raise Exception(f"GraphQL request failed with status code {response.status_code}")

def send_messages(system_message=None, assistant_message=None, user_message=None, model_name="gpt-3.5-turbo-0301"):
    send_messages_mutation = """
    mutation SendMessages($systemMessage: String, $assistantMessage: String, $userMessage: String,$modelName: String) {
        sendMessages(systemMessage: $systemMessage, assistantMessage: $assistantMessage, userMessage: $userMessage, modelName: $modelName) {
            systemMessage {
                content
            }
            assistantMessage {
                content
            }
            userMessage {
                content
            }
            modelName
        }
    }
    """

    variables = {
        "systemMessage": system_message,
        "assistantMessage": assistant_message,
        "userMessage": user_message,
        "modelName":  model_name
    }

    response = send_graphql_request(send_messages_mutation, variables)
    if 'errors' in response:
        print("Error sending messages:")
        print(response['errors'])
    else:
        return response['data']['sendMessages']


def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat with OpenAI models using GraphQL server")
    parser.add_argument("--system", type=str, default="be my English teacher", help="System message to send")
    parser.add_argument("--assistant", type=str, default="I wii correct your English.",help="Assistant message to send")
    parser.add_argument("--user", default="Hello" ,type=str, help="User message to send")
    parser.add_argument("--model", default="gpt-3.5-turbo-0301", type=str, help="model")
    return parser.parse_args()


def main():
    args = parse_arguments()

    send_messages_response = send_messages(system_message=args.system, assistant_message=args.assistant, user_message=args.user, model_name=args.model)
    if send_messages_response:
        print("OpenAI's response:")
        if send_messages_response["systemMessage"]:
            print(f"Res: System: {send_messages_response['systemMessage']['content']}")
        if send_messages_response["assistantMessage"]:
            print(f"Res: Assistant: {send_messages_response['assistantMessage']['content']}")
        if send_messages_response["userMessage"]:
            print(f"Res: User: {send_messages_response['userMessage']['content']}")
        if send_messages_response["modelName"]:
            print(f"Res: Model Name: {send_messages_response['modelName']}")

    print("Sent messages:")
    print(send_messages_response)

if __name__ == "__main__":
    main()
