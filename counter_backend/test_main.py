# counter_backend/test_main.py

import pytest
from unittest.mock import MagicMock, patch
import json

# Global variable to hold the mocked Firestore client instance
# This will be initialized by the patch block below and then used by the fixture.
mock_db_instance = None
app = None # Initialize app as None, to be set by the patch block

# =========================================================================
# CRITICAL FIX: Patch google.cloud.firestore.Client *BEFORE* importing 'main.py'
# This ensures that when 'db = firestore.Client()' runs in main.py,
# it receives a mocked client instead of trying to authenticate.
# =========================================================================
with patch('google.cloud.firestore.Client') as MockFirestoreClient:
    # Initialize the global mock_db_instance here
    mock_db_instance = MagicMock()
    MockFirestoreClient.return_value = mock_db_instance

    # Now import the app; firestore.Client() in main.py will use the mock
    from main import app # Assign to the global app variable


# =========================================================================
# This fixture will ensure a clean mock state for the Firestore client
# for each individual test, referring to the global mock_db_instance.
# =========================================================================
@pytest.fixture(autouse=True)
def mock_firestore_db():
    # Reset the mock_db_instance for each test to ensure clean state
    mock_db_instance.reset_mock()

    # Re-mock commonly used methods on the client for each test's fresh state
    mock_collection_ref = MagicMock()
    mock_document_ref = MagicMock()

    mock_db_instance.collection.return_value = mock_collection_ref
    mock_collection_ref.document.return_value = mock_document_ref

    # Yield the global mock_db_instance for tests to use
    yield mock_db_instance


# Test case for OPTIONS (preflight) request
def test_options_request():
    with app.test_client() as client:
        response = client.options('/')

        assert response.status_code == 200 # Flask-CORS typically returns 200 OK for OPTIONS
        assert response.data == b'' # Empty body for OPTIONS
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*' # Or your specific domain
        assert 'Access-Control-Allow-Methods' in response.headers
        assert response.headers['Access-Control-Allow-Methods'] == 'GET, POST, OPTIONS'
        assert 'Access-Control-Allow-Headers' in response.headers
        assert response.headers['Access-Control-Allow-Headers'] == 'Content-Type'
        assert 'Access-Control-Max-Age' in response.headers


# Test case for a new visitor (GET request)
def test_new_visitor(mock_firestore_db):
    # Configure the mock document for the scenario where it doesn't exist initially
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.return_value = MagicMock(exists=False) # Simulate document not existing

    with app.test_client() as client:
        response = client.get('/')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'

        # Verify response data
        data = response.json # Flask's response object has a .json property for JSON data
        assert data['count'] == 1

        # Verify Firestore interactions
        mock_doc_ref.set.assert_called_once_with({"count": 1})
        mock_doc_ref.update.assert_not_called() # Ensure update was not called


# Test case for existing visitor (GET request)
def test_existing_visitor(mock_firestore_db):
    # Configure the mock document for the scenario where it exists with a count
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.return_value = MagicMock(exists=True, to_dict=lambda: {"count": 5}) # Simulate existing data

    with app.test_client() as client:
        response = client.get('/')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'

        # Verify response data
        data = response.json
        assert data['count'] == 6

        # Verify Firestore interactions
        mock_doc_ref.get.assert_called_once()
        mock_doc_ref.update.assert_called_once_with({"count": 6})
        mock_doc_ref.set.assert_not_called() # Ensure set was not called


# Test case for error handling (e.g., Firestore exception)
def test_error_handling(mock_firestore_db, capsys):
    # Simulate an exception when trying to get the document
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.side_effect = Exception("Simulated Firestore connection error")

    with app.test_client() as client:
        response = client.get('/')

        assert response.status_code == 500
        assert response.headers['Content-Type'] == 'application/json'

        data = response.json
        assert "error" in data
        assert data['error'] == "Failed to update visitor count" # Check the generic error message from main.py

        # Verify that the error was printed to stdout (captured by capsys)
        captured = capsys.readouterr()
        assert "An error occurred: Simulated Firestore connection error" in captured.out