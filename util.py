import os
import random
from flask import Flask
from flask_graphql import GraphQLView
import graphene
import re
import spacy
from chatgpt import chat_with_models
# import MeCab
import datetime
from collections import defaultdict


class NameAndPlaceFinder:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def find(self, text):
        doc = self.nlp(text)
        names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        places = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

        return names, places


class Message(graphene.ObjectType):
    content = graphene.String()


class UniqueUpdater:
    @staticmethod
    def update(original_dict, new_dict):
        for key, value in new_dict.items():
            if key in original_dict:
                counter = 1
                new_key = key + "_" + str(counter)
                while new_key in original_dict:
                    counter += 1
                    new_key = key + "_" + str(counter)
                original_dict[new_key] = value
            else:
                original_dict[key] = value
        return original_dict


class KeywordFilter:
    @staticmethod
    def filter(text, keyword_file='keywords.txt'):
        replacements = {}
        with open(keyword_file, 'r', encoding='utf-8') as file:
            keywords = [line.strip() for line in file.readlines()]

        for keyword in keywords:
            if keyword in text:
                text = text.replace(keyword, "{REDACTED}")
                replacements[keyword] = "{REDACTED}"

        return text, replacements


class NumericalInformationFilter:
    @staticmethod
    def filter(text):
        replacements = defaultdict(list)

        # Replace phone numbers
        pattern = r'\b\d{2,4}[-\s.]?\d{2,4}[-\s.]?\d{2,4}[-\s.]?\d{0,4}\b'
        for match in re.findall(pattern, text):
            replacements[match].append('{phone_number}')
        text = re.sub(pattern, '{phone_number}', text)
    
        # Replace credit card numbers
        pattern = r'\b(?:\d{4}[-\s.]?){3}\d{4}\b'
        for match in re.findall(pattern, text):
            replacements[match].append('{credit_card_number}')
        text = re.sub(pattern, '{credit_card_number}', text)
    
        # Replace expiration dates
        pattern = r'\b\d{2}\/\d{2,4}\b'
        for match in re.findall(pattern, text):
            replacements[match].append('{expiration_date}')
        text = re.sub(pattern, '{expiration_date}', text)

        return text, replacements


class TextAnonymizer:
    def __init__(self):
        self.finder = NameAndPlaceFinder()

    def anonymize(self, text):
        replacements = {}
        names, places = self.finder.find(text)
        name_placeholder = "{name}"
        place_placeholder = "{place}"
    
        for name in names:
            text = re.sub(re.escape(name), name_placeholder, text, flags=re.IGNORECASE | re.UNICODE)
            replacements[name] = name_placeholder
    
        for place in places:
            text = re.sub(re.escape(place), place_placeholder, text, flags=re.IGNORECASE | re.UNICODE)
            replacements[place] = place_placeholder

        return text, replacements


class JapaneseFilter:
    # Note: MeCab instance initialization can be moved to constructor if necessary
    @staticmethod
    def filter_names(text):
        mecab = MeCab.Tagger("-Ochasen")
        node = mecab.parseToNode(text)

        masked_text = text
        replacements = {}
        while node:
            word, feature = node.surface, node.feature.split(',')
            if feature[0] == '名詞' and feature[1] == '固有名詞':
                masked_word = "{japanese_name}"
                masked_text = masked_text.replace(word, masked_word)
                if word not in replacements:
                    replacements[word] = masked_word
            node = node.next

        return masked_text, replacements

    @staticmethod
    def filter_by_name_keisyou(text):
        name_pattern = r"([一-龯]+(さん|ちゃん|君|くん|様|さま))"
        replacements = {}
        masked_text = text
        matches = re.findall(name_pattern, text)
        for match in matches:
            masked_word = "{japanese_name}"
            masked_text = masked_text.replace(match[0], masked_word)
            if match[0] not in replacements:
                replacements[match[0]] = masked_word
        return masked_text, replacements

    @staticmethod
    def filter_by_place_keisyou(text):
        place_pattern = r"([一-龯]+(市|町|村|区|都))"
        replacements = {}
        masked_text = text
        matches = re.findall(place_pattern, text)
        for match in matches:
            masked_word = "{japanese_place}"
            masked_text = masked_text.replace(match[0], masked_word)
            if match[0] not in replacements:
                replacements[match[0]] = masked_word
        return masked_text, replacements

    @staticmethod
    def filter_by_age_keyshou(text):
        age_pattern = r"(\d{1,2}歳)"
        replacements = {}
        masked_text = text
        matches = re.findall(age_pattern, text)
        for match in matches:
            masked_word = "{japanese_age}"
            masked_text = masked_text.replace(match, masked_word)
            if match not in replacements:
                replacements[match] = masked_word
        return masked_text, replacements

    @staticmethod
    def apply_filters(text, filters=[
                                JapaneseFilter.filter_by_name_keisyou,
                                JapaneseFilter.filter_by_place_keisyou,
                                JapaneseFilter.filter_by_age_keyshou,
                                JapaneseFilter.filter_names]):
        replacements = {}
        for filter_func in filters:
            text, filter_replacements = filter_func(text)
            replacements.update(filter_replacements)
        return text, replacements
