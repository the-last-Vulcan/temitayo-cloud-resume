# counter_backend/test_main.py

import pytest
from unittest.mock import MagicMock, patch
import json

# Global variable to hold the mocked Firestore client instance
mock_db_instance = None
app = None  # Will hold the Flask app after importing

# Patch firestore.Client BEFORE importing main.py
# Ensures Firestore client inside main.py uses the mock instead of making real GCP calls
with patch('google.cloud.firestore.Client') as MockFirestoreClient:
    mock_db_instance = MagicMock()  # Create a mock Firestore client
    MockFirestoreClient.return_value = mock_db_instance  # Override Client() to return our mock
    from main import app  # Now import main.py (which uses firestore.Client)

# Automatically use this fixture for all tests
# Resets mock Firestore client state before each test to avoid side effects
@pytest.fixture(autouse=True)
def mock_firestore_db():
    mock_db_instance.reset_mock()  # Clear any previous mock calls

    # Set up mock collection and document references
    mock_collection_ref = MagicMock()
    mock_document_ref = MagicMock()

    # Simulate db.collection('views') returning a mock
    mock_db_instance.collection.return_value = mock_collection_ref
    # Simulate .document('counter') returning a mock
    mock_collection_ref.document.return_value = mock_document_ref

    yield mock_db_instance  # Provide the mock to test functions


# Test the OPTIONS preflight CORS behavior for /
def test_options_request():
    with app.test_client() as client:
        # First test: basic OPTIONS request without special headers
        response = client.options('/')
        assert response.status_code == 200  # Should succeed
        assert response.data == b''  # Should return empty body
        assert 'Access-Control-Allow-Origin' in response.headers
        assert response.headers['Access-Control-Allow-Origin'] == '*'  # Allow all origins

        # Now simulate a full preflight OPTIONS request with CORS headers
        simulated_request_headers = {
            'Origin': 'http://example.com',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type',
        }

        response = client.options('/', headers=simulated_request_headers)
        assert response.status_code == 200  # Should still succeed
        headers = response.headers

        # Should echo back the origin
        assert headers['Access-Control-Allow-Origin'] == simulated_request_headers['Origin']

        # CORS allows these methods — must be a superset
        expected_methods = {'GET', 'POST', 'OPTIONS'}
        # Split the returned comma-separated string into a set
        returned_methods = set(m.strip() for m in headers['Access-Control-Allow-Methods'].split(','))
        assert expected_methods <= returned_methods  # Allow HEAD or other extras too

        # Ensure allowed headers include 'Content-Type'
        assert 'Access-Control-Allow-Headers' in headers
        assert 'Content-Type' in headers['Access-Control-Allow-Headers']


# Test when there’s no visitor record yet — first-time visitor
def test_new_visitor(mock_firestore_db):
    # Simulate Firestore doc not existing yet
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.return_value = MagicMock(exists=False)

    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200  # Successful call
        assert response.headers['Content-Type'] == 'application/json'
        data = response.json
        assert data['count'] == 1  # New visitor count should be 1

        # Ensure .set() was used to create the new document
        mock_doc_ref.set.assert_called_once_with({"count": 1})
        # Ensure .update() was NOT called
        mock_doc_ref.update.assert_not_called()


# Test when a visitor has already been counted before
def test_existing_visitor(mock_firestore_db):
    # Simulate Firestore document already existing with count 5
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.return_value = MagicMock(exists=True, to_dict=lambda: {"count": 5})

    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200  # Successful request
        assert response.headers['Content-Type'] == 'application/json'
        data = response.json
        assert data['count'] == 6  # Incremented from 5 to 6

        mock_doc_ref.get.assert_called_once()  # Ensure get() was called
        mock_doc_ref.update.assert_called_once_with({"count": 6})  # Ensure correct update
        mock_doc_ref.set.assert_not_called()  # Should not create new document


# Test error handling — simulate Firestore connection failure
def test_error_handling(mock_firestore_db, capsys):
    # Simulate Firestore throwing an exception during .get()
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.side_effect = Exception("Simulated Firestore connection error")

    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 500  # Internal server error
        assert response.headers['Content-Type'] == 'application/json'
        data = response.json
        assert data['error'] == "Failed to update visitor count"  # Expected error message

        # Ensure the error message was printed to logs
        captured = capsys.readouterr()
        assert "An error occurred: Simulated Firestore connection error" in captured.out
