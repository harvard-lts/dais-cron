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
logname_template = os.path.dirname(os.path.realpath(__file__)) + "/logs/monitor_dropbox_{}.log"
logging.basicConfig(filename=logname_template.format(datetime.today().strftime("%Y%m%d")),
                    format='%(asctime)-2s --%(filename)s-- %(levelname)-8s %(message)s', datefmt=DATEFORMAT,
                    level=logging.DEBUG)

dts_endpoint = os.environ.get('DTS_ENDPOINT')
dropbox_root_dir = os.environ.get('BASE_DROPBOX_PATH')
dropbox_dirs = os.environ.get('DROPBOX_DIRS')
dropbox_list = dropbox_dirs.replace(" ", "").split(",")
testing = os.environ.get("TESTING", "False")

logging.debug("Executing monitor_dropbox.py")


def collect_loadreports():
    loadreports = {}
    for dropbox in dropbox_list:
        loadreport_files = []
        loadreport_dir = os.path.join(dropbox_root_dir, dropbox, "incoming")
        logging.debug("Checking for load reports in dropbox loc: " + loadreport_dir)

        for root, dirs, files in os.walk(loadreport_dir):
            for name in files:
                if re.match("LOADREPORT", name):
                    loadreport_files.append(name)
        if loadreport_files:
            loadreports[dropbox] = loadreport_files
    return loadreports


def notify_dts_loadreports(filename, dropbox):
    logging.debug("Calling DTS /loadreport for file: " + filename)
    try:
        url = dts_endpoint + "/loadreport?filename={}&dropbox={}".format(filename, dropbox)
        response = get(url, verify=False)
        logging.debug("Response status code for '/loadreport?filename='" + filename + ": " + str(response.status_code))
        response.raise_for_status()
    except (exceptions.ConnectionError, HTTPError) as e:
        logging.error("Error when calling DTS /loadreport for file: " + str(e))


def collect_failed_batch():
    failed_batches = {}
    for dropbox in dropbox_list:
        failed_batch_list = []
        failed_batch_dir = os.path.join(dropbox_root_dir, dropbox, "incoming")
        logging.debug("Checking failed batches in loc: " + failed_batch_dir)

        for root, dirs, files in os.walk(failed_batch_dir):
            for name in files:
                if re.match("batch.xml.failed", name):
                    split_path = root.split("/")
                    failed_batch_list.append(split_path.pop())
        if failed_batch_list:
            failed_batches[dropbox] = failed_batch_list

    return failed_batches


def notify_dts_failed_batch(batch_name, dropbox):
    logging.debug("Calling DTS for failed batch: " + batch_name)
    try:
        url = dts_endpoint + "/failedBatch?batchName={}&dropbox={}".format(batch_name, dropbox)
        response = get(url, verify=False)
        logging.debug("Response status code for '/failedBatch?batchName='" + batch_name + ": " + str(response.status_code))
        response.raise_for_status()
    except (exceptions.ConnectionError, HTTPError) as e:
        logging.error("Error when calling DTS /loadreport for file: " + str(e))


def main():
    # Collect successful ingests
    loadreports = collect_loadreports()
    logging.debug("Load report files returned: " + str(loadreports))
    for dropbox in loadreports:
        load_report_list = loadreports[dropbox]
        for loadreport in load_report_list:
            if testing == "False":
                notify_dts_loadreports(loadreport, dropbox)

    # Collect failed ingests
    failed_batches = collect_failed_batch()
    logging.debug("Failed batch files returned: " + str(failed_batches))
    for dropbox in failed_batches:
        failed_batch_list = failed_batches[dropbox]
        for failed_batch in failed_batch_list:
            if testing == "False":
                notify_dts_failed_batch(failed_batch, dropbox)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
