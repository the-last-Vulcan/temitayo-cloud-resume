# counter_backend/test_main.py (Modified)
import pytest
from unittest.mock import MagicMock, patch
import json

from main import count_visitors # Assuming count_visitors is your entry point function
# You might need to import Response if your function explicitly returns it
# from flask import Response # Or whatever framework you're using

# Mock the Firestore client
@pytest.fixture
def mock_firestore_db():
    with patch('main.firestore.Client') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        yield mock_db

# Test case for a new visitor
def test_count_visitors_new_document(mock_firestore_db):
    mock_request = MagicMock()
    mock_request.method = 'GET'
    # Mocking for incoming request headers/data if needed, e.g. for CORS preflight
    mock_request.headers = {}
    mock_request.get_json.return_value = None # Assuming no JSON body for GET
    mock_request.args = {} # Assuming no query parameters

    mock_doc_ref = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value.exists = False

    # Call the function - now it returns a Response object
    response = count_visitors(mock_request) # <--- Change here: Capture the Response object

    # Assertions on the Response object
    assert response.status_code == 200 # Access status_code directly from response object
    response_data = json.loads(response.data) # Access data and parse it
    assert response_data['total_views'] == 1

    mock_doc_ref.set.assert_called_once_with({"total_views": 1})

# Test case for existing visitor
def test_count_visitors_existing_document(mock_firestore_db):
    mock_request = MagicMock()
    mock_request.method = 'GET'
    mock_request.headers = {}
    mock_request.get_json.return_value = None
    mock_request.args = {}

    mock_doc_ref = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value.exists = True
    # Fix for line 56: Make sure this is a dictionary, not just key-value pair
    mock_doc_ref.get.return_value.to_dict.return_value = {"total_views": 5}

    # Call the function - now it returns a Response object
    response = count_visitors(mock_request) # <--- Change here: Capture the Response object

    # Assertions on the Response object
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['total_views'] == 6

    mock_doc_ref.update.assert_called_once_with({"total_views": 6})