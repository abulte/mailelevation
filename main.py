from flask import Flask, request
app = Flask(__name__)

app.debug = True

@app.route('/incoming/email', methods=['POST'])
def mail_receive():
    app.logger.info(request.form)
    app.logger.info(request.files)
    return 'OK'

@app.route('/')
def index():
	app.logger.debug('Coucou')
	return 'Send an email with a GPX attached (max 100ko) to b29d062265b9b6b211c0@cloudmailin.net'

if __name__ == '__main__':
    app.run()