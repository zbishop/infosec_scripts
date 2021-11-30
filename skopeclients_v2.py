import requests, datetime, json

token_file = open("/path/to/ns_token.txt", 'r')
myToken = token_file.read().split("\n")[0]
splunk_HEC = "Enter Splunk HEC Token"
splunk_index = "netskope"
splunk_sourcetype = "skopeclients"
log_file = "/path/to/your/log.txt"
splunk_URL= "https://http-inputs-exampleCompany.splunkcloud.com:443/services/collector"

#print(myToken)
#head = {'Authorization': myToken,
		#'Content-Type': 'application/json'}
		
head2 = {'Authorization': 'Splunk %s' %splunk_HEC,
         'Content-Type' : 'application/json'}
		

#format the data and send to splunk
def send_to_splunk(output):
    output_data = json.dumps(output)
    #print("Data being sent to Splunk:  ", output_data)
    output_json = '{"index" : "%s", "sourcetype": "%s", "event": %s}' %(splunk_index, splunk_sourcetype, output_data)
    output_to_splunk = requests.post(url=splunk_URL, headers=head2, data=output_json)
    print(output_to_splunk.text)
    with open(log_file, 'a') as file:
        file.write("Netskope Splunk Response: %s  %s" %(output_to_splunk, output_to_splunk.text) + "\n")

def client_pull():

	clients = requests.get("https://yourcompany.goskope.com/api/v1/clients?token=%s&type=application&timeperiod=900&limit=5000" % myToken).json()
	#print(clients)

	return clients

def splunk_stuff():
	
	skope_data = client_pull()	
	for x in skope_data['data']:
		send_to_splunk(x)

splunk_stuff()
