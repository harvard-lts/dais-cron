import pytest, sys, os.path
import monitor_dropbox


def test_find_loadreport():
    loadreports_list = monitor_dropbox.collect_loadreports()
    assert loadreports_list == ['LOADREPORT_test.txt', 'LOADREPORT_test2.txt', 'LOADREPORT_test3.txt']


def test_find_failed_batch():
    failed_batch_list = monitor_dropbox.collect_loadreports()
    assert failed_batch_list == ['/home/appuser/dropbox/dvndev/incoming/batch1/batch.xml.failed',
                                 '/home/appuser/dropbox/dvndev/incoming/batch2/batch.xml.failed']
