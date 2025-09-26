import json # common for API handling
import os # Used to access environment variables like PORT
from google.cloud import firestore # Imports the Firestore client library for database interaction
from flask import Flask, request, jsonify, make_response # Imports Flask core components for web application development
from flask_cors import CORS # Imports CORS extension for Flask to handle Cross-Origin Resource Sharing

# Initialize Flask app
# Creates an instance of the Flask web application.
app = Flask(__name__)

# Enable CORS - allow any origin.
# flask-cors will automatically handle preflight (OPTIONS) requests and add necessary CORS headers to all responses from this Flask app.

CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]}})# lets flask-cors handle all origins for now

# Initialize Firestore client, Creates a client object to interact with the Firestore database.
# The project ID is usually picked up automatically from the environment (e.g., Cloud Run).
db = firestore.Client()

@app.route('/', methods=['GET', 'POST'])
# Defines a route for the root URL ('/').
# It accepts GET (to retrieve count) and POST (to increment/update count) requests.

def count_visitors():
   
    # Defines a reference to a specific document in Firestore.
    # It points to a document named 'counter' within the 'views' collection.
    doc_ref = db.collection('views').document('counter')
    new_count = 0 # Initializes a variable to hold the updated count

    try:
        # Attempts to retrieve the 'counter' document from Firestore.
        doc = doc_ref.get()
        if doc.exists:
            # If the document exists, get the current 'count' value. Defaults to 0 if 'count' field is missing.
            current_count = doc.to_dict().get("count", 0)
            new_count = current_count + 1 # Increment the count by 1
            # Update the 'count' field in the existing Firestore document.
            doc_ref.update({"count": new_count})
        else:
            # If the document does not exist (first visitor), set the count to 1.
            new_count = 1
            # Create the 'counter' document with the initial count.
            doc_ref.set({"count": new_count})

        # Returns the new count as a JSON response with a 200 OK status.
        # flask-cors will automatically add the 'Access-Control-Allow-Origin' header to this response.
        return jsonify({"count": new_count}), 200

    except Exception as e:
        # Catches any exceptions that occur during the Firestore operation.
        print(f"An error occurred: {str(e)}") # Prints the error to the console (useful for Cloud Run logs)
        # Returns an error message as JSON with a 500 Internal Server Error status.
        # flask-cors will also add the 'Access-Control-Allow-Origin' header to this error response.
        return jsonify({"error": "Failed to update visitor count"}), 500

# This block ensures the Flask app runs only when the script is executed directly.
if __name__ == '__main__':
    # Gets the port from the environment variable 'PORT' (set by Cloud Run), defaulting to 8080.
    port = int(os.environ.get("PORT", 8080))
    # Runs the Flask application.
    # debug=False: Disables debug mode for production (important for security and performance).
    # host="0.0.0.0": Makes the server accessible from any IP, necessary for Cloud Run.
    # port=port: Uses the port specified by the environment variable.
    app.run(debug=False, host="0.0.0.0", port=port)