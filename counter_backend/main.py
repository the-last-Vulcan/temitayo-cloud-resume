import json
import os
from google.cloud import firestore
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for your Flask app.
# IMPORTANT: For production, replace "*" with your specific resume domain (e.g., 'https://www.temitayoapata.online')
# Using "*" allows any origin, which is suitable for a challenge/development.
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firestore client globally to reuse across invocations.
# This is a best practice for serverless environments like Cloud Run.
db = firestore.Client()

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def count_visitors():
    """
    HTTP Flask endpoint to count website visitors using Firestore.
    Each call increments the counter in the 'views' collection.
    Handles GET, POST, and OPTIONS (preflight) requests.
    """
    # NO EXPLICIT OPTIONS HANDLING HERE. Flask-CORS will handle it automatically
    # because 'OPTIONS' is in the methods list for the route.
   
    doc_ref = db.collection('views').document('counter')
    new_count = 0 # Initialize new_count for scope

    try:
        # Get the current count from Firestore
        doc = doc_ref.get()
        if doc.exists:
            current_count = doc.to_dict().get("count", 0)
            new_count = current_count + 1
            # Update the document with the new count
            doc_ref.update({"count": new_count})
        else:
            # If the document doesn't exist, create it with count = 1
            new_count = 1
            doc_ref.set({"count": new_count})

        # Return the new visitor count as JSON with HTTP 200 OK.
        # jsonify automatically sets 'Content-Type: application/json'.
        return jsonify({"count": new_count}), 200

    except Exception as e:
        # Log the error for debugging purposes (visible in Cloud Logging)
        print(f"An error occurred: {str(e)}")
        # Return a generic error message to the frontend with HTTP 500 Internal Server Error
        # Ensure we return a plain string error message, not the exception object itself.
        return jsonify({"error": "Failed to update visitor count"}), 500


# This block is crucial for running the Flask application as a web server.
# Cloud Run expects your application to listen on the port specified by the PORT environment variable,
# which defaults to 8080 if not explicitly set.
if __name__ == '__main__':
    # Get the port from the environment variable or default to 8080
    port = int(os.environ.get("PORT", 8080))
    # Run the Flask app on all available network interfaces (0.0.0.0)
    # debug=False is important for production/Cloud Run environments.
    app.run(debug=False, host="0.0.0.0", port=port)