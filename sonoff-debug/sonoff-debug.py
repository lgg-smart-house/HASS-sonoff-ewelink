# -*- coding: utf-8 -*-
import argparse, sys, json, time, random, pprint, base64, requests, hmac, hashlib, re

# named params	
if not sys.argv[1].startswith('-') and not sys.argv[2].startswith('-'):
	email 		= sys.argv[1]
	password 	= sys.argv[2]

else:
	parser=argparse.ArgumentParser()
	parser.add_argument('-e', '--email', 		help='email used for eWeLink app')
	parser.add_argument('-p', '--password', 	help='password for email/account')

	args=parser.parse_args()

	# positional params
	if hasattr(args, 'email') and hasattr(args, 'password'):
		email 		= args.email
		password 	= args.password

	else:
		print 'Please read the instructions better!'
		sys.exit(1)

def gen_nonce(length=8):
	"""Generate pseudorandom number."""
	return ''.join([str(random.randint(0, 9)) for i in range(length)])

headers = {'Content-Type'  : 'application/json'}
user_details = {}
api_region='us'

def do_login():
	global api_region

	decryptedAppSecret = '6Nz4n0xA8s8qdxQf2GqurZj2Fs55FUvM'
	
	app_details = {
		'email'     : email,
		'password'  : password,
		'version'   : '6',
		'ts'        : int(time.time()),
		'nonce'     : gen_nonce(15),
		'appid'     : 'oeVkj2lYFGnJu5XUtWisfW4utiN4u9Mq',
		'imei'      : '01234567-89AB-CDEF-0123-456789ABCDEF',
		'os'        : 'iOS',
		'model'     : 'iPhone10,6',
		'romVersion': '11.1.2',
		'appVersion': '3.5.3'
	}

	hex_dig = hmac.new(decryptedAppSecret, json.dumps(app_details), digestmod=hashlib.sha256).digest()
	sign = base64.b64encode(hex_dig).decode()

	headers.update({'Authorization' : 'Sign ' + sign})
	r = requests.post('https://%s-api.coolkit.cc:8080/api/user/login' % api_region, headers=headers, json=app_details)
	resp = r.json()
	
	if 'error' in resp and 'region' in resp and resp['error'] == 301:
		# re-login using the new localized endpoint
		api_region = resp['region']
		do_login()

	else:
		global user_details
		user_details = r.json()

def get_devices():
	headers.update({'Authorization' : 'Bearer ' + user_details['at']})
	r = requests.get('https://%s-api.coolkit.cc:8080/api/user/device' % api_region, headers=headers)
	devices = r.json()

	return json.dumps(devices, indent=2, sort_keys=True)

def clean_data(data):
	data = re.sub(r'"phoneNumber": ".*"', '"phoneNumber": "[hidden]"', data)
	data = re.sub(r'"name": ".*"', '"name": "[hidden]"', data)
	data = re.sub(r'"ip": ".*",', '"ip": "[hidden]"', data)
	data = re.sub(r'"deviceid": ".*",', '"deviceid": "[hidden]"', data)
	data = re.sub(r'"_id": ".*",', '"_id": "[hidden]"', data)
	data = re.sub(r'"\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}"', '"xx:xx:xx:xx:xx:xx"', data)
	data = re.sub(r'"\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"', '"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"', data)
	return data

if __name__ == "__main__":
	do_login()
	devices_json = get_devices()
	print clean_data(devices_json)

