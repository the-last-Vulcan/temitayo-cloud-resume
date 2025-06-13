# counter_backend/test_main.py
import pytest
from unittest.mock import MagicMock, patch
import json # For converting JSON response to dict

# Assuming your main.py has a function like this:
# from google.cloud import firestore
# def count_visitors(request):
#     db = firestore.Client()
#     ...
from main import count_visitors # Adjust 'main' if your function is named differently

# Pytest fixture to mock the Firestore client for each test
@pytest.fixture
def mock_firestore_db():
    with patch('main.firestore.Client') as mock_client: # Adjust 'main' if firestore.Client is imported differently in your main.py
        mock_db_instance = MagicMock() # Mock the Firestore client instance
        mock_client.return_value = mock_db_instance # When firestore.Client() is called, return our mock
        yield mock_db_instance # Provide this mock to the test functions

# Test case 1: New visitor (document doesn't exist)
def test_count_visitors_new_document(mock_firestore_db):
    # Mock the HTTP request object
    mock_request = MagicMock()
    mock_request.method = 'GET' # Simulate a GET request

    # Mock Firestore document.get() behavior when document does NOT exist
    mock_doc_ref = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value = mock_doc_ref # Simulate db.collection('visitors').document('resume')
    mock_doc_ref.get.return_value.exists = False # Document does not exist

    # Call the Cloud Run function
    response_data, status_code = count_visitors(mock_request)

    # Assertions
    assert status_code == 200
    # Assuming your function returns JSON directly as text, parse it
    response_dict = json.loads(response_data)
    assert response_dict['total_views'] == 1

    # Verify Firestore interactions
    mock_doc_ref.set.assert_called_once_with({"total_views": 1}) # Expect set() to be called for a new document

# Test case 2: Existing visitor (document exists)
def test_count_visitors_existing_document(mock_firestore_db):
    # Mock the HTTP request object
    mock_request = MagicMock()
    mock_request.method = 'GET'

    # Mock Firestore document.get() behavior when document DOES exist
    mock_doc_ref = MagicMock()
    mock_firestore_db.collection.return_value.document.return_value = mock_doc_ref
    mock_doc_ref.get.return_value.exists = True # Document exists
    mock_doc_ref.get.return_value.to_dict.return_value = {"total_views": 5} # Simulate existing data

    # Call the Cloud Run function
    response_data, status_code = count_visitors(mock_request)

    # Assertions
    assert status_code == 200
    response_dict = json.loads(response_data)
    assert response_dict['total_views'] == 6 # Expecting incremented count

    # Verify Firestore interactions
    mock_doc_ref.update.assert_called_once_with({"total_views": 6}) # Expect update() to be called for existing document