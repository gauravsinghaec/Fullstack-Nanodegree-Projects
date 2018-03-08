# Run a test server.
from app import app
# if __name__ == '__main__':
# PORT = int(os.environ.get('PORT'))
PORT = 8000
app.run(host='0.0.0.0', port=PORT)