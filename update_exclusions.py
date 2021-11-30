import requests
import json

token_file=open("/path/to/your/ss_token.txt", 'r')
token_file_2=open("/path/to/your/S1_token.txt", 'r')
my_ss_token=token_file.read()
my_s1_token=token_file_2.read()

head1 = {'Authorization': my_ss_token,
		 'Content-Type':'application/json'}
head2 = {'Authorization': my_s1_token,
		 'Content-Type':'application/json'}

def exclusions():

	# get sheet data
	response = requests.get("https://api.smartsheet.com/2.0/sheets/1833471862695812", headers=head1)
	get_stuff=response.json()
	get_rows=get_stuff['rows']
	print(response.status_code)
	for x in range(0, len(get_rows)):
			try:
				sheet_id=get_rows[x]['id']
				cell_content=get_rows[x]['cells']
		
				file_name=cell_content[0]['value']
				file_hash=cell_content[4]['value']
				site_name=cell_content[1]['value']
				requester_user=cell_content[2]['value']
				reason=cell_content[3]['value']
				print("FILE NAME= %s") %file_name
				note=()
				note=str("Added from Known Programs SmartSheet.  https://app.smartsheet.com/sheets/CjMXGF2fM7PGcfR5pP8Wm6M5qJXgMrrVp49hPPV1?view=grid    Explanation:  %s" %reason)
				print(note)
			
				
				#print("hash= %s") %file_hash
				print("site= %s") %site_name

		 # Update exclusions in SentinelOne
				sent1_body= {
		"data": {
			"description": note,
			"type":  "hash",
			"targetScope":  "group",
			"note": note
		},
		"filter": {
			"contentHash__contains": file_hash
		}
	}

				sent1_body=json.dumps(sent1_body)
				#print(sent1_body)
				#add_exclusions= requests.post("https://yourTenant.sentinelone.net/web/api/v2.1/threats/add-to-exclusions", headers=head2, data=sent1_body)
				#print("Status code:  %s" %add_exclusions.status_code)
				#print(add_exclusions.json())
				if add_exclusions.status_code == 200:
					print("Exclusion successfully added")
				else:
					print("Fuck.  Something is wrong.")             
		
				
			except Exception as e:
				print(e)
				print("File name was %s" %file_name)
				print("Probably missing Hash.  Proceeding.")

				
token_file.close()
token_file_2.close()
exclusions()
