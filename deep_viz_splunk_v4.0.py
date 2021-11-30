import traceback, requests, datetime, time, json, sys, os, simplejson

now = datetime.datetime.utcnow()
compare_time = now - datetime.timedelta(minutes=30)
query_file = "/path/to/your/queries.txt"
splunk_index = "sentinelone"
deepviz_sourcetype = "deepviz"
splunk_deepviz_HEC = "your splunk HEC"
deepvizlog_sourcetype = "deepviz_log"
splunk_deepvizlog_hec = "deepviz_log HEC"
s1_log = "s1_log.json"
sample_file = "deepviz_data.json"
s1_raw = "deepviz_raw.json"
log_file = "deepviz_log.txt"

open_s1_log = open(s1_log, "w")
open_s1_log.close()

open_s1_sample = open(sample_file, "w")
open_s1_sample.close()

head3 = {'Authorization': 'Splunk %s' %splunk_deepviz_HEC,
         'Content-Type' : 'application/json'}
         
head4 = {'Authorization': 'Splunk %s' %splunk_deepvizlog_hec,
         'Content-Type' : 'application/json'}

with open("/path/to/your/S1_token.txt", 'r') as token_file:
	myToken = token_file.read()
	
head2 = {'Authorization': myToken.replace("\n", ""),
		'Content-Type': 'application/json'}

with open(query_file, 'r') as query_file:
	query_list=query_file.readlines()
	
# Initialize Iterator
i = 0
deep_viz_raw = {}

#format the data and send to splunk
def send_to_splunk(output, sourcetype, header, event_count, actual_count):
	print("Sending %s to Splunk..." %sourcetype)
	print("Events being sent to Splunk", actual_count)
	print("Expected number of events ", event_count)
	output_data = json.dumps(output, indent=4)
	output_json = '{"index" : "%s",  "sourcetype": "%s", "event": %s}' %(splunk_index, sourcetype, output_data)
	output_to_splunk = requests.post(url="https://http-inputs-yourcompany.splunkcloud.com:443/services/collector", headers=header, data=output_json)
	print(output_to_splunk.text)
	with open(log_file, 'a') as file:
		file.write("Splunk Response: %s  %s" %(output_to_splunk, output_to_splunk.text) + "\n")
	with open(sample_file, 'a') as file:
		file.write(output_json)
		file.write("\n")

def deep_viz_queries():
	
	deep_viz_data = {}
	results = {}	
	deep_viz_log = []
	query_count = 0
	
	for line in query_list:
		print("Query Line Text:  " , line),
		query_count += 1

		query_formatted = line.rstrip("\n").replace('"', '\\\"')
		#.replace('(', '\\\(').replace(')', '\\\)')
		## QUERY DEEP VIZ ##
		query = """
				{
				"query": "%s",
				"fromDate": "%s",
				"toDate": "%s",
				"queryType":["events"]
				}
				""" % (query_formatted, str(compare_time), str(now))
		
		#print(query)
		
		init_query = requests.post("https://yourTenant.sentinelone.net/web/api/v2.1/dv/init-query", data=query, headers=head2)
		print("INIT QUERY RESPONSE: ", init_query)
		#print("INIT QUERY RESULT:", init_query.text)
		retries = 0

#Check status codes and wait if we hit the rate limit.		
		if init_query.status_code == 200:
			query_id = init_query.json()['data']['queryId']
		elif init_query.status_code in [503, 429]:
			print("Query Error:  ", init_query.text)
			while init_query.status_code in [429, 503]:
				retries += 1
				if retries > 25:
					print("Process exiting.  Too many retries (%s)." %(retries))
					sys.exit()
					continue
				init_query = requests.post("https://yourTenant.sentinelone.net/web/api/v2.1/dv/init-query", data=query, headers=head2)
				print(init_query)
				print("Trying again... %s retries" %(retries))
				if init_query.status_code == 200:
					query_id = init_query.json()['data']['queryId']
				elif init_query.status_code == 503:
					time.sleep(10)
					continue
				elif init_query.status_code == 429:
					time.sleep(10)
					continue
				elif init_query.status_code == 400:
					print("Fix the query...")
					print("Moving on...")
				else:
					print(init_query.status_code)
					continue
		else:
			print("FUCK")
			print(init_query.status_code)
			print(init_query.json())
			break
			
#get the status of the query
		try:
			query_status = requests.get("https://yourTenant.sentinelone.net/web/api/v2.1/dv/query-status?queryId=" + query_id,
										headers=head2).json()
			
			query_response = query_status['data']['responseState']
			
			while query_response not in ['FINISHED', 'TIMED_OUT']:
				time.sleep(10)
				query_status_next = requests.get("https://yourTenant.sentinelone.net/web/api/v2.1/dv/query-status?queryId=" + query_id,
											headers=head2).json()
				query_response = query_status_next['data']['responseState']

#Check for the query to finish and then get results.
			if query_response == 'FINISHED':
				query_results = requests.get("https://yourTenant.sentinelone.net/web/api/v2.1/dv/events?limit=100&queryId=" + query_id,
											 headers=head2).json()
				deep_viz_raw.update(query_results)
					
#Iterate through the results (data, pagination)				
				for key in query_results:
					print("Key :", key)
					i = 0
					for x in query_results['data']:
						i += 1
						print(len(x))
						for key1, value in x.items():
							#print(key)
							if key1 != 'attributes':
								old_results = {key1 : value}
								results.update(old_results)
						deep_viz_data.update({'query': line})
						deep_viz_data.update(results)
						send_to_splunk(deep_viz_data, deepviz_sourcetype, head3, len(query_results['data']), i)
					nextCursor = query_results['pagination']['nextCursor']
				
#Grab and append all the pages of data to the python list.
				while nextCursor:
					query_results_next = requests.get("https://yourTenant.sentinelone.net/web/api/v2.1/dv/events?limit=100&queryId=%s&cursor=%s" % (str(query_id), str(nextCursor)),
													   headers=head2).json()											   
					deep_viz_raw.update(query_results_next)
					for key in query_results:
						print("Key :", key)

# Loop through the dictionaries in the list.						
						for x in query_results['data']:
							i += 1
							#print(len(x))

# Parse through the keys and skip Attributes
							for key1, value in x.items():
								if key1 != 'attributes':
									old_results = {key1 : value}
									results.update(old_results)
							deep_viz_data.update({'query': line})
							deep_viz_data.update(results)
							send_to_splunk(deep_viz_data, deepviz_sourcetype, head3, len(query_results['data']), i)
					nextCursor = query_results_next['pagination']['nextCursor']	

#Send to Splunk
				#send_to_splunk(deep_viz_data, deepviz_sourcetype, head3, len(query_results['data']), i)
				print("Finished query, moving on..." + "\n")
				#if retries > 0:
				#print("Took " + str(retries) + " tries...")
				
			else:
				print("Query timed out...")

#Log stats about the query	to file.	
			ldt = datetime.datetime.utcnow()
			log_time = str(ldt).replace(' ', 'T')[:-3] + 'Z'
			log_msg = {
				"log_source": "deepviz_base",
				"total_results": i,
				"queryId": query_id,
				"status": query_response, 
				"queryNum": query_count, 
				"query_text": str(line),
				"retries": retries, 
				"init_status": init_query.status_code, 
				"ts": log_time,
				"error": "n/a"
					}
			print(log_msg)
			deep_viz_log.append(log_msg)

#Send the log data to Splunk
			send_to_splunk(log_msg, deepvizlog_sourcetype, head4, len(query_results['data']), i)
			#with open(s1_log, "a") as file:
			#	file.write(log_msg)
			#with open(sample_file, "a") as file:
			#	file.write(json.dumps(log_msg, indent=4))
			#	file.write("\n")
			time.sleep(5)

# Log Errors to a log file.			
		except Exception as e:			
			print(traceback.format_exc())
			ldt = datetime.datetime.utcnow()
			log_time = str(ldt).replace(' ', 'T')[:-3] + 'Z'
			log_msg =  {
				"log_source": "deepviz_base",
				"total results": i,
				"queryId": query_id, 
				"status": query_response, 
				"queryNum": query_count, 
				"query_text": line,
				"retries": retries, 
				"init_status": init_query.status_code, 
				"ts": log_time,
				"error": str(traceback.format_exc())
				}
				 
			#deep_viz_log.append(log_msg)
			print("Deep Viz Log :", log_msg)
			send_to_splunk(log_msg, deepvizlog_sourcetype, head4, len(query_results['data']), i)
			with open(s1_log, 'a') as file:
				file.write("S1 Deepviz Errors: %s" %(json.dumps(log_msg, indent=4)))
				file.write("\n")
				
	with open(s1_log, "w") as file:
		file.write(json.dumps(deep_viz_log, indent=4))		
	return deep_viz_data, deep_viz_log

deep_viz_queries()




