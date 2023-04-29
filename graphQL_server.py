import os
import random
from flask import Flask
from flask_graphql import GraphQLView
import graphene
import sqlite3
import re
import spacy

# graphQL_server.py
def load_spacy_model():
    global nlp
    nlp = spacy.load("ja_core_news_sm")

class Author(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    country = graphene.String()

class Book(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author = graphene.Field(Author)

# Sample data
authors = [
    Author(id=1, name='George Orwell', country='United Kingdom'),
    Author(id=2, name='Aldous Huxley', country='United Kingdom'),
]

books = [
    Book(id=1, title='1984', author=authors[0]),
    Book(id=2, title='Animal Farm', author=authors[0]),
    Book(id=3, title='Brave New World', author=authors[1]),
]

class SystemMessage(graphene.ObjectType):
    content = graphene.String()

class AssistantMessage(graphene.ObjectType):
    content = graphene.String()


system_messages = [
    SystemMessage(content="You are now chatting with GPT-4."),
]

assistant_messages = [
    AssistantMessage(content="Hello! I'm GPT-4, and I'm here to help you."),
]



def read_keywords_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        keywords = [line.strip() for line in file.readlines()]
    return keywords

confidential_keywords = read_keywords_from_file(os.path.join(os.path.dirname(__file__), 'keywords.txt'))

def find_names_and_places(text):
    doc = nlp(text)
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    places = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    return names, places

def anonymize_text(text):
    names, places = find_names_and_places(text)
    name_placeholder = "{name}"
    place_placeholder = "{place}"
    
    for name in names:
        text = re.sub(re.escape(name), name_placeholder, text, flags=re.IGNORECASE | re.UNICODE)
    
    for place in places:
        text = re.sub(re.escape(place), place_placeholder, text, flags=re.IGNORECASE | re.UNICODE)

    return text

def contains_confidential_information(message):
    for keyword in confidential_keywords:
        if keyword.lower() in message.lower():
            print(f"Keyword '{keyword}' found in message: '{message}'")
            return True, keyword
    return False, None

# def contains_confidential_information(message):
#     for keyword in confidential_keywords:
#         if keyword.lower() in message.lower():
#             return True
#     return False


class Query(graphene.ObjectType):
    authors = graphene.List(Author)
    books = graphene.List(Book)
    system_messages = graphene.List(SystemMessage)
    print(AssistantMessage)
    assistant_messages = graphene.List(AssistantMessage)

    def resolve_authors(self, info):
        return authors

    def resolve_books(self, info):
        return books

    
    def resolve_system_messages(self, info):
        # Filter out messages containing confidential information
        filtered_messages = []
        for msg in system_messages:
            contains_confidential, keyword = contains_confidential_information(msg.content)
            if not contains_confidential:
                filtered_messages.append(msg)
            else:
                print(f"Filtered out message: {msg.content} | Detected keyword: {keyword}")
        return filtered_messages


    def resolve_assistant_messages(self, info):
        # Filter out messages containing confidential information
        
        filtered_messages = [msg for msg in assistant_messages if not contains_confidential_information(msg.content)]
        return filtered_messages

schema = graphene.Schema(query=Query)

app = Flask(__name__)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


def read_keywords_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        keywords = [line.strip() for line in file.readlines()]
    return keywords

# Read keywords from the file
confidential_keywords = read_keywords_from_file('keywords.txt')


if __name__ == '__main__':
    app.run()
