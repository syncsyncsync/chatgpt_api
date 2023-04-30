import os
import random
from flask import Flask
from flask_graphql import GraphQLView
import graphene
import sqlite3
import re
import spacy
from chatgpt import chat_with_models
# import MeCab


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

import re

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


class SendMessages(graphene.Mutation):
    class Arguments:
        system_message = graphene.String()
        assistant_message = graphene.String()
        user_message = graphene.String()

    system_message = graphene.Field(lambda: SystemMessage)
    assistant_message = graphene.Field(lambda: AssistantMessage)
    user_message = graphene.Field(lambda: UserMessage)

    def mutate(self, info, filters=[], system_message=None, assistant_message=None, user_message=None):
        model_name = "gpt-3.5-turbo-0301"  # Add this line to define the model_name

        input_messages = []

        if system_message:
            system_message = apply_filters(system_message, filters)
            input_messages.append({"role": "system", "content": system_message})
        if assistant_message:
            assistant_message = apply_filters(assistant_message, filters)
            input_messages.append({"role": "assistant", "content": assistant_message})
        if user_message:
            user_message = apply_filters(user_message, filters)
            input_messages.append({"role": "user", "content": user_message})

        response = chat_with_models(model_name, input_messages)

        if isinstance(response, list):
            # Extract system, assistant, and user messages from the response
            system_message = next((msg["content"] for msg in response if msg["role"] == "system"), None)
            assistant_message = next((msg["content"] for msg in response if msg["role"] == "assistant"), None)
            user_message = next((msg["content"] for msg in response if msg["role"] == "user"), None)
        else:
            system_message = None
            assistant_message = response["content"]
            user_message = None

        return SendMessages(system_message=SystemMessage(content=system_message) if system_message else None,
                            assistant_message=AssistantMessage(content=assistant_message) if assistant_message else None,
                            user_message=UserMessage(content=user_message) if user_message else None)


class Mutation(graphene.ObjectType):
    send_messages = SendMessages.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

app = Flask(__name__)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

if __name__ == '__main__':
    app.run()
