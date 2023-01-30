import pytest, sys, os.path
import monitor_unprocessed_batches


def test_find_unprocessed_batches():
    unprocessed_batch_list = monitor_unprocessed_batches.collect_unprocessed_batches()
    assert unprocessed_batch_list == ['/home/appuser/dropbox/dvndev/incoming/unprocessed', '/home/appuser/dropbox/epadddev_secure/incoming/unprocessed', '/home/appuser/dropbox/epadddev_secure/incoming/unprocessed-missingadminmd', '/home/appuser/dropbox/epadddev_secure/incoming/unprocessed-nodrsconfig']
    
def test_parse_drsconfig_metadata():
    admin_md = monitor_unprocessed_batches.parse_drsconfig_metadata('/home/appuser/dropbox/epadddev_secure/incoming/unprocessed/drsConfig.txt')
    print(admin_md)
    assert admin_md

def test_failed_parse_drsconfig_metadata_nodrsconfig():
    admin_md = monitor_unprocessed_batches.parse_drsconfig_metadata('/home/appuser/dropbox/epadddev_secure/incoming/unprocessed-nodrsconfig/drsConfig.txt')
    print(admin_md)
    assert not admin_md

def test_failed_parse_drsconfig_metadata_missingadminmd():
    admin_md = monitor_unprocessed_batches.parse_drsconfig_metadata('/home/appuser/dropbox/epadddev_secure/incoming/unprocessed-missingadminmd/drsConfig.txt')
    print(admin_md)
    assert not admin_md
