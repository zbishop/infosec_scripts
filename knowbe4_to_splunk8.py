import requests, json, simplejson, re, os, time as ptime, traceback
from dateutil.parser import *
from datetime import *

knowbe4_token='your_knowbe4_key'
splunk_knowbe4_HEC='your_splunk_HEC_token'

head = {'Authorization': 'Bearer %s' %knowbe4_token,
'Content-Type': 'application/json'}
head3 = {'Authorization': 'Splunk %s' %splunk_knowbe4_HEC,
'Content-Type' : 'application/json'}

splunk_index='knowbe4'

timestamp=str(datetime.now()).replace(" ", "_").replace("-", "").replace(":", "_")

log_file= '/path/to/your/log.txt'
with open(log_file, 'w') as file:
	file.write(str(datetime.now())+ "\n")

#Set the number of days to decide what Splunk will ingest
past_time=datetime.now() - timedelta(days=120)
print("Past date to compare to: ", past_time)

#Pull the data from KnowBe4
def data_pull():
	try:
		for i in range(1000):
			print("Enrollment Page number %s" %i)
			enrollment_request=requests.get(url='https://us.api.knowbe4.com/v1/training/enrollments?per_page=500&page=%s' %i, headers=head)
			print(enrollment_request)
			enrollments = enrollment_request.json()
			if enrollments:
				for enrollment in enrollments:
					enrollment_splunk(enrollment)
					#print(enrollment)
			else: break
		
		#group data pull
		for i in range(15):
			groups_request=requests.get(url='https://us.api.knowbe4.com/v1/groups?per_page=500&page=%s' %i, headers=head)
			print(groups_request)
			groups = groups_request.json()
			if groups:
				for group in groups:
					groups_splunk(group)
			else:
				continue
		
		#knowbe4 user data pull
		for i in range(15):
			users=requests.get(url='https://us.api.knowbe4.com/v1/users?per_page=500&page=%s' %i, headers=head).json()
		#print(users.status_code)
			if users:
				print("User data on page ", i)
				for user in users:
					users_splunk(user)
			#print(user)
			else:
				continue
		
		#if the campaign was ran in the last 120 days, ingest to splunk
		campaigns=requests.get('https://us.api.knowbe4.com/v1/phishing/campaigns', headers=head).json()
		for campaign in campaigns:
			campaign_splunk(campaign)
		
		for campaign in campaigns:
			campaign_id = campaign['campaign_id']
			security_tests_get = requests.get("https://us.api.knowbe4.com/v1/phishing/campaigns/%s/security_tests" % campaign_id, headers=head)
			security_tests = security_tests_get.json()
		
		#parse security tests for start time
		for security_test in security_tests:
			start_time=security_test['started_at']
			start_time_parsed = parse(start_time, ignoretz=True)
		#send security test data to Splunk
			security_test_splunk(security_tests)
			pst_id = security_test['pst_id']
			for i in range(100):
				print("Recipient page number", i)
				recipient_results = requests.get("https://us.api.knowbe4.com/v1/phishing/security_tests/%s/recipients?per_page=500&page=%s" %(pst_id, i), headers=head).json()
				if recipient_results:
		#send recipient data to splunk
					for recipient_test in recipient_results:
						recipient_splunk(recipient_test)
				else: break
		
	except Exception as e:
		print(str(traceback.format_exc()))
		with open(log_file, 'a') as file:
			file.write(str(traceback.format_exc()))

def enrollment_splunk(output):
	knowbe4_enrollment_data=json.dumps(output)
	knowbe4_enrollment_json = '{"index" : "%s", "sourcetype": "knowbe4_training", "event": %s}' %(splunk_index, knowbe4_enrollment_data)
	enrollment_to_splunk = requests.post(url="https://http-inputs-yourTenant.com:443/services/collector", headers=head3, data=knowbe4_enrollment_json)
	with open(log_file, 'a') as file:
		file.write("KnowBe4 Training Enrollment Splunk Response: %s  %s" %(enrollment_to_splunk, enrollment_to_splunk.text) + "\n")

def groups_splunk(output):
	knowbe4_group_data=json.dumps(output)
	knowbe4_group_json = '{"index" : "%s", "sourcetype": "knowbe4_group", "event": %s}' %(splunk_index, knowbe4_group_data)
	groups_to_splunk = requests.post(url="https://http-inputs-yourTenant.com:443/services/collector", headers=head3, data=knowbe4_group_json)
	print(groups_to_splunk.text)
	with open(log_file, 'a') as file:
		file.write("KnowBe4 Group Splunk Response: %s  %s" %(groups_to_splunk, groups_to_splunk.text) + "\n")

def users_splunk(output):
	knowbe4_user_data=json.dumps(output)
	knowbe4_user_json = '{"index" : "%s", "sourcetype": "knowbe4_user", "event": %s}' %(splunk_index, knowbe4_user_data)
	users_to_splunk = requests.post(url="https://http-inputs-yourTenant.com:443/services/collector", headers=head3, data=knowbe4_user_json)
	print(users_to_splunk.text)
	with open(log_file, 'a') as file:
		file.write("KnowBe4 Users Splunk Response: %s  %s" %(users_to_splunk, users_to_splunk.text) + "\n")

#format the recipient data and send to splunk
def recipient_splunk(output):
	knowbe4_recipient_data = json.dumps(output)
	knowbe4_recipient_json = '{"index" : "%s", "sourcetype": "knowbe4_recipient", "event": %s}' %(splunk_index, knowbe4_recipient_data)
	recipients_to_splunk = requests.post(url="https://http-inputs-yourTenant.com:443/services/collector", headers=head3, data=knowbe4_recipient_json)
	print(recipients_to_splunk.text)
	with open(log_file, 'a') as file:
		file.write("KnowBe4 Recipient Splunk Response: %s  %s" %(recipients_to_splunk, recipients_to_splunk.text) + "\n")

#format the security test data and send to splunk
def security_test_splunk(output):
	knowbe4_data = json.dumps(output)
	knowbe4_securitytest_json = '{"index" : "%s", "sourcetype": "knowbe4_securitytest_TEST", "event": %s}' %(splunk_index, knowbe4_data)
	# print(knowbe4_data)
	security_test_to_splunk = requests.post(url="https://http-inputs-yourTenant.com:443/services/collector", headers=head3, data=knowbe4_securitytest_json)
	with open(log_file, 'a') as file:
		file.write("KnowBe4 Security Test Splunk Response: %s  %s" %(security_test_to_splunk, security_test_to_splunk.text) + "\n")
	print(security_test_to_splunk.text)

def campaign_splunk(output):
	knowbe4_campaigns=json.dumps(output)
	knowbe4_campaigns_json = '{"index" : "%s", "sourcetype": "knowbe4_campaign", "event": %s}' %(splunk_index, knowbe4_campaigns)
	#send campaign data to splunk
	campaigns_to_splunk= requests.post(url="https://http-inputs-yourTenant.com:443/services/collector", headers=head3, data=knowbe4_campaigns_json)
	print(campaigns_to_splunk.text)
	with open(log_file, 'a') as file:
		file.write("KnowBe4 Campaign Splunk Response: %s  %s" %(campaigns_to_splunk, campaigns_to_splunk.text) + "\n")

data_pull()
ptime.sleep(5)
