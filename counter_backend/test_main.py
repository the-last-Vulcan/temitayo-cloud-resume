# counter_backend/test_main.py (FINAL VERSION to align with main.py's 3-item tuple return)
import pytest
from unittest.mock import MagicMock, patch
import json

from main import count_visitors # Assuming count_visitors is your entry point function

# Mock the Firestore client
@pytest.fixture
def mock_firestore_db():
    with patch('main.firestore.Client') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        yield mock_db

# Test case for OPTIONS (preflight) request
def test_count_visitors_options_request(mock_firestore_db):
    mock_request = MagicMock()
    mock_request.method = 'OPTIONS'
    # For OPTIONS, the request body/args aren't usually relevant
    mock_request.headers = {
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type',
        'Origin': 'https://temitayoapata.online' # Example origin
    }

    # Call the function - NOW UNPACK ALL THREE VALUES!
    body, status_code, headers = count_visitors(mock_request)

    # Assertions for OPTIONS
    assert status_code == 204 # No Content
    assert body == '' # Empty body
    assert headers['Access-Control-Allow-Origin'] == '*'
    assert headers['Access-Control-Allow-Methods'] == 'GET, POST, OPTIONS'
    assert headers['Access-Control-Allow-Headers'] == 'Content-Type'

# Test case for a new visitor (GET request)
def test_count_visitors_new_document(mock_firestore_db):
    mock_request = MagicMock()
    mock_request.method = 'GET'
    mock_request.headers = {}
    mock_request.get_json.return_value = None
    mock_request.args = {}

    mock_doc_ref = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value.exists = False # Document does not exist

    # Call the function - NOW UNPACK ALL THREE VALUES!
    body, status_code, headers = count_visitors(mock_request)

    # Assertions
    assert status_code == 200
    assert headers['Access-Control-Allow-Origin'] == '*' # Check CORS headers

    # Assuming main.py now returns JSON:
    response_data = json.loads(body) # Parse the JSON string from the body
    assert response_data['count'] == 1 # Check the 'count' key

    # Verify Firestore interactions
    mock_doc_ref.set.assert_called_once_with({"count": 1})

# Test case for existing visitor (GET request)
def test_count_visitors_existing_document(mock_firestore_db):
    mock_request = MagicMock()
    mock_request.method = 'GET'
    mock_request.headers = {}
    mock_request.get_json.return_value = None
    mock_request.args = {}

    mock_doc_ref = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value.exists = True # Document exists
    mock_doc_ref.get.return_value.to_dict.return_value = {"count": 5} # Simulate existing data (using 'count' key)

    # Call the function - NOW UNPACK ALL THREE VALUES!
    body, status_code, headers = count_visitors(mock_request)

    # Assertions
    assert status_code == 200
    assert headers['Access-Control-Allow-Origin'] == '*' # Check CORS headers

    # Assuming main.py now returns JSON:
    response_data = json.loads(body) # Parse the JSON string from the body
    assert response_data['count'] == 6 # Check the 'count' key

    # Verify Firestore interactions
    mock_doc_ref.update.assert_called_once_with({"count": 6})