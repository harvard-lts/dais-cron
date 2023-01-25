import pytest, sys, os.path
import monitor_unprocessed_batches


def test_find_unprocessed_batches():
    unprocessed_batch_list = monitor_unprocessed_batches.collect_unprocessed_batches()
    assert unprocessed_batch_list == ['/home/appuser/dropbox/dvndev/incoming/unprocessed']
