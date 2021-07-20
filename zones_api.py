#!/usr/bin/env python3

try:

	import requests
	import certifi
	import argparse
	import json
	import sys
	from Smartzone import Smartzone
	from prettytable import PrettyTable

except ImportError:
	print('error importing modules')
	exit(1)

class Zones():

	global api_version
	api_version = Smartzone.return_api_version()

	def parse_args(self):
		parser = argparse.ArgumentParser(description="Smartzone platform",conflict_handler='resolve')
		parser.add_argument("-list-domains", action="store_true", dest="list_domains", help="list all domains")
		parser.add_argument("-list-zones", action="store", dest="list_zones", metavar="<DOMAIN NAME>", help="list all zones in <domain name>")
		parser.add_argument("-list-zones-default", action="store_true", dest="list_zones_default", help="list all zones in the default domain")
		parser.add_argument("-list-zone-firmwares", action="store", dest="list_zone_firmwares", nargs=2, metavar=('<ZONE NAME>',' <DOMAIN NAME>'), help="list availible firmwares in <zone name> <domain name>")
		parser.add_argument("-get-zone", action="store", dest="get_zone", metavar="<ZONE ID>", help="Get Zone config of <zone ID>")
		parser.add_argument("-get-isolation", action="store", dest="get_isolation", metavar="<ZONE ID>", help="Get client isolation whitelist for <zone id>")
		parser.add_argument("-get-radius", action="store", dest="get_radius", metavar="<ZONE ID>", help="Get RADIUS server list for <zone id>")
		parser.add_argument("-get-zone-firmware", action="store", dest="get_zone_firmware", nargs=2, metavar=('<ZONE NAME>',' <DOMAIN NAME>'), help="get active firmware for <zone name> <domain name")
		parser.add_argument("-create-radius", action="store", dest="create_radius", nargs=4, metavar=('<ZONE ID>','<RADIUS IP>','<RADIUS NAME','<RADIUS SECRET'), help="Create new RADIUS profile for zone <zone id> with radius server <radius name> IP <radius ip> and secret <radius secret>")
		parser.add_argument("-create-zone",action="store",nargs=3,metavar=('<ZONE NAME>','<ZONE COUNTRY>','<DOMAIN NAME'),dest="create_zone",help="create new zone with name <zone name> using country template <country code> inside domain <domain name> ")
		parser.add_argument("-delete-radius", action="store", dest="delete_radius", nargs=2, metavar=('<ZONE ID>, <RADIUS ID>'), help="Delete radius profile in zone <zone id> and id <radius id>")
		parser.add_argument("-delete-zone", action="store", dest="delete_zone",metavar="<ZONE ID>", help='Delete zone with ID <zone id>')
		parser.add_argument("-delete-all-zones", action="store", dest="delete_all_zones",metavar="<DOMAIN NAME>", help='Delete all zones in <domain name>')
		parser.add_argument("-modify-zone", action="store", dest="modify_zone", nargs=2, metavar=('<ZONE ID>', '<JSON FILE>'), help="modify zone with ID <zone id> with attributes in JSON file <json file")
		parser.add_argument("-change-ap-firmware", action="store", dest="change_firmware", nargs=3, metavar=('<ZONE NAME>','<DOMAIN NAME>','<AP FIRMWARE>'), help="change AP firmware in <zone name> <domain name> to <firmware version>")
		parser.add_argument("--json", action="store_true", dest="json_flag", help="append to display output in raw JSON")
		parseargs = vars(parser.parse_args(None if sys.argv[1:] else ['-h']))

		modify_zone = parseargs['modify_zone']
		change_ap_firmware = parseargs['change_firmware']
		get_zone_firmware = parseargs['get_zone_firmware']
		list_zone_firmwares = parseargs['list_zone_firmwares']
		list_zones = parseargs['list_zones']
		list_domains = parseargs['list_domains']
		create_zone = parseargs['create_zone']
		create_radius = parseargs['create_radius']
		delete_radius = parseargs['delete_radius']

		if parseargs['modify_zone']:
			items = ['zoneid', 'jsonfile']
			modify_zone = dict(zip(items,parseargs['modify_zone']))

		if parseargs['change_firmware']:
			items = ['zonename', 'domainname','firmware']
			change_ap_firmware = dict(zip(items,parseargs['change_firmware']))

		if parseargs['get_zone_firmware']:
			items = ['zonename', 'domainname']
			get_zone_firmware = dict(zip(items,parseargs['get_zone_firmware']))

		if parseargs['list_zone_firmwares']:
			items = ['zonename','domainname']
			list_zone_firmwares = dict(zip(items,parseargs['list_zone_firmwares']))

		if parseargs['create_radius']:
			radius_items = ['zoneid','radiusip','radiusname','radiussecret']
			create_radius = dict(zip(radius_items,parseargs['create_radius']))
	
		if parseargs['create_zone']:
			zone_items  = ['name','country','domain']
			create_zone = dict(zip(zone_items,parseargs['create_zone']))

		if parseargs['delete_radius']:
			items = ['zoneid','radiusid']
			delete_radius = dict(zip(items,parseargs['delete_radius']))


		return parseargs['list_domains'],parseargs['list_zones'],create_zone,parseargs['get_zone'], \
		parseargs['delete_zone'],parseargs['delete_all_zones'],parseargs['get_isolation'],parseargs['get_radius'],create_radius,delete_radius,parseargs['list_zones_default'],list_zone_firmwares,get_zone_firmware,change_ap_firmware,modify_zone,parseargs['json_flag']

	def load_smartzone(self):
		# initiates connection object for SZ controller API
		s = Smartzone()

		return s

	def load_json(self,country):
		# loads country template file in JSON for processing
		try:
			with open('template_schemas/wlan_zone_template_' + country + '.json', 'r') as f:
				data = json.load(f)

			return data
			f.close()

		except:
			exit('error loading template file - does the JSON file exist?')

	def modify_zone(self,zoneid,json_file):
		# modifies attributes for a zone
		try:
			with open(json_file,'r') as f:
				payload = json.load(f)

			command = '/' + api_version + '/rkszones/'  + zoneid
			output = Smartzone.http_method('PATCH',command,payload)
			
			f.close()

		except:
			exit('error loading JSON file - does the JSON file exist?')

		if 'ok' in dir(output):	
			print('zone ' + zoneid + ' modified with JSON from ' + json_file)
		else:
			exit('error in API call has occured when modfying zone attributes: ' + str(output))

	def create_new_zone(self,data,name,country,domain):
		# creates a new zone in a particular domain using a JSON template file for each country 
		data['name'] = name
		data['domainId'] = self.fetch_domain_id(domain)
		
		with open('zone_schemas/wlan_zone_' + str(name) + '.json','w') as f:
			json.dump(data,f,indent=4)

		f.close()
		
		output = Smartzone.http_method('POST','/' + api_version + '/rkszones',data)

		if 'ok' in dir(output):
			self.create_client_isolation(output.json()['id'])
			return(output.json()['id'])
		else: 
			exit('error in API call has occurred when creating zone: ' + str(output))

	def create_client_isolation(self,zoneid):
		# creates client isolation whitelist for the zone configured from json template
		command = '/' + api_version + '/rkszones/' + zoneid + '/clientIsolationWhitelist'
		
		with open('template_schemas/client_isolation_whitelist.json') as template:
			payload = json.load(template)
			output = Smartzone.http_method('POST',command,payload)
		
		template.close()

		if 'ok' in dir(output):	
			return(output.json()['id'])
		else:
			exit('error in API call has occured when creating client isolation whitelist: ' + str(output))

	def client_isolation_table(self,zoneid,json_flag):
		# returns a table with client isolation data for a specific zone name
		command = '/' + api_version + '/rkszones/' + zoneid + '/clientIsolationWhitelist'
		output = Smartzone.http_method('GET',command,'').json()

		if json_flag != True:

			t = PrettyTable(['WHITELIST ID','ZONE ID','NAME','DESCRIPTION'])
			c = PrettyTable(['MAC','IP','DESCRIPTION'])

			for i in output['list']:
				t.add_row([i['id'],i['zoneId'],i['name'],i['description']])
				print(t)
				for w in i['whitelist']:
					c.add_row([w['mac'],w['ip'],w['description']])			
				print(c)
		else: 
				return json.dumps(output,indent=4)
		
	def domains_table(self,json_flag):
		# returns a table of all domains on the controller
		command = '/' + api_version + '/domains'
		output = Smartzone.http_method('GET',command,'').json()

		if json_flag != True:
			t = PrettyTable(['ID','Domain Name','Zone Count','AP Count'])

			for i in output['list']:
				t.add_row([i['id'],i['name'],i['zoneCount'],i['apCount']])
			return t
		else:
			return json.dumps(output,indent=4)

	def get_all_zones(self,domainname):
		#  dump all zones in a domain in JSON format
		domainid = self.fetch_domain_id(domainname)
		command = '/' + api_version + '/rkszones?domainId=' + str(domainid)
		output = Smartzone.http_method('GET',command,'').json()
		return output

	def get_all_zones_default(self):
		# dump all zones in defaulkt domain
		command = '/' + api_version + '/rkszones'
		output = Smartzone.http_method('GET',command,'').json()

		return output

	def zones_default_table(self,json_flag):
		# display table of all the zones in default domain
		zones = self.get_all_zones_default()

		if json_flag != True:

			t = PrettyTable(['ID','Zone Name'])

			for i in zones['list']:
				t.add_row([i['id'],i['name']])
			print(t)
		else:
			print(json.dumps(zones,indent=4))

	def zones_table(self,domainname,json_flag):
		# display table of all the zones in a domain 
		zones = self.get_all_zones(domainname)

		if json_flag != True:

			t = PrettyTable(['ID','Zone Name','Domain Name'])

			for i in zones['list']:
				t.add_row([i['id'],i['name'],domainname])
			print(t)
		else:
			print(json.dumps(zones,indent=4))
			

	def get_zone(self,zoneid):
		# get individual zone data and output in JSON 
		command = '/' + api_version + '/rkszones/' + zoneid
		
		try:
			output = Smartzone.http_method('GET',command,'').json()
			return json.dumps(output,indent=4)
		except:
			exit('could not load zone with id ' + zoneid)

	def get_zone_radius(self,zoneid,json_flag):
		# get all the radius servers configured for a zone 
		command = '/' + api_version + '/rkszones/' + zoneid + '/aaa/radius'

		if json_flag == True:

			try:
				output = Smartzone.http_method('GET',command,'').json()
				return json.dumps(output,indent=4)
			except:
				exit('could not load zone with id ' + zoneid)

		else:
			try:
				output = Smartzone.http_method('GET',command,'').json()
				t = PrettyTable(['ID','NAME','DESCRIPTION','SERVICE TYPE','PRIMARY IP','PRIMARY PORT','PRIMARY SECRET','SECONDARY IP','SECONDARY PORT','SECONDARY SECRET'])

				for i in output['list']:
					if i['secondary'] != None:
						t.add_row([i['id'],i['name'],i['description'],i['serviceType'],i['primary']['ip'],i['primary']['port'],i['primary']['sharedSecret'],i['secondary']['ip'],i['secondary']['port'],i['secondary']['sharedSecret']])
					else:
						t.add_row([i['id'],i['name'],i['description'],i['serviceType'],i['primary']['ip'],i['primary']['port'],i['primary']['sharedSecret'],'','',''])
				print(t)
			except:
				exit('could not load zone with id ' + zoneid)

	def create_zone_radius(self,zoneid,radiusip,radiusname,radiussecret):
		# creates radius template for the zone
		command = '/' + api_version + '/rkszones/' + zoneid + '/aaa/radius'

		json_payload = {
    		"name": radiusname,
   			"primary": {
        	"ip": radiusip,
        	"port": 1812,
        	"sharedSecret": radiussecret
    		},
    		"standbyServerEnabled": False
		}

		output = Smartzone.http_method('POST',command,json_payload)

		if 'ok' in dir(output):
			print('radius profile created for zone ' + zoneid)
		else:
			exit('error in API call has occured when creating radius profile: ' + str(output))

	def delete_radius_profile(self,zoneid,radiusid):
		# deleted radius profile
		command = '/' + api_version + '/rkszones/'+ zoneid + '/aaa/' + radiusid
		output = Smartzone.http_method('DELETE',command,'')

		if 'ok' in dir(output):
			print('radius profiles deleted for zone ' + zoneid)
		else:
			exit('error in API call has occured when deleting all radius profiles for zone ' + zoneid + ' : ' + str(output))

	def delete_all_zone_radius(self,zoneid):
		# delete all radius profiles for a zone
		# NOT IMPLEMENTED - SZ API DOCS MISSING SCHEMA
		command = '/' + api_version + '/rkszones/' + zoneid + '/aaa'
		output = Smartzone.http_method('DELETE',command,'')

		if 'ok' in dir(output):
			print('radius profiles deleted for zone ' + zoneid)
		else:
			exit('error in API call has occured when deleting all radius profiles for zone ' + zoneid + ' : ' + str(output))

	def delete_zone(self,zoneid):
		# deletes a zone using its ID 
		zonename = json.loads(self.get_zone(zoneid))['name']
		command = '/' + api_version + '/rkszones/' + zoneid
		output = Smartzone.http_method('DELETE',command,'')

		if 'ok' in dir(output):
			print('zone with name ' + zonename +  ' and ID ' + zoneid + ' deleted successfully')
		else:
			print('failed: ' + str(output))

	def delete_all_zones(self,domainname):
		# removes all zones off the controller in a particular domain name
		zones = self.get_all_zones(domainname)

		for zone in zones['list']:
			self.delete_zone(zone['id'])

	def fetch_domain_name(self,domainid):
		# maps a domain ID to its name 
		command = '/' + api_version + '/domains'
		output = Smartzone.http_method('GET',command,'').json()

		for i in output['list']:
			if i['id'] == domainid:
				domain_name = i['name']
				return domain_name
			else:
				exit('domain name not found')

	def fetch_domain_id(self,domainname):	
		# maps a domain name to its ID
		command = '/' + api_version + '/domains'
		output = Smartzone.http_method('GET',command,'').json()

		domain_id = None

		for i in output['list']:
			if i['name'].casefold() == domainname.casefold():
				domain_id = i['id']

		if domain_id != None:
				return domain_id
		else:
			exit('domain name not found')

	def fetch_zone_id(self,zonename,domainname):
		# map a zone name to a id
		all_zones = self.get_all_zones(domainname)
		
		for i in all_zones['list']:
			if i['name'] == zonename:
				zone_id = i['id']
				return zone_id

	def get_firmwares(self,zonename,domainname):
		# get all AP firmwares in specified zone and domain
		domain_id = self.fetch_domain_id(domainname)
		zone_id = self.fetch_zone_id(zonename,domainname)

		command = '/' + api_version + '/rkszones/' + zone_id + '/apFirmware'

		output = Smartzone.http_method('GET',command,'').json()

		return output

	def get_active_firmware(self,zonename,domainname):
		# get active fireware for a zone
		domain_id = self.fetch_domain_id(domainname)
		zone_id = self.fetch_zone_id(zonename,domainname)

		zone = json.loads(self.get_zone(zone_id))

		return zone['version']

	def change_active_firmeware(self,zonename,domainname,firmware):
		# upgrades/downgrades APs in zone
		domain_id = self.fetch_domain_id(domainname)
		zone_id = self.fetch_zone_id(zonename,domainname)
		
		command = '/' + api_version + '/rkszones/' + zone_id + '/apFirmware'

		payload = {"firmwareVersion": firmware}

		output = Smartzone.http_method('PUT',command,payload)

		if 'ok' in dir(output):
			print('APs beginning to upgrade in ' + zone_id + ' to firmware version ' + firmware)
		else:
			exit('error in API call has occured changing firmware in zone ' + zone_id + ' : ' + str(output))


if __name__ == "__main__":
	z = Zones()
	list_domains,list_zones,create_zone,get_zone,delete_zone, \
	delete_all_zones,get_isolation,get_radius,create_radius,delete_radius,list_zones_default,list_zone_firmwares,get_zone_firmware,change_ap_firmware,modify_zone,json_flag = z.parse_args()

	if list_domains:
		z.load_smartzone()
		domains = z.domains_table(json_flag)
		print(domains)

	if create_zone:
		z.load_smartzone()
		zone_data = z.load_json(create_zone['country'])
		print('new zone created with ID ' + z.create_new_zone(zone_data,create_zone['name'],create_zone['country'],create_zone['domain']))

	if list_zones:
		z.load_smartzone()
		zones = z.zones_table(list_zones,json_flag)

	if list_zones_default:
		z.load_smartzone()
		zones = z.zones_default_table(json_flag)

	if get_zone:
		z.load_smartzone()
		zone_json = z.get_zone(str(get_zone))
		print(zone_json)

	if delete_zone:
		z.load_smartzone()
		z.delete_zone(delete_zone)

	if delete_all_zones:
		z.load_smartzone()
		z.delete_all_zones(delete_all_zones)

	if get_isolation:
		z.load_smartzone()
		z.client_isolation_table(get_isolation,json_flag)

	if get_radius:
		z.load_smartzone()
		z.get_zone_radius(get_radius,json_flag)

	if create_radius:
		z.load_smartzone()
		z.create_zone_radius(create_radius['zoneid'],create_radius['radiusip'],create_radius['radiusname'],create_radius['radiussecret'])

	if delete_radius:
		z.load_smartzone()
		z.delete_radius_profile(delete_radius['zoneid'],delete_radius['radiusid'])

	if list_zone_firmwares:
		z.load_smartzone()
		firmwares = z.get_firmwares(list_zone_firmwares['zonename'],list_zone_firmwares['domainname'])

		for i in firmwares['list']:
			print(i['firmwareVersion'])

	if get_zone_firmware:
		z.load_smartzone()
		print(z.get_active_firmware(get_zone_firmware['zonename'],get_zone_firmware['domainname']))

	if change_ap_firmware:
		z.load_smartzone()
		z.change_active_firmeware(change_ap_firmware['zonename'],change_ap_firmware['domainname'],change_ap_firmware['firmware'])

	if modify_zone:
		z.load_smartzone()
		z.modify_zone(modify_zone['zoneid'],modify_zone['jsonfile'])



