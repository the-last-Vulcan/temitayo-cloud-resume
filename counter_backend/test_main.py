# counter_backend/test_main.py

import pytest
from unittest.mock import MagicMock, patch
import json

# IMPORTANT: We now import the Flask 'app' instance, not the 'count_visitors' function directly.
# The `patch` for firestore.Client must happen before 'app' is imported if it's at module level in main.py
# However, if using pytest fixtures with autouse, it can be handled there too.
# For simplicity, we'll ensure the patch is active when 'app' is loaded.

# Mock the Firestore client using a pytest fixture
@pytest.fixture(autouse=True) # autouse=True means this fixture runs for every test
def mock_firestore_db():
    # Patch google.cloud.firestore.Client when it's imported by 'main' module
    with patch('google.cloud.firestore.Client') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db

        # Mock commonly used methods on the client
        mock_collection_ref = MagicMock()
        mock_document_ref = MagicMock()

        mock_db.collection.return_value = mock_collection_ref
        mock_collection_ref.document.return_value = mock_document_ref

        # Yield the mocked db instance so tests can configure it
        yield mock_db

# Import the Flask app AFTER the patch setup, to ensure it uses the mocked Firestore client
from main import app # This imports your Flask app instance

# Test case for OPTIONS (preflight) request
def test_options_request():
    with app.test_client() as client:
        response = client.options('/')

        assert response.status_code == 200 # Flask-CORS typically returns 200 OK for OPTIONS
        assert response.data == b'' # Empty body for OPTIONS
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*' # Or your specific domain
        assert response.headers['Access-Control-Allow-Methods'] == 'GET, POST, OPTIONS'
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
    mock_doc_ref.get.side_effect = Exception("Firestore connection error")

    with app.test_client() as client:
        response = client.get('/')

        assert response.status_code == 500
        assert response.headers['Content-Type'] == 'application/json'
        
        data = response.json
        assert "error" in data
        assert data['error'] == "Failed to update visitor count" # Check the generic error message

        # Verify that the error was printed to stdout (captured by capsys)
        captured = capsys.readouterr()
        assert "An error occurred: Firestore connection error" in captured.out