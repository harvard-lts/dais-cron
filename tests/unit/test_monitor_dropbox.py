import pytest, sys, os.path
import monitor_dropbox


def test_find_loadreport():
    loadreports_list = monitor_dropbox.collect_loadreports()
    assert "dvndev" in loadreports_list
    assert "epadddev_secure" in loadreports_list
    assert 'LOADREPORT_test.txt' in loadreports_list["dvndev"]
    assert 'LOADREPORT_test2.txt' in loadreports_list["dvndev"]
    assert 'LOADREPORT_test3.txt' in loadreports_list["dvndev"]
    assert 'LOADREPORT_test.txt' in loadreports_list["epadddev_secure"]
    assert 'LOADREPORT_test2.txt' in loadreports_list["epadddev_secure"]
    assert 'LOADREPORT_test3.txt' in loadreports_list["epadddev_secure"]
    

def test_find_failed_batch():
    failed_batch_list = monitor_dropbox.collect_failed_batch()
    assert failed_batch_list == {"dvndev": ['test-batch', 'test2-batch']}