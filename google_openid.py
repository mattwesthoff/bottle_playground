from bottle import route, run, request, template, static_file, redirect
from openid.consumer import consumer
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import ax, pape, sreg

@route('/hello/<name>')
def hello(name='person'):
	return '<b>Hello %s</b><br />%s' % (name, request.query.to)

@route('/yeah')
def yeah():
	return '<html><body><h1>you came from: %s</h1></body></html>' % request.url

@route('/redirect')
def redir():
	redirect(request.query.to)

@route('/startlogin')
def startLogin():
	c = consumer.Consumer({}, None)
	error = None
	try:
		auth_request = c.begin("https://www.google.com/accounts/o8/id")
	except DiscoveryFailure, e:
		error = "OpenID discovery error: %s" % (str(e),)
	if error:
		return error

	ax_request = ax.FetchRequest()
	ax_request.add(ax.AttrInfo('http://axschema.org/contact/email', required=True))
	ax_request.add(ax.AttrInfo('http://axschema.org/namePerson/first', required=True))
	ax_request.add(ax.AttrInfo('http://axschema.org/namePerson/last', required=True))
	auth_request.addExtension(ax_request)
	
	
	trust_root = "http://localhost:8080/"
	return_to = "http://localhost:8080/endlogin"	

	if auth_request.shouldSendRedirect():
		url = auth_request.redirectURL(trust_root, return_to)
		redirect(url)
	else:
		form_html = auth_request.formMarkup(trust_root, return_to, False, {'id': 'openid_message'})
		html = """<html><body onload="document.getElementById('openid_message').submit()">%s</body></html>"""
		return html % form_html

@route('/endlogin')
def endLogin():
	c = consumer.Consumer({}, None)
	return_to = "http://localhost:8080/endlogin"
	response = c.complete(request.query, return_to)

	if response.status == consumer.SUCCESS:
	 	ax_response = ax.FetchResponse.fromSuccessResponse(response)
		if ax_response:
			email = ax_response.get('http://axschema.org/contact/email')
			first_name = ax_response.get('http://axschema.org/namePerson/first')
			last_name = ax_response.get('http://axschema.org/namePerson/last')
			output = "email is %s, firstname: %s, lastname: %s" % (email,first_name,last_name)
			return output

		return "success!"
	
	if response.status == consumer.CANCEL:
		return "cancelled"

	if response.status == consumer.FAILURE:
		return "failure"

run(host='localhost', port=8080)
