import pytest
from cppcpyutils.io import find_images
from cppcpyutils.io import get_imagemetadata
from pandas.testing import assert_frame_equal
from pandas import DataFrame
from pandas import Timestamp


def test_find_images_nodirectoryexists():
    TEST_DIR = '-'
    with pytest.raises(ValueError):
        find_images(TEST_DIR)


def test_find_images_noimages():
    TEST_DIR = '.'
    with pytest.raises(RuntimeError):
        find_images(TEST_DIR)


def test_get_imagemetadata_badfilenames():
    TEST_FNS = ['image.png']
    with pytest.raises(ValueError):
        get_imagemetadata(TEST_FNS)


def test_get_imagemetadata():
    TEST_FNS = [
        'C6-GoldStandard_PSII-20190312T000911-PSII0-14.png',
        'C6-GoldStandard_PSII-20190312T000911-PSII0-15.png'
    ]
    TEST_DF = DataFrame({
        'plantbarcode': {
            0: 'C6',
            1: 'C6'
        },
        'experiment': {
            0: 'GoldStandard_PSII',
            1: 'GoldStandard_PSII'
        },
        'cameralabel': {
            0: 'PSII0',
            1: 'PSII0'
        },
        'frameid': {
            1: 14,
            0: 15
        },
        'filename': {
            1: 'C6-GoldStandard_PSII-20190312T000911-PSII0-14.png',
            0: 'C6-GoldStandard_PSII-20190312T000911-PSII0-15.png'
        },
        'datetime': {
            0: Timestamp('2019-03-12 00:09:11'),
            1: Timestamp('2019-03-12 00:09:11')
        },
        'jobdate': {
            0: Timestamp('2019-03-12 00:00:00'),
            1: Timestamp('2019-03-12 00:00:00')
        }
    })
    TEST_DF['frameid'] = TEST_DF.frameid.astype('uint8')
    TEST_DF = TEST_DF.sort_values(['plantbarcode', 'datetime', 'frameid'])
    TEST_DF = TEST_DF.set_index(['plantbarcode', 'experiment', 'datetime', 'jobdate'])

    snapshotdf = get_imagemetadata(TEST_FNS)
    assert_frame_equal(snapshotdf, TEST_DF)
