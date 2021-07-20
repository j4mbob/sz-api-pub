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

class Groups():

	global api_version
	api_version = Smartzone.return_api_version()

	def parse_args(self):
		parser = argparse.ArgumentParser(description="Smartzone platform",conflict_handler='resolve')
		parser.add_argument("-create-ap-group", action="store", dest="create_ap_group", nargs=4, metavar=('<GROUP NAME>','<ZONE NAME>','<DOMAIN NAME>', '<GROUP DESCRIPTION>'), help="Create AP group with name <group name> in <zone name> <domain name> with description <group descrption>")
		parser.add_argument("-move-aps", action="store", dest="move_aps", nargs=6, metavar=('<AP GROUP>','<ZONE NAME>','<DOMAIN NAME>','<NEW AP GROUP>','<NEW ZONE NAME>','<NEW DOMAIN NAME>'), help="Move APs from <ap group> <zone name> <domain nname> to <new ap group> <new zone name> <new domain name>")
		parser.add_argument("-get-ap-groups", action="store", dest="get_ap_groups", nargs=2, metavar=('<ZONE NAME>','<DOMAIN NAME>'), help="Get AP groups in <zone name> <domain name> for root TLD use 'System'")
		parser.add_argument("-get-group-aps", action="store", dest="get_group_aps", nargs=3, metavar=('<AP GROUP>','<ZONE NAME>','<DOMAIN NAME>'), help="Get APs in group <ap group> in <zone name> <domain name>")
		parser.add_argument("-delete-empty-groups", action="store", dest="delete_empty_groups", nargs=2, metavar=('<ZONE NAME>','<DOMAIN NAME>'), help="delete all empty AP groups in <zone name> <dmain name>")

		parseargs = vars(parser.parse_args(None if sys.argv[1:] else ['-h']))

		create_ap_group = parseargs['create_ap_group']
		move_aps = parseargs['move_aps']
		get_ap_groups = parseargs['get_ap_groups']
		get_group_aps = parseargs['get_group_aps']
		delete_empty_groups = parseargs['delete_empty_groups']

		if parseargs['delete_empty_groups']:
			items = ['zonename','domainname']
			delete_empty_groups = dict(zip(items,parseargs['delete_empty_groups']))

		if parseargs['create_ap_group']:
			items = ['groupname','zonename','domainname','groupdesc']
			create_ap_group = dict(zip(items,parseargs['create_ap_group']))

		if parseargs['move_aps']:
			items = ['apgroup','zonename','domainname','newapgroup','newzonename','newdomainname']
			move_aps = dict(zip(items,parseargs['move_aps']))

		if parseargs['get_ap_groups']:
			items = ['zonename','domainname']
			get_ap_groups = dict(zip(items,parseargs['get_ap_groups']))

		if parseargs['get_group_aps']:
			items = ['apgroup','zonename','domainname']
			get_group_aps = dict(zip(items,parseargs['get_group_aps']))

		return delete_empty_groups,create_ap_group,move_aps,get_ap_groups,get_group_aps

	def load_smartzone(self):
		# initiates connection object for SZ controller API
		s = Smartzone()

		return s

	def get_ap_groups(self,zonename,domainname):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)
		
		command = '/' + api_version + '/rkszones/' + zone_id + '/apgroups'

		try:
			output = Smartzone.http_method('GET',command,'').json()
			return json.dumps(output,indent=4)
		except:
			exit('could not load zone with id ' + zoneid)


	def create_ap_group(self,groupname,zonename,domainname,groupdesc):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)

		with open('template_schemas/ap_group.json') as template:
			payload = json.load(template)

		payload['name'] = groupname
		payload['description'] = groupdesc
	
		command = '/' + api_version + '/rkszones/' + zone_id + '/apgroups'

		output = Smartzone.http_method('POST',command,payload)

		if 'ok' in dir(output):
			return output.json()
		else:
			exit('could not create AP group: ' + str(output))

	def clone_group_to_zone(self):
		z = Zones()

	def delete_group(self,apgroup,zonename,domainname):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)

		apgroup_id = self.fetch_ap_group_id(apgroup,zonename,domainname)
		
		command = '/' + api_version + '/rkszones/' + zone_id + '/apgroups/' + apgroup_id

		output = Smartzone.http_method('DELETE',command,'')

		if 'ok' in dir(output):
			print('deleted AP group ' + apgroup +  ' in zone ' + zonename + ' domain ' + domainname)
		else:
			print('failed: ' + str(output))

	def delete_empty_groups(self,zonename,domainname):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)

		for group in json.loads(self.get_ap_groups(zonename,domainname))['list']:
			gdata = self.get_ap_group_info(group['id'],zonename,domainname)
			
			if len(gdata['members']) == 0:
				print('Removing empty group: ' + gdata['name'])
				self.delete_group(gdata['name'],zonename,domainname)
			else:
				print(gdata['name'] + ' has ' + str(len(gdata['members'])) + ' AP members, leaving')					
			
	def get_ap_group_info(self,apgroupid,zonename,domainname):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)
		
		command = '/' + api_version + '/rkszones/' + zone_id + '/apgroups/' + apgroupid

		output = Smartzone.http_method('GET',command,'')

		if 'ok' in dir(output):
			return output.json()
		else:
			exit('could not retrieve AP group: ' + str(output))
	
	def fetch_ap_group_id(self,apgroup,zonename,domainname):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)

		ap_groups = json.loads(self.get_ap_groups(zonename,domainname))

		apgroup_id =  None

		for i in ap_groups['list']:
			if apgroup == i['name']:
				apgroup_id  = i['id']
		if apgroup_id != None:
			return apgroup_id
		else:
			exit('could not find ap group ' + apgroup)

	def get_group_aps(self,apgroup,zonename,domainname):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)

		apgroup_id = self.fetch_ap_group_id(apgroup,zonename,domainname)

		command = '/' + api_version + '/query/ap'

		payload = { "filters":[{
				      "type": "ZONE",
				      "value": zone_id,
				      "operator": "eq"
				    }],
				    "extraFilters": [
				    {
				      "type": "APGROUP",
				      "value": apgroup_id,
				      "operator": "eq"
				    }
				    ],
				    "limit": 5000,
				}

		output = Smartzone.http_method('POST',command,payload).json()

		return json.dumps(output,indent=4)


	def move_all_aps(self,zonename,domainname,apgroup_id,newapgroup,newzonename,newdomainname,ap_macs):
		z = Zones()
		zone_id = z.fetch_zone_id(zonename,domainname)
		domain_id = z.fetch_domain_id(domainname)
		new_zone_id = z.fetch_zone_id(newzonename,newdomainname)
		new_domain_id = z.fetch_domain_id(newdomainname)

		new_apgroup_id = self.fetch_ap_group_id(newapgroup,newzonename,newdomainname)

		#command = '/v9_0/rkszones/' + new_zone_id + '/apgroups/' + new_apgroup_id + '/members'

		schema = {"zoneId": new_zone_id,
				"apGroupId": new_apgroup_id
		}

		#schema = { "memberList": []}

		for ap in ap_macs:
			#schema["memberList"].append({"apMac":ap})
			command = '/' + api_version + '/aps/' + ap
			output = Smartzone.http_method('PATCH',command,schema)
			
			if 'ok' in dir(output):
				print('AP ' + ap + ' moved to ' + newapgroup)
			else:
				print('AP ' + ap + ' move failed: ' + output)
			
  

if __name__ == "__main__":
	g = Groups()
	delete_empty_groups,create_ap_group,move_aps,get_ap_groups,get_group_aps = g.parse_args()

	if create_ap_group:
		g.load_smartzone()
		print(g.create_ap_group(create_ap_group['groupname'],create_ap_group['zonename'],create_ap_group['domainname'],create_ap_group['groupdesc']))

	if move_aps:
		g.load_smartzone()
		aps = json.loads(g.get_group_aps(move_aps['apgroup'],move_aps['zonename'],move_aps['domainname']))
		apgroup_id = g.fetch_ap_group_id(move_aps['apgroup'],move_aps['zonename'],move_aps['domainname'])

		ap_macs = []
		
		for i in aps['list']:
			ap_macs.append(i['apMac'])

		g.move_all_aps(move_aps['zonename'],move_aps['domainname'],apgroup_id,move_aps['newapgroup'],move_aps['newzonename'],move_aps['newdomainname'],ap_macs)


	if get_ap_groups:
		g.load_smartzone()
		print(g.get_ap_groups(get_ap_groups['zonename'],get_ap_groups['domainname']))


	if get_group_aps:
		g.load_smartzone()
		print(g.get_group_aps(get_group_aps['apgroup'],get_group_aps['zonename'],get_group_aps['domainname']))

	if delete_empty_groups:
		g.load_smartzone()
		g.delete_empty_groups(delete_empty_groups['zonename'],delete_empty_groups['domainname'])







