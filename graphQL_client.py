import os
import openai
import argparse
import requests
import json

openai.api_key = os.getenv("OPENAI_API_KEY")

def send_graphql_request(query):
    url = "http://localhost:5000/graphql"
    headers = {
        "Content-Type": "application/json",
    }
    data = json.dumps({"query": query})
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"GraphQL request failed with status code {response.status_code}")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat with OpenAI models using GraphQL server")
    parser.add_argument("--model", type=str, default="gpt-4", help="Model name")
    return parser.parse_args()




# def main():
#     args = parse_arguments()
#     model_name = args.model
#     if model_name is None:
#         print("Please specify a model name")
#         return

#     # GraphQL query to fetch system and assistant messages
#     system_and_assistant_query = """
#     query {
#         system_messages {
#             content
#         }
#         assistant_messages {
#             content
#         }
#     }
#     """

#     # GraphQL query to fetch book data
#     book_data_query = """
#     query {
#         books {
#             title
#             author {
#                 name
#                 country
#             }
#         }
#     }
#     """

#     system_and_assistant_response = send_graphql_request(system_and_assistant_query)
#     book_data_response = send_graphql_request(book_data_query)

#     if 'errors' in system_and_assistant_response:
#         print("Error fetching data from GraphQL API:")
#         print(system_and_assistant_response['errors'])
#         return

#     if 'errors' in book_data_response:
#         print("Error fetching data from GraphQL API:")
#         print(book_data_response['errors'])
#         return

#     system_messages = system_and_assistant_response['data']['system_messages']
#     assistant_messages = system_and_assistant_response['data']['assistant_messages']
#     book_data = book_data_response['data']['books'][0]
#     book_title = book_data['title']
#     author_name = book_data['author']['name']
#     author_country = book_data['author']['country']
    
#     user_message = f"Tell me more about the book '{book_title}' written by {author_name} from {author_country}."

#     messages = []
#     for msg in system_messages:
#         messages.append({"role": "system", "content": msg['content']})
#     for msg in assistant_messages:
#         messages.append({"role": "assistant", "content": msg['content']})
#     messages.append({"role": "user", "content": user_message})

#     response = chat_with_models(model_name, messages)
#     if response is not None:
#         print(f"{model_name}'s response: {response}")


def main():
    # GraphQL query to fetch system and assistant messages
    system_and_assistant_query = """
    query {
        systemMessages {
            content
        }
        assistantMessages {
            content
        }
    }
    """

    system_and_assistant_response = send_graphql_request(system_and_assistant_query)

    if 'errors' in system_and_assistant_response:
        print("Error fetching data from GraphQL API:")
        print(system_and_assistant_response['errors'])
    else:
        print("System and Assistant Messages:")
        print(system_and_assistant_response)


if __name__ == "__main__":
    main()
