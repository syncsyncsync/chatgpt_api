import os
import openai
import argparse

openai.api_key = os.getenv("OPENAI_API_KEY")

# add coment
def chat_with_models(model, messages):
    '''
    Chat with OpenAI models
    Args:
        model (str): Model name
        messages (list): List of messages
    Returns:
        dict: Response from the model
    '''
    
    print(f"[EXPOSED] Messages sent to OpenAI: {messages}")

    try:
        chat_models = [
            "gpt-4", "gpt-4-0314", "gpt-4-32k", "gpt-4-32k-0314",
            "gpt-3.5-turbo", "gpt-3.5-turbo-0301"
        ]

        if model in chat_models:
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages
                )
                return {"role": "assistant", "content": response.choices[0].message.content}
            except Exception as e:
                print(f"Error: {e}")
                return {"role": "assistant", "content": "Error: Unable to get response from the model."}
        else:
            prompt = " ".join([msg["content"] for msg in messages if msg["role"] == "user"])
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.5
            )
            return {"role": "assistant", "content": response.choices[0].text.strip()}

    except Exception as e:
        print(f"Error: {e}")
        return {"role": "assistant", "content": "Error: Unable to get response from the model."}

# def chat_with_models(model, messages):
#     '''
#     Chat with OpenAI models
#     Args:
#         model (str): Model name
#         messages (list): List of messages
#     Returns:
#         str: Response from the model
#     '''
    
#     print(f"Messages sent to OpenAI: {messages}")

#     try:
#         chat_models = [
#             "gpt-4", "gpt-4-0314", "gpt-4-32k", "gpt-4-32k-0314",
#             "gpt-3.5-turbo", "gpt-3.5-turbo-0301"
#         ]

#         if model in chat_models:
#             response = openai.ChatCompletion.create(
#                 model=model,
#                 messages=messages
#             )
#             # return response.choices[0].message.content
#             return {"role": "assistant", "content": response.choices[0].message.content}
#         else:
#             prompt = " ".join([msg["content"] for msg in messages if msg["role"] == "user"])
#             response = openai.Completion.create(
#                 engine=model,
#                 prompt=prompt,
#                 max_tokens=150,
#                 n=1,
#                 stop=None,
#                 temperature=0.5
#             )
#             #return response.choices[0].text.strip()
#             return {"role": "assistant", "content": response.choices[0].text.strip()}

            


    except openai.OpenAIError as e:
        print(f"Error occurred while connecting to OpenAI API: {e}")
        print("Possible causes:")
        print("1. Invalid API key")
        print("2. Network issues")
        print("3. Invalid model or unsupported model for chat")
        print("4. Issues with the OpenAI API service")
        return None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Chat with OpenAI models")
    parser.add_argument("--model", type=str,default="gpt-3.5-turbo-0301", help="Model name")
    parser.add_argument("--system", nargs="*", default=[], help="System message(s)")
    parser.add_argument("--assistant", nargs="*", default=[], help="Assistant message(s)")
    parser.add_argument("--user", nargs="*", default=[], help="User message(s)")
    return parser.parse_args()


def main():
    args = parse_arguments()
    model_name = args.model

    messages = []
    for msg in args.system:
        messages.append({"role": "system", "content": msg})
    for msg in args.assistant:
        messages.append({"role": "assistant", "content": msg})
    for msg in args.user:
        messages.append({"role": "user", "content": msg})

    response = chat_with_models(model_name, messages)
    if response is not None:
        print(f"{model_name}'s response: {response}")

if __name__ == "__main__":
    main()