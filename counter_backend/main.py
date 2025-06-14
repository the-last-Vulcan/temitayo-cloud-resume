import json
import os
from google.cloud import firestore
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (for local dev or Cloud Run; replace "*" with your domain for production)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firestore client globally
db = firestore.Client()

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def count_visitors():
    """
    HTTP Flask endpoint to count website visitors using Firestore.
    Each call increments the counter in the 'views' collection.
    """

    # Explicitly handle OPTIONS (preflight) requests to avoid Firestore access
    if request.method == 'OPTIONS':
        # Let Flask-CORS add the appropriate headers
        return '', 200

    doc_ref = db.collection('views').document('counter')
    new_count = 0

    try:
        # Attempt to get the current visitor count
        doc = doc_ref.get()
        if doc.exists:
            current_count = doc.to_dict().get("count", 0)
            new_count = current_count + 1
            doc_ref.update({"count": new_count})
        else:
            new_count = 1
            doc_ref.set({"count": new_count})

        return jsonify({"count": new_count}), 200

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Failed to update visitor count"}), 500

# Entry point for running locally (e.g., for testing or dev server)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
