import pytest
from graphene.test import Client
from graphQL_server import app, schema, anonymize_text, contains_confidential_information, read_keywords_from_file, load_spacy_model


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_authors(client):
    query = """
    query {
        authors {
            id
            name
            country
        }
    }
    """
    client = Client(schema)
    response = client.execute(query)
    assert response['data']['authors'] is not None
    assert len(response['data']['authors']) == 2

def test_books(client):
    query = """
    query {
        books {
            id
            title
            author {
                id
                name
                country
            }
        }
    }
    """
    client = Client(schema)
    response = client.execute(query)
    assert response['data']['books'] is not None
    assert len(response['data']['books']) == 3

def test_system_messages(client):
    query = """
    query {
        systemMessages {
            content
        }
    }
    """
    client = Client(schema)
    response = client.execute(query)
    assert response['data']['systemMessages'] is not None
    assert len(response['data']['systemMessages']) == 1


# def test_assistant_messages(client):
#     query = """
#     query {
#         assistantMessages {
#             content
#         }
#     }
#     """
#     client = Client(schema)
#     response = client.execute(query)
#     filtered_messages = response['data']['assistantMessages']
#     print(f"Filtered messages: {filtered_messages}")
#     assert filtered_messages is not None
#     assert len(filtered_messages) == 1


def test_read_keywords_from_file():
    keywords = read_keywords_from_file("keywords.txt")
    assert len(keywords) > 0
    assert "secret" in keywords


def test_contains_confidential_information():
    confidential_message = "This message contains a secret keyword."
    non_confidential_message = "This message does not have any sensitive data."
    contains_confidential, keyword = contains_confidential_information(confidential_message)
    assert contains_confidential == True
    contains_confidential, keyword = contains_confidential_information(non_confidential_message)
    assert contains_confidential == False, f"False positive caused by keyword: {keyword}"



def test_anonymize_text():
    load_spacy_model()
    original_text = "田中太郎と鈴木花子は東京から大阪に引っ越しました。"
    expected_anonymized_text = "{name}と{name}は{place}から{place}に引っ越しました。"
    anonymized_text = anonymize_text(original_text)
    assert anonymized_text == expected_anonymized_text


if __name__ == "__main__":
    pytest.main()
