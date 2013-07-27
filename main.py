from flask import Flask
app = Flask(__name__)

@app.route('/target/200', methods=['POST'])
def mail_receive():
    return 'Hello World!'

@app.route('/')
def index():
    return 'Send an email with a GPX attached (max 100ko) to b29d062265b9b6b211c0@cloudmailin.net'

if __name__ == '__main__':
    app.run()