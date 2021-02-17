from gevent.pywsgi import WSGIServer
from flask import Flask, request, send_from_directory
from wtforms import Form, StringField, validators

flag = 'ctf{00000000000000000000000000000000}'

app = Flask(__name__)

def encrypt_data(flag, key):
	mapping = {}
	freq = {}

	i = 0
	for flag_ch in flag:
		key_ch = key[i]

		mapping[ord(key_ch)] = flag_ch

		if flag_ch in freq:
			freq[flag_ch] += 1
		else:
			freq[flag_ch] = 1

		i += 1

	output = []

	for i in range(len(key)):
		key_ord = ord(key[i])
		flag_ch = mapping[key_ord]

		output.append(hash(str(ord(flag_ch) * freq[flag_ch]) + flag_ch + key[i]))

		if freq[flag_ch] - 1 == 0:
			del freq[flag_ch]
		else:
			freq[flag_ch] -= 1

	return output


class FlagEncryptionForm(Form):
	key = StringField('key', [validators.InputRequired()])

	def validate_key(form, field):
		if len(field.data) != len(flag) or len(set(field.data)) != len(field.data):
			raise validators.ValidationError('invalid encryption key!')


@app.errorhandler(Exception)
def handle_exception(e):
	# allows us to make exceptions and return the exception's message instead of a generic 500!
	return str(e)

@app.route('/encrypt', methods=['POST'])
def encrypt():
	form = FlagEncryptionForm(request.form)
	if form.validate():
		return str(encrypt_data(flag, form.key.data.upper()))
	else:
		raise Exception('invalid encryption key!')

@app.route('/')
def index():
	return send_from_directory('', 'index.html')

WSGIServer(('0.0.0.0', 5000), app).serve_forever()