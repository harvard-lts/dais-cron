import pytest, sys, os.path
import monitor_dropbox


def test_find_loadreport():
    loadreports_list = monitor_dropbox.collect_loadreports()
    assert loadreports_list == ['LOADREPORT_test.txt', 'LOADREPORT_test2.txt', 'LOADREPORT_test3.txt', 'LOADREPORT_test.txt', 'LOADREPORT_test2.txt', 'LOADREPORT_test3.txt']


def test_find_failed_batch():
    failed_batch_list = monitor_dropbox.collect_failed_batch()
    assert failed_batch_list == ['test-batch',
                                 'test2-batch']