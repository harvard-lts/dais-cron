#!/usr/bin/python3

import logging
import os
import os.path
import sys
import traceback
import time
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
    threshold = int(os.environ.get("UNPROCESSED_CHECK_THRESHOLD", 86400))
    seconds_from_now = time.time() - threshold
    logging.debug("Threshold seconds from now: " + str(seconds_from_now))
    
    for dropbox in dropbox_list:
        dropbox_dir = os.path.join(dropbox_root_dir, dropbox, "incoming")
        logging.debug("Checking for unprocessed batches in dropbox loc: " + dropbox_dir)
        if (os.path.isdir(dropbox_dir)):
            for name in os.listdir(dropbox_dir):
                if not "-batch" in name:
                    batch_path = os.path.join(dropbox_dir,name)
                    logging.debug("Inspecting: " + batch_path)
                    create_time = os.stat(batch_path).st_ctime
                    logging.debug("Create time in seconds: " + str(create_time))
                    #If the create time was more than the given threshold then reprocess it.
                    if (threshold == -1 or seconds_from_now >= create_time):
                        unprocessed_batches.append(batch_path)

    return unprocessed_batches


def notify_dts_unprocessed_batches(unprocessed_batches_list):
    logging.debug("Calling DTS /reprocess_batches")
    try:
        payload = {"unprocessed_exports": unprocessed_batches_list}
        response = get(dts_endpoint + '/reprocess_batches', params=payload, verify=False)
        logging.debug("Response status code for '/reprocess_batches: " + str(response.status_code))
        response.raise_for_status()
    except (exceptions.ConnectionError, HTTPError) as e:
        logging.error("Error when calling DTS /reprocess_batch" + str(e))




def main():
    # Collect unprocessed batches
    logging.debug("Unprocessed batches")
    unprocessed_batches_list = collect_unprocessed_batches()
    logging.debug("Unprocessed batches returned: " + str(unprocessed_batches_list))

    if testing == "False":
        notify_dts_unprocessed_batches(unprocessed_batches_list)


        
if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
