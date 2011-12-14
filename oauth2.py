from bottle import route, run, request, redirect
import httplib2
from urllib import urlencode
import simplejson

@route('/gauth')
def googleAuth():
	client_id = "290910061097.apps.googleusercontent.com"
	url = "https://accounts.google.com/o/oauth2/auth"
	url += "?response_type=code&client_id=%s" % client_id
	url += "&redirect_uri=http://localhost:8080/oauth2callback"
	url += "&scope=https://www.googleapis.com/auth/plus.me"
	url += "&approval_prompt=force"

	redirect(url)

def get_google_token(auth_code):
	http = httplib2.Http()
	data = dict(code=auth_code,
		client_id="290910061097.apps.googleusercontent.com",
		client_secret="38xorQwbOrcrPbFQG-3_NuHG",
		redirect_uri="http://localhost:8080/oauth2callback",
		grant_type="authorization_code")
	url = "https://accounts.google.com/o/oauth2/token"
	r_token, c_token = http.request(url, "POST", 
		headers={"Content-Type":"application/x-www-form-urlencoded"},
		body=urlencode(data))
	if r_token['status'] == '200':
		return simplejson.loads(c_token)['access_token']
	else:
		return None

def get_google_data(token):
	if not token:
		return None
	http = httplib2.Http()
	url = "https://www.googleapis.com/plus/v1/people/me"
	r_data, c_data = http.request(url, "GET", 
		headers={"Authorization":("OAuth %s" % token)})
	if r_data['status'] == '200':
		return simplejson.loads(c_data)
	else:
		return None

@route('/oauth2callback')
def oauth2callback():
	if request.query.code:
		token = get_google_token(request.query.code)
		if not token:
			return "unable to get an access token!"
		
		user_data = get_google_data(token)
		if user_data:
			return "<img src='%s' />%s" % \
				(user_data['image']['url'], user_data['displayName'])
		return "An error occurred getting your user data"
	return "Didn't get a code from your idp!"

run(host='localhost', port=8080)
