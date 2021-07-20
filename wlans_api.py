#!/usr/bin/env python3

try:

	import requests
	import certifi
	import argparse
	import json
	import sys
	from Smartzone import Smartzone
	from prettytable import PrettyTable
	from zones_api import Zones

except ImportError:
	print('error importing modules')
	exit(1)

class Wlans():

	global api_version
	api_version = Smartzone.return_api_version()

	def parse_args(self):
		parser = argparse.ArgumentParser(description="Smartzone platform",conflict_handler='resolve')
		parser.add_argument("-get-wlans", action="store", dest="get_wlans", nargs=2, metavar=('<ZONE NAME>','<DOMAIN NAME>'), help="get wlans in <ZONE NAME> <DOMAIN NAME>")
		parser.add_argument("-create-wpa2-wlan", action="store", dest="create_wpa2_wlan", nargs=9,  metavar=('<ZONE NAME>','<DOMAIN NAME>','<COUNTRY CODE>', '<SSID>', '<NAME>', '<PSK>', '<DESCRIPTION>', '<VLAN>', '<ISOLATION>'), help="create new WPA2 WLAN in <zone> <domain> <country> with <SSID> <name> <PSK> <description> <VLANID>  and <isolation> set to  'on' for enabled or 'off' for disabled")
		parser.add_argument("-delete-wlan", action="store", dest="delete_wlan", nargs=3, metavar=('<ZONE NAME>','<DOMAIN NAME>', '<WLAN ID>'), help="delete WLAN in <ZONE NAME> <DOMAIN NAME> with WLAN ID <WLAN ID>")
		parser.add_argument("-clone-wlan-group", action="store", dest="clone_wlans", nargs=3, metavar=('<ZONE NAME>','<DOMAIN NAME>', ''), help="delete WLAN in <ZONE NAME> <DOMAIN NAME> with WLAN ID <WLAN ID>")
		parseargs = vars(parser.parse_args(None if sys.argv[1:] else ['-h']))

		get_wlans = parseargs['get_wlans']
		delete_wlan = parseargs['delete_wlan']
		create_wpa2_wlan = parseargs['create_wpa2_wlan']

		if parseargs['get_wlans']:
			items = ['zonename','domainname']
			get_wlans = dict(zip(items,parseargs['get_wlans']))

		if parseargs['create_wpa2_wlan']:
			items = ['zonename','domainname','country','ssid','name','psk','description','vlan','isolation']
			create_wpa2_wlan = dict(zip(items,parseargs['create_wpa2_wlan']))

		if parseargs['delete_wlan']:
			items = ['zonename','domainname','wlanid']
			delete_wlan = dict(zip(items,parseargs['delete_wlan']))

		return create_wpa2_wlan,get_wlans,delete_wlan

	def load_smartzone(self):
		# initiates connection object for SZ controller API
		s = Smartzone()

		return s

	def load_ssid_template(self,country):
		# loads SSID template file in JSON for processing
		try:
			with open('template_schemas/ssid_template_' + country + '.json', 'r') as f:
				data = json.load(f)
			return data

		except OSError as error : 
			print(error)
			exit('error loading SSID template file - does the JSON file exist?')

	def create_wpa2_wlan(self,zonename,domainname,country,ssid,name,psk,description,vlan,isolation):
		# builds new wpa2 PSK secured SSID
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)

		data = self.load_ssid_template(country)

		payload = self.create_wpa2_wlan_schema(data,zonename,ssid,name,psk,description,vlan,isolation)

		command = '/' + api_version + '/rkszones/' + zone_id + '/wlans'

		output = Smartzone.http_method('POST',command,payload)

		if 'ok' in dir(output):
			print('wlan created with id ' + output.json()['id'])
		else:
			exit('error in API call has occured when creating wlan: ' + str(output))


	def create_wpa2_wlan_schema(self,data,zonename,ssid,name,psk,description,vlan,isolation):
		# builds third party wpa2 secured JSON schema
		data['name'] = name
		data['ssid'] = ssid
		data['description'] = description
		data['vlan']['accessVlan'] = int(vlan)

		if isolation == 'on':
			data['advancedOptions']['clientIsolationEnabled'] = True
			data['advancedOptions']['clientIsolationUnicastEnabled'] = True
			data['advancedOptions']['clientIsolationMulticastEnabled'] = True
		else:
			data['advancedOptions']['clientIsolationEnabled'] = False
			data['advancedOptions']['clientIsolationUnicastEnabled'] = False
			data['advancedOptions']['clientIsolationMulticastEnabled'] = False


		del(data['authServiceOrProfile'])
		data['encryption']['method'] = 'WPA2'
		data['encryption']['algorithm'] = 'AES'
		data['encryption']['passphrase'] = psk

		with open('zone_schemas/' + name + '_wpa2_wlan_' + str(zonename) + '.json','w') as f:
			json.dump(data,f,indent=4)

		f.close()

		return data

	
	def get_wlans(self,zonename,domainname):
		z = Zones()
		domain_id =z.fetch_domain_id(domainname)
		zone_id = z.fetch_zone_id(zonename,domainname)

		command = '/' + api_version + '/rkszones/' + zone_id + '/wlans'

		try:
			output = Smartzone.http_method('GET',command,'').json()
			return json.dumps(output,indent=4)
		except:
			exit('could not load zone with id ' + zoneid)

	def delete_wlan(self,zonename,domainname,wlanid):
		z = Zones()
		domain_id =z.fetch_domain_id(domainname)
		zone_id = z.fetch_zone_id(zonename,domainname)

		command = '/' + api_version + '/rkszones/' + zone_id + '/wlans/' + wlanid

		output = Smartzone.http_method('DELETE',command,'')

		if 'ok' in dir(output):
			print('wlan deleted with id ' + wlanid)
		else:
			exit('error in API call has occured when creating wlan: ' + str(output))

	def get_wlan_groups(self,zonename,domainname):
		z = Zones()
		domain_id =z.fetch_domain_id(domainname)
		zone_id = z.fetch_zone_id(zonename,domainname)

		command = '/' + api_version + '/rkszones/' + zpone_id + '/wlangroups'

	
if __name__ == "__main__":
	w = Wlans()
	create_wpa2_wlan,get_wlans,delete_wlan = w.parse_args()

	if create_wpa2_wlan:
		w.load_smartzone()
		w.create_wpa2_wlan(create_wpa2_wlan['zonename'],create_wpa2_wlan['domainname'],create_wpa2_wlan['country'],create_wpa2_wlan['ssid'],create_wpa2_wlan['name'],create_wpa2_wlan['psk'],create_wpa2_wlan['description'],create_wpa2_wlan['vlan'],create_wpa2_wlan['isolation'])

	if get_wlans:
		w.load_smartzone()
		print(w.get_wlans(get_wlans['zonename'],get_wlans['domainname']))

	if delete_wlan:
		w.load_smartzone()
		w.delete_wlan(delete_wlan['zonename'],delete_wlan['domainname'],delete_wlan['wlanid'])
