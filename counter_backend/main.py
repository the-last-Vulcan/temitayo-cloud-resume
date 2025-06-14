import json
import os
from google.cloud import firestore
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Enable CORS - allow any origin for development
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firestore client
db = firestore.Client()

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def count_visitors():
    # Explicitly handle OPTIONS (CORS preflight)
    if request.method == 'OPTIONS':
        response = make_response('', 200)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response

    doc_ref = db.collection('views').document('counter')
    new_count = 0

    try:
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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
