import functions_framework
import json
from google.cloud import firestore

# Initialize Firestore client globally to reuse across invocations
# This is a best practice for Cloud Functions.

@functions_framework.http
def count_visitors(request):
    """
    HTTP Cloud Function to count website visitors using Firestore.
    Each call increments the counter in the 'views' collection.
    """
    db = firestore.Client()
    # Set CORS headers for preflight and actual requests
    # Adjust 'Access-Control-Allow-Origin' to your specific resume domain (e.g., 'https://yourdomain.com')
    # Using '*' allows any origin, which is fine for a challenge but less secure for production.
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600' # Cache preflight response for 1 hour
    }

    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        # Respond to preflight request with CORS headers and 204 No Content
        return ('', 204, headers)

    doc_ref = db.collection('views').document('counter')
    new_count = 0 # Initialize new_count outside the try block

    try:
        # Read existing count
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

        # Return the new visitor count as a string with HTTP 200 OK and CORS headers
        return (json.dumps({"count": new_count}), 200, headers)

    except Exception as e:
        # Log the error for debugging purposes in Cloud Logging
        print(f"An error occurred: {str(e)}")
        # Return an error message to the frontend with HTTP 500 Internal Server Error and CORS headers
        return (json.dumps({"error": str(e)}), 500, headers)