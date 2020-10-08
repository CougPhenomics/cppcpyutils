# -*- coding: utf-8 -*-
import os
import glob
import re as re
from datetime import timedelta
import pandas as pd


def import_snapshots(snapshotdir, camera='psII', ext='png', delimiter='-'):
    """Import snapshots from PSII imaging

    Parameter
    ---------
    snapshotdir : str
        path to image directory
    camera : str
        camera label for backwards compatibility (no longer used)
    ext : str
        extension of image files
    delimiter : str
        either single character delimiter or a regex string

    Returns
    -------
        pandas dataframe with snapshot metadata

    Notes
    -----
    Export .png into data/<camera> folder from LemnaBase using the commandline `LT-db-extractor`. file format example: C6-GoldStandard_PSII-20190312T000911-PSII0-15.png

    """

    fns = find_images(snapshotdir, ext)
    return get_imagemetadata(fns, delimiter)


def find_images(snapshotdir, ext):
    """Find png images is specified directory

    Parameters
    ----------
    snapshotdir : str
        directory of image files
    ext : str
        extension of image files

    Returns
    -------
    filenames of image files : list

    Raises
    ------
    ValueError
        if the given directory doesn't exist
    RuntimeError
        if no files with extension png were found

    """

    if not os.path.exists(snapshotdir):
        raise ValueError('the path %s does not exist' % snapshotdir)

    fns = [fn for fn in glob.glob(pathname=os.path.join(snapshotdir, '*%s' % ext))]

    if len(fns) == 0:
        raise RuntimeError('No files with extension %s were found in the directory specified.' % ext)

    return(fns)


def get_imagemetadata(fns, delimiter):
    """Get image filenames and metadata from filenames
    Parameters
    ----------
        fns : list
            filenames of image files
        delimiter : str
            single character or regex to split filename


    Returns
    -------
        snapshotdf : pandas dataframe
            dataframe of snapshot metadata

    Raises
    ------
    ValueError
        if the filenames do not have 6 pieces delimited by a `-`

    """
    # Compile regex (even if it's only a delimiter character)
    regex = re.compile(delimiter)

    flist = list()
    for fullfn in fns:
        fn = os.path.basename(fullfn)
        fn = os.path.splitext(fn)
        f = parse_filename(fn[0], delimiter, regex) #if delimiter is a single character it will split filenam with delimiter otherwise uses regex
        f.append(fullfn)
        flist.append(f)

    try:
        fdf = pd.DataFrame(flist,
                        columns=[
                            'plantbarcode', 'experiment', 'timestamp',
                            'cameralabel', 'frameid', 'filename'
                        ])
    except ValueError as e:
        raise ValueError('The filenames did have correctly formated metadata as specified by delimiter argument.') from e

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


# Filename metadata parser, from plantcv 3.10
###########################################
def parse_filename(filename, delimiter, regex):
    """Parse the input filename and return a list of metadata.

    Parameters
    ----------
        filename : str
            Filename to parse metadata from
        delimiter :  str
            Delimiter character to split the filename on
        regex : re.Pattern
            Compiled regular expression pattern to process file with

    Returns
    -------
        metadata : list
    """

    # Split the filename on delimiter if it is a single character
    if len(delimiter) == 1:
        metadata = filename.split(delimiter)
    else:
        metadata = re.search(regex, filename)
        if metadata is not None:
            metadata = list(metadata.groups())
        else:
            metadata = []
    return metadata
###########################################
