# counter_backend/test_main.py (Reverted and Corrected for Tuple Return)
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

# Test case for a new visitor
def test_count_visitors_new_document(mock_firestore_db):
    mock_request = MagicMock()
    mock_request.method = 'GET'
    # Mocking for incoming request headers/data if needed, e.g. for CORS preflight
    mock_request.headers = {}
    mock_request.get_json.return_value = None
    mock_request.args = {}

    mock_doc_ref = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value.exists = False

    # Call the function - NOW UNPACK THE TUPLE AGAIN!
    response_data_str, status_code = count_visitors(mock_request) # <--- Revert this line

    # Assertions
    assert status_code == 200 # Now status_code is directly available
    response_data = json.loads(response_data_str) # And response_data_str is the JSON string
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
    mock_doc_ref.get.return_value.to_dict.return_value = {"total_views": 5} # Already fixed this from last time

    # Call the function - NOW UNPACK THE TUPLE AGAIN!
    response_data_str, status_code = count_visitors(mock_request) # <--- Revert this line

    # Assertions
    assert status_code == 200
    response_data = json.loads(response_data_str)
    assert response_data['total_views'] == 6

    mock_doc_ref.update.assert_called_once_with({"total_views": 6})