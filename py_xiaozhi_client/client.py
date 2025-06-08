from flask import Flask, request, jsonify

app = Flask(__name__)

def handle_request(request_data):
  """Handles the request data."""
  print(f"Received request: {request_data}")

@app.route('/debug_request', methods=['POST'])
def debug_request_route():
  """Handles the debug request route."""
  request_data = request.get_json()
  handle_request(request_data)
  return jsonify({"status": "success", "message": "Request received"})

if __name__ == '__main__':
  app.run(debug=True, port=5000)
