# -*- coding: utf-8 -*-
import os
import glob
import re as re
from datetime import timedelta
import pandas as pd


def import_snapshots(snapshotdir, camera='psII'):
    '''
    Import snapshots from PSII imaging.

    Input:
        snapshotdir: path to image directory
        camera: camera label for backwards compatibility (no longer used)
    Returns:
        snapshotdf: pandas dataframe with snapshot metadata
    Details:
        Export .png into data/<camera> folder from LemnaBase using data-science-tools/LT-db-extractor.py
    for example: C6-GoldStandard_PSII-20190312T000911-PSII0-15.png
    '''

    fns = find_images(snapshotdir)
    return get_imagemetadata(fns)


def find_images(snapshotdir):
    '''
    Input:
        snapshotdir = directory of .png files
    Returns:
        fns = filenames of image files
    '''

    # %% Get metadata from .tifs
    # snapshotdir = 'data/raw_snapshots/psII'

    if not os.path.exists(snapshotdir):
        raise ValueError('the path %s does not exist' % snapshotdir)

    fns = [fn for fn in glob.glob(pathname=os.path.join(snapshotdir, '*.png'))]

    if len(fns) == 0:
        raise RuntimeError('No files with extension .png were found in the directory specified.')

    return(fns)


def get_imagemetadata(fns):
    '''
    Get image filenames and metadata from filenames
    Input:
        fns: filenames of image files
    Returns:
        snapshotdf: pandas dataframe with snapshot metadata
    '''

    flist = list()
    for fn in fns:
        f = re.split('[-]', os.path.splitext(os.path.basename(fn))[0])
        f.append(fn)
        flist.append(f)

    try:
        fdf = pd.DataFrame(flist,
                        columns=[
                            'plantbarcode', 'experiment', 'timestamp',
                            'cameralabel', 'frameid', 'filename'
                        ])
    except ValueError as e:
        raise ValueError('The filenames did have correctly formated metadata separated by "-".') from e

    # convert date and time columns to datetime format
    fdf['datetime'] = pd.to_datetime(fdf['timestamp'])
    fdf['jobdate'] = fdf.datetime.dt.floor('d')

    #create a jobdate to match dark and light measurements. dark experiments after 8PM correspond to the next day's light experiments
    fdf.loc[fdf.datetime.dt.hour >= 20,
            'jobdate'] = fdf.loc[fdf.datetime.dt.hour >= 20,
                                    'jobdate'] + timedelta(days=1)

    # convert image id from string to integer that can be sorted numerically
    fdf['frameid'] = fdf.frameid.astype('uint8')
    fdf = fdf.sort_values(['plantbarcode', 'datetime', 'frameid'])

    fdf = fdf.set_index(['plantbarcode', 'experiment', 'datetime',
                         'jobdate']).drop(columns=['timestamp'])

    return fdf
