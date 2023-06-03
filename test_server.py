import pytest
import json
from graphQL_server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_system_messages(client):
    query = '''
    query {
        systemMessages {
            content
        }
    }
    '''

    response = client.post('/graphql', json={'query': query})
    print(response.data)  # Add this line for debugging purposes
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'errors' not in json_data
    assert len(json_data['data']['systemMessages']) == len(system_messages_list)

def test_assistant_messages(client):
    query = '''
    query {
        assistantMessages {
            content
        }
    }
    '''

    response = client.post('/graphql', json={'query': query})
    print(response.data)  # Add this line for debugging purposes
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'errors' not in json_data
    assert len(json_data['data']['assistantMessages']) == len(assistant_messages_list)

def test_user_messages(client):
    query = '''
    query {
        userMessages {
            content
        }
    }
    '''

    response = client.post('/graphql', json={'query': query})
    print(response.data)  # Add this line for debugging purposes
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'errors' not in json_data
    assert len(json_data['data']['userMessages']) == len(user_messages_list)
