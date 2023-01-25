#!/usr/bin/python3

import logging
import os
import os.path
import re
import sys
import traceback
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


def notify_dts_unprocessed_batches(batchname):
    logging.debug("Calling DTS /reprocess_batch for file: " + batchname)
    try:
        response = get(dts_endpoint + '/reprocess_batch?batchname=' + batchname, verify=False)
        logging.debug("Response status code for '/reprocess_batch?batchname='" + filename + ": " + str(response.status_code))
        response.raise_for_status()
    except (exceptions.ConnectionError, HTTPError) as e:
        logging.error("Error when calling DTS /reprocess_batch for batch: " + str(e))




def main():
    # Collect unprocessed batches
    logging.debug("Unprocessed batches")
    unprocessed_batches_list = collect_unprocessed_batches()
    logging.debug("Unprocessed batches returned: " + str(unprocessed_batches_list))
    for batch_path in unprocessed_batches_list:
        destination_path = batch_path
        package_id = os.path.basename(batch_path)
        admin_metadata = {}
        batch_as_array = batch.path.split("/")
        dropbox_name = batch_as_array[-3]
        if re.match("dvn", dropbox_name):
            application_name = "Dataverse"
        else:
            application_name = "ePADD"
        if testing == "False":
            notify_dts_unprocessed_batches(batch_path)


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
