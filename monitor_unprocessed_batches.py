#!/usr/bin/python3

import logging
import os
import os.path
import re
import sys
import traceback, time, json
from datetime import datetime

from requests import exceptions, get, HTTPError

DATEFORMAT = '%Y-%m-%d %H:%M:%S'
relative_dir = os.path.dirname(os.path.realpath(__file__))
logname_template = os.path.dirname(os.path.realpath(__file__)) + "/logs/monitor_unprocessed_batches{}.log"
logging.basicConfig(filename=logname_template.format(datetime.today().strftime("%Y%m%d")),
                    format='%(asctime)-2s --%(filename)s-- %(levelname)-8s %(message)s', datefmt=DATEFORMAT,
                    level=logging.DEBUG)

dts_endpoint = os.environ.get('DTS_ENDPOINT')
dropbox_root_dir = os.environ.get('BASE_DROPBOX_PATH')
dropbox_dirs = os.environ.get('DROPBOX_DIRS')
dropbox_list = dropbox_dirs.replace(" ", "").split(",")
testing = os.environ.get("TESTING", "False")

logging.debug("Executing monitor_unprocessed_batches.py")


def collect_unprocessed_batches():
    unprocessed_batches = []
    for dropbox in dropbox_list:
        dropbox_dir = os.path.join(dropbox_root_dir, dropbox, "incoming")
        logging.debug("Checking for unprocessed batches in dropbox loc: " + dropbox_dir)
        if (os.path.isdir(dropbox_dir)):
            for name in os.listdir(dropbox_dir):
                if not "-batch" in name:
                    unprocessed_batches.append(os.path.join(dropbox_dir,name))

    return unprocessed_batches


def notify_dts_unprocessed_batches(unprocessed_data_path, application_name, admin_metadata):
    logging.debug("Calling DTS /reprocess_batch for file: " + unprocessed_data_path)
    try:
        admin_metadata_json = json.dumps(admin_metadata)
        payload = {"unprocessed_data_path": unprocessed_data_path, "application_name": application_name, "admin_metadata": admin_metadata_json}
        response = get(dts_endpoint + '/reprocess_batch', data=payload, verify=False)
        logging.debug("Response status code for '/reprocess_batch: " + str(response.status_code))
        response.raise_for_status()
    except (exceptions.ConnectionError, HTTPError) as e:
        logging.error("Error when calling DTS /reprocess_batch for batch: " + str(e))




def main():
    # Collect unprocessed batches
    logging.debug("Unprocessed batches")
    unprocessed_batches_list = collect_unprocessed_batches()
    logging.debug("Unprocessed batches returned: " + str(unprocessed_batches_list))
    
    threshold = int(os.environ.get("UNPROCESSED_CHECK_THRESHOLD", 86400))
    seconds_from_now = time.time() - threshold
    logging.debug("Threshold seconds from now: " + str(seconds_from_now))
    
    for batch_path in unprocessed_batches_list:
        logging.debug("Inspecting: " + batch_path)
        create_time = os.stat(batch_path).st_ctime
        logging.debug("Create time in seconds: " + str(create_time))
        
        #If the create time was more than the given threshold then reprocess it.
        if (seconds_from_now >= create_time):
            logging.debug("Reprocessing: " + batch_path)
            destination_path = batch_path
            package_id = os.path.basename(batch_path)
            admin_metadata = {}
            batch_as_array = batch_path.split("/")
            dropbox_name = batch_as_array[-3]
            if re.match("dvn", dropbox_name):
                application_name = "Dataverse"
                admin_metadata = {"dropbox_name": dropbox_name}
            else:
                application_name = "ePADD"
                drs_config_path = os.path.join(batch_path, "drsConfig.txt")
                admin_metadata = parse_drsconfig_metadata(drs_config_path)
                #If errors were caught while trying to parse the drsConfig file
                #then move to the next unprocessed batch
                if not admin_metadata:
                    continue
                admin_metadata["dropbox_name"] = dropbox_name
                
            if testing == "False":
                notify_dts_unprocessed_batches(batch_path, application_name, admin_metadata)

def parse_drsconfig_metadata(drs_config_path):
    admin_metadata = {}
    try:
        #This will throw an error if the file is missing which is handled in the try-except
        with open(drs_config_path, 'r', encoding='UTF-8') as file:
            metadata = file.read().splitlines()
            metadata_dict = {}
            for val in metadata:
                if len(val) > 0:
                    split_val = val.split('=')
                    metadata_dict[split_val[0]] = split_val[1]
            
            try:
                #This will throw an error if any key is missing and is handled in the try-except
                admin_metadata = {        
                    "accessFlag": metadata_dict["accessFlag"],
                    "contentModel": metadata_dict["contentModel"],
                    "depositingSystem": metadata_dict["depositingSystem"],
                    "firstGenerationInDrs": metadata_dict["firstGenerationInDrs"],
                    "objectRole": metadata_dict["objectRole"],
                    "usageClass": metadata_dict["usageClass"],
                    "storageClass": metadata_dict["storageClass"],
                    "ownerCode": metadata_dict["ownerCode"],
                    "billingCode": metadata_dict["billingCode"],
                    "resourceNamePattern": metadata_dict["resourceNamePattern"],
                    "urnAuthorityPath": metadata_dict["urnAuthorityPath"],
                    "depositAgent": metadata_dict["depositAgent"],
                    "depositAgentEmail": metadata_dict["depositAgentEmail"],
                    "successEmail": metadata_dict["successEmail"],
                    "failureEmail": metadata_dict["failureEmail"],
                    "successMethod": metadata_dict["successMethod"],
                    "adminCategory": metadata_dict["adminCategory"]
                }
            except KeyError as err:
                logging.error("Missing a key in " + drs_config_path +" file: " + str(err))

    except FileNotFoundError as err:
        logging.error("drsConfig.txt does not exist for path: "+ drs_config_path)
    
    return admin_metadata
        
if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
