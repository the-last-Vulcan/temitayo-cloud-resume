# counter_backend/test_main.py

import pytest
from unittest.mock import MagicMock, patch
import json

# Global variable to hold the mocked Firestore client instance
mock_db_instance = None
app = None  # Will hold the Flask app

# Patch firestore.Client BEFORE importing main.py
with patch('google.cloud.firestore.Client') as MockFirestoreClient:
    mock_db_instance = MagicMock()
    MockFirestoreClient.return_value = mock_db_instance
    from main import app  # Now import after mocking


@pytest.fixture(autouse=True)
def mock_firestore_db():
    mock_db_instance.reset_mock()

    mock_collection_ref = MagicMock()
    mock_document_ref = MagicMock()

    mock_db_instance.collection.return_value = mock_collection_ref
    mock_collection_ref.document.return_value = mock_document_ref

    yield mock_db_instance


# Updated CORS preflight OPTIONS test
def test_options_request():
    with app.test_client() as client:
        response = client.options('/')

        assert response.status_code == 200
        assert response.data == b''  # Flask-CORS returns empty body for OPTIONS
        headers = response.headers

        assert 'Access-Control-Allow-Origin' in headers
        assert headers['Access-Control-Allow-Origin'] == '*'

        # Flask-CORS returns headers only if the request includes Origin and Access-Control headers.
        # We simulate that below.
        simulated_request_headers = {
            'Origin': 'http://example.com',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type',
        }

        response = client.options('/', headers=simulated_request_headers)

        assert response.status_code == 200
        headers = response.headers
        assert headers['Access-Control-Allow-Origin'] == simulated_request_headers['Origin']
        assert headers['Access-Control-Allow-Methods'] == 'GET,HEAD,POST,OPTIONS'
        assert 'Access-Control-Allow-Headers' in headers


def test_new_visitor(mock_firestore_db):
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.return_value = MagicMock(exists=False)

    with app.test_client() as client:
        response = client.get('/')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'
        data = response.json
        assert data['count'] == 1

        mock_doc_ref.set.assert_called_once_with({"count": 1})
        mock_doc_ref.update.assert_not_called()


def test_existing_visitor(mock_firestore_db):
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.return_value = MagicMock(exists=True, to_dict=lambda: {"count": 5})

    with app.test_client() as client:
        response = client.get('/')

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'
        data = response.json
        assert data['count'] == 6

        mock_doc_ref.get.assert_called_once()
        mock_doc_ref.update.assert_called_once_with({"count": 6})
        mock_doc_ref.set.assert_not_called()


def test_error_handling(mock_firestore_db, capsys):
    mock_doc_ref = mock_firestore_db.collection.return_value.document.return_value
    mock_doc_ref.get.side_effect = Exception("Simulated Firestore connection error")

    with app.test_client() as client:
        response = client.get('/')

        assert response.status_code == 500
        assert response.headers['Content-Type'] == 'application/json'
        data = response.json
        assert data['error'] == "Failed to update visitor count"

        captured = capsys.readouterr()
        assert "An error occurred: Simulated Firestore connection error" in captured.out
