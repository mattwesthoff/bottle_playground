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

@route('/oauth2callback')
def oauth2callback():
	if request.query.code:
		http = httplib2.Http()
		data = dict(code=request.query.code,
			client_id="290910061097.apps.googleusercontent.com",
			client_secret="38xorQwbOrcrPbFQG-3_NuHG",
			redirect_uri="http://localhost:8080/oauth2callback",
			grant_type="authorization_code")
		url = "https://accounts.google.com/o/oauth2/token"
		headers={"Content-Type":"application/x-www-form-urlencoded"}
		resp, content = http.request(url, "POST", headers=headers,
			body=urlencode(data))
		if resp['status'] == '200':
			c = simplejson.loads(content)
			access_token = c['access_token']
			url = "https://www.googleapis.com/plus/v1/people/me"
			auth_header="OAuth %s" % access_token
			r, cnt = http.request(url, "GET", 
				headers={"Authorization":auth_header})
			if resp['status'] == '200':
				user_data = simplejson.loads(cnt)
				return "<img src='%s' />%s" % \
					(user_data['image']['url'], user_data['displayName'])
			return "h: %s<br />t: %s<br />r: %s<br />cnt: %s<br />c: %s" % \
				(auth_header, access_token, r, cnt, c)
		return "r: %s<br />c: %s" % (resp, content)
	else:	
		return "here!" 

@route('/oauth2token')
def oauth2token():
	return "token time"

run(host='localhost', port=8080)
