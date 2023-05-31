import os
import random
from flask import Flask
from flask_graphql import GraphQLView
import graphene
#import sqlite3
import re
import spacy
from chatgpt import chat_with_models
# import MeCab
import datetime
# Initializing session history
session_history = {}


def load_spacy_model():
    global nlp
    nlp = spacy.load("en_core_web_sm")

load_spacy_model()

class SystemMessage(graphene.ObjectType):
    content = graphene.String()

class AssistantMessage(graphene.ObjectType):
    content = graphene.String()

class UserMessage(graphene.ObjectType):
    content = graphene.String()


def filter_keyword_information(text, keyword_file='keywords.txt'):
    with open(keyword_file, 'r', encoding='utf-8') as file:
        keywords = [line.strip() for line in file.readlines()]
    
    for keyword in keywords:
        text = text.replace(keyword, "{REDACTED}")

    return text


def filter_confidential_by_ai(text, model):
    # to be deployed 
    return text


def find_names_and_places(text):
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    places = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    return names, places


def filter_japanese_names(text):
    mecab = MeCab.Tagger("-Ochasen")
    node = mecab.parseToNode(text)

    masked_text = text
    while node:
        word, feature = node.surface, node.feature.split(',')
        if feature[0] == '名詞' and feature[1] == '固有名詞':
            masked_text = re.sub(word, "{japanese_name}", masked_text)
        node = node.next

    return masked_text


def filter_japanese_by_name_keisyou(text):
    name_pattern = r"([一-龯]+(さん|ちゃん|君|くん|様|さま))"
    masked_text = re.sub(name_pattern, "{japanese_name}", text)
    return masked_text

def filter_japanese_by_place_keisyou(text):
    place_pattern = r"([一-龯]+(市|町|村|区|都))"
    masked_text = re.sub(place_pattern, "{japanese_place}", text)
    return masked_text


def filter_japanese_by_age_keyshou(text):
    age_pattern = r"(\d{1,2}歳)"
    masked_text = re.sub(age_pattern, "{japanese_age}", text)
    return masked_text

def filter_japanese_by_mecab(text):
    mecab = MeCab.Tagger("-Ochasen")
    node = mecab.parseToNode(text)

    masked_text = text
    while node:
        word, feature = node.surface, node.feature.split(',')
        if feature[0] == '名詞' and feature[1] == '固有名詞':
            masked_text = re.sub(word, "{japanese_name}", masked_text)
        node = node.next

    return masked_text


def filter_anonymize_text(text):
    names, places = find_names_and_places(text)
    name_placeholder = "{name}"
    place_placeholder = "{place}"
    
    for name in names:
        text = re.sub(re.escape(name), name_placeholder, text, flags=re.IGNORECASE | re.UNICODE)
    
    for place in places:
        text = re.sub(re.escape(place), place_placeholder, text, flags=re.IGNORECASE | re.UNICODE)

    return text


def apply_japanese_filters(text, filters=[  
                    filter_japanese_by_name_keisyou,
                    filter_japanese_by_place_keisyou,
                    filter_japanese_by_age_keyshou]):
#                    filter_japanese_by_mecab]):
    for filter_func in filters:
        text = filter_func(text)
    return text


def apply_filters(text, filters= [ 'numerical', 'keyword',  'anonymize'],jp_filters=[] ,model=None, keyword_file=None):

    if filters== [] :
        filters= [ 'numerical', 'keyword',  'anonymize', 'japanese']

    if 'numerical' in filters:
        text = filter_numerical_information(text)
    if 'keyword' in filters and keyword_file:
        text = filter_keyword_information(keyword_file, text)
    if 'anonymize' in filters:
        text = filter_anonymize_text(text)
    if 'japanese' in filters:
        if jp_filters == []:
            text = apply_japanese_filters(text)
        else:
            text = apply_japanese_filters(text, filters=jp_filters)
    if 'ai' in filters and model:
        text = filter_confidential_by_ai(text, model)
    
    return text


def filter_numerical_information(text):
    # Replace phone numbers
    text = re.sub(r'\b\d{2,4}[-\s.]?\d{2,4}[-\s.]?\d{2,4}[-\s.]?\d{0,4}\b', '{phone_number}', text)
    
    # Replace credit card numbers
    text = re.sub(r'\b(?:\d{4}[-\s.]?){3}\d{4}\b', '{credit_card_number}', text)
    
    # Replace expiration dates
    text = re.sub(r'\b\d{2}\/\d{2,4}\b', '{expiration_date}', text)

    return text


def contains_confidential_information(message):
    for keyword in confidential_keywords:
        if keyword.lower() in message.lower():
            # pirnt("confidential found")
            return True, keyword
    return False, None


class Query(graphene.ObjectType):
    system_messages = graphene.List(SystemMessage)
    assistant_messages = graphene.List(AssistantMessage)
    user_messages = graphene.List(UserMessage)

    model_info = graphene.Field(lambda: ModelInfo, model_name=graphene.String(default_value="gpt-3.5-turbo"))
 
    session_history = graphene.List(graphene.String, sessionId=graphene.String())

    def resolve_session_history(self, info, sessionId):
        print(f"sessionId: {sessionId}")
        return session_history.get(sessionId, [])

    def resolve_model_info(self, info, model_name="gpt-3.5-turbo"):
        #token_count = count_tokens(model_name)
        return ModelInfo(model_name=model_name, token_count=None)


    def resolve_system_messages(self, info):
        filtered_messages = []
        for msg in system_messages:
            contains_confidential, keyword = contains_confidential_information(msg.content)
            if not contains_confidential:
                filtered_messages.append(msg)
            else:
                print(f"Filtered out message: {msg.content} | Detected keyword: {keyword}")
        return filtered_messages


    def resolve_assistant_messages(self, info):
        filtered_messages = []
        for msg in assistant_messages:
            contains_confidential, keyword = contains_confidential_information(msg.content)
            if not contains_confidential:
                filtered_messages.append(msg)
            else:
                print(f"Filtered out message: {msg.content} | Detected keyword: {keyword}")
        return filtered_messages


    def resolve_user_messages(self, info):
        filtered_messages = []
        for msg in user_messages:
            contains_confidential, keyword = contains_confidential_information(msg.content)
            if not contains_confidential:
                filtered_messages.append(msg)
            else:
                print(f"Filtered out message: {msg.content} | Detected keyword: {keyword}")
        return filtered_messages


def extract_messages_from_session_history(sessionId):
    session_data = session_history.get(sessionId, [])
    messages = []

    for entry in session_data:
        role = entry.get("role")
        message = entry.get("message")
        
        if role and message is not None:
            messages.append({"role": role, "content": message})

    return messages

class ModelInfo(graphene.ObjectType):
    model_name = graphene.String()
    token_count = None



class SendMessages(graphene.Mutation):
    class Arguments:
        sessionId = graphene.String(required=True)
        system_message = graphene.String()
        assistant_message = graphene.String()
        user_message = graphene.String()
        model_name = graphene.String(default_value="gpt-3.5-turbo")

    system_message = graphene.Field(lambda: SystemMessage)
    assistant_message = graphene.Field(lambda: AssistantMessage)
    user_message = graphene.Field(lambda: UserMessage)
    modelName = graphene.String()


    def mutate(self, info, sessionId, system_message=None, assistant_message=None, user_message=None, model_name=None):
        global session_history  # Declare it global to access it inside this method
        if sessionId not in session_history:
            session_history[sessionId] = []

        input_messages = []

        # Get previous input_messages if they exist
        for message in session_history[sessionId]:
            input_messages.append(message)

           # Apply filters to the user_message
        if user_message:
            user_message = apply_filters(user_message, filters=['numerical', 'keyword', 'anonymize'], jp_filters=[], model=None, keyword_file=None)


        # Add new messages to session history and input_messages for model
        for role, message in [('system', system_message), ('assistant', assistant_message), ('user', user_message)]:
            if message:
                new_message = {
                    "role": role,
                    "content": message,
                }
                session_history[sessionId].append(new_message)
                input_messages.append(new_message)

        # Call the model with the combined old and new input_messages
        response = chat_with_models(model_name, input_messages)

        if isinstance(response, list):
            system_message = next((msg["content"] for msg in response if msg["role"] == "system"), None)
            assistant_message = next((msg["content"] for msg in response if msg["role"] == "assistant"), None)
            user_message = next((msg["content"] for msg in response if msg["role"] == "user"), None)
        else:
            system_message = None
            assistant_message = response["content"]
            user_message = None

        # Add responses to session history
        for role, message in [('system', system_message), ('assistant', assistant_message), ('user', user_message)]:
            if message:
                session_history[sessionId].append({
                    "role": role,
                    #"message": message,
                    "content": message,
                    #"timestamp": datetime.datetime.now().isoformat(),
                })
        return SendMessages(system_message=SystemMessage(content=system_message) if system_message else None,
                            assistant_message=AssistantMessage(content=assistant_message) if assistant_message else None,
                            user_message=UserMessage(content=user_message) if user_message else None,
                            modelName=model_name)


class Mutation(graphene.ObjectType):
    send_messages = SendMessages.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

app = Flask(__name__)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

if __name__ == '__main__':
    app.run()
