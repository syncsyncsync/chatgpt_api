# ChatGPT API 

This is a simple Python client/server using GraphQL to interact with the OpenAI ChatGPT API. It demonstrates how to send messages to the API and receive responses in a conversation-like manner. The server also includes functionality to mask sensitive information and process Japanese text.

## Requirements

- Python 3.6 or higher
- Install the required packages by running: `pip install -r requirements.txt`

## Installation

Follow these steps to set up the ChatGPT API server:

1. Ensure you have Python 3.6 or higher installed on your system.

2. Clone the repository or download the source files to your local machine.

3. Navigate to the project directory in your terminal.

4. Install the required packages by running:

```bash
pip install -r requirements.txt
```

5. Download the necessary spaCy language model


That's it. Now you can follow the usage instructions in the README to start the server and interact with the ChatGPT API.



## Usage

1. Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Start the GraphQL server by running,
```bash
python graphQL_server.py
```
3. Run the graphQL_client.py script with the following arguments:

* --system: The system message to start the conversation (optional).
* --assistant: The assistant message (optional).
* --user: The user message (required).

```bash
python graphQL_client.py --system "be my English teacher" --assistant "I will correct your English" --user "Your text message here"
```

## Features
### Masking Sensitive Information
The client can mask sensitive information like names, phone numbers, credit card numbers, and expiration dates in the user's messages. To enable this feature, apply the mask_sensitive_data function to the user message.



## Supported ChatGPT Models
As of now, the following ChatGPT models can be used with this server:

* gpt-4
* gpt-4-0314
* gpt-4-32k
* gpt-4-32k-0314
* gpt-3.5-turbo
* gpt-3.5-turbo-0301

You can modify the model_name variable in the graphQL_server.py script to use a different model.


### Handling Japanese Text
The client can handle Japanese text by converting it to Unicode escape characters before sending it to the API. To use this feature, apply the unicode_escape function to the user message, and the unicode_unescape function to the API response.

## Customization

Feel free to modify the graphQL_client.py script to add your own filters or implement additional functionality as needed.

## Known Issues
Some users have reported issues with sending Japanese text to the API. Please ensure that the OpenAI API supports Unicode escape characters before using the Japanese text handling feature.

## Lincense
MIT
