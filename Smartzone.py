#!/usr/bin/env python3
# smartzone API module

import requests
# ignore self signed cert errors:
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import certifi
import json


class Smartzone():

	# sets SZ API version to use in all modules
	global api_version
	global sz_json
	api_version = 'v9_1'
	sz_json = 'api.json'


	def __init__(self):

		with open(sz_json, 'r') as f:
			api = json.load(f)
	
		global session,sessionid,request,host
		session,sessionid,request = self.logon(api['username'],api['password'],api['hostname'])
		host = api['hostname']

	def logon(self,username,password,hostname):
		data = {
			"username": username,
			"password": password,
			"timeZoneUtcOffset": "+00:00"
		}

		try:
			session = requests.Session()

			request = session.post('https://'+ hostname +':8443/wsg/api/public/' + api_version + '/session', verify=False,json=data)
			request.raise_for_status()
		except requests.exceptions.RequestException as e:
			print(e)
			exit()
		else:
			headers = request.headers['Set-Cookie'].split(';')
			sessionid = headers[0].split('=')[1]

			return session,sessionid,request

	def return_api_version():
		# function to return set api version
		return api_version


	def http_method(verb,command,payload):

		api_headers = {'Content-Type': 'application/json;charset=UTF-8','Cookie': 'JSESSIONID=' + sessionid}
		try:
			if verb == "GET":
				request = session.get('https://'+ host + ':8443/wsg/api/public' + command, verify=False,headers=api_headers,json=payload)
				#print(request.request.url)
				request.raise_for_status()
			elif verb == "POST":
				request = session.post('https://'+ host + ':8443/wsg/api/public' + command, verify=False,headers=api_headers,json=payload)
				#print(request.request.body)	
				request.raise_for_status()
			elif verb == "PUT":
				request = session.put('https://'+ host + ':8443/wsg/api/public' + command, verify=False,headers=api_headers,json=payload)
				request.raise_for_status()
			elif verb == "PATCH":
				request = session.patch('https://'+ host + ':8443/wsg/api/public' + command, verify=False,headers=api_headers,json=payload)
				request.raise_for_status()
			elif verb == "DELETE":
				request = session.delete('https://'+ host + ':8443/wsg/api/public' + command, verify=False,headers=api_headers,json=payload)
				request.raise_for_status()
		except requests.exceptions.RequestException as e:
			return e
			exit()
		else:
			return request









