import graphQL_client as client
import pytest
import json

def test_send_graphql_request():
    query = """
    query {
        test {
            message
        }
    }
    """
    response = client.send_graphql_request(query)
    assert isinstance(response, dict)
    assert 'errors' not in response
    assert 'data' in response
    assert 'user_messages' in response['data']

def test_send_messages():
    system_message = "be my English teacher"
    assistant_message = "I will correct your English."
    user_message = "Hello"
    model_name = "gpt-3.5-turbo-0301"

    response = client.send_messages(
        system_message=system_message,
        assistant_message=assistant_message,
        user_message=user_message,
        model_name=model_name
    )

    assert response is not None
    assert 'errors' not in response
    assert 'systemMessage' in response
    assert 'assistantMessage' in response
    assert 'userMessage' in response
    assert 'modelName' in response

    if response["systemMessage"]:
        assert 'content' in response['systemMessage']

    if response["assistantMessage"]:
        assert 'content' in response['assistantMessage']

    if response["userMessage"]:
        assert 'content' in response['userMessage']

    if response["modelName"]:
        assert isinstance(response['modelName'], str)

    assert response['assistantMessage']['content'] is not None

def main():
    system_message = "be my English teacher"
    assistant_message = "I will correct your English."
    user_message = "Hello"
    model_name = "gpt-3.5-turbo-0301"

    response = client.send_messages(
        system_message=system_message,
        assistant_message=assistant_message,
        user_message=user_message,
        model_name=model_name
    )

    if response:
        print("OpenAI's response:")
        if response["systemMessage"]:
            print(f"Res: System: {response['systemMessage']['content']}")
        if response["assistantMessage"]:
            print(f"Res: Assistant: {response['assistantMessage']['content']}")
        if response["userMessage"]:
            print(f"Res: User: {response['userMessage']['content']}")
        if response["modelName"]:
            print(f"Res: Model Name: {response['modelName']}")

    print("Sent messages:")
    print(response)

# if __name__ == "__main__":
#     main()
