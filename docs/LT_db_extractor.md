# Data Extraction Tool

Allow a user to connect to a LemnaTec database and download snapshots without the requirement to use LemnaTec software.

## Instructions

### 1. Create a database.config file and adjust parameters in the JSON file to suit your set-up.

A couple things to keep in mind.

- username, password, hostname refer to the server ssh login. If you are running the script on the server, hostname = "localhost"
- dbhostname, dbname, dbusername, dbpassword are specifically for the database. If you are running the script on the server, dbhostname = ""
- path is the path to the blob files
- the parameter `"Colour"` describes the colour conversion process that is required. This has an `int code`, which can be obtained from the [OpenCV Colour Space Conversions list](https://docs.opencv.org/4.0.0/d8/d01/group__imgproc__color__conversions.html). For instance, the code for `COLOR_BAYER_RG2BGR` is `48`.
- height, width parameters are in pixels

```json
{
  "username" : "user",
  "password" : "password",
  "hostname" : "hostname",
  "dbhostname" : "dbhostname",
  "dbname" : "dbname",
  "dbusername" : "dbuser",
  "dbpassword" : "dbpwd",
  "path" : "/path/on/lemnatec/server",
  "colour" : 48,
  "vis_height" : 2056,
  "vis_width" : 2454,
  "nir_height" : 508,
  "nir_width" : 636,
  "psII_height" : 1038,
  "psII_width" : 1388
}
```

### 2. Open the terminal and run `LT-db-extractor.py` with `-h` to see available command line arguments.

```sh
(plantcv) C:\Users\dominikschneider\Documents\phenomics>python LT-db-extractor.py -h
usage: LT-db-extractor.py [-h] -c CONFIG -e EXPER [-l CAMERA]
                          [-i FRAMEID [FRAMEID ...]] -o OUTDIR [-a DATE1]
                          [-z DATE2] [-d]

Retrieve data from a LemnaTec database.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        JSON config file. (default: None)
  -e EXPER, --exper EXPER
                        Experiment number/name (measurement label) (default:
                        None)
  -l CAMERA, --camera CAMERA
                        Camera label. VIS or PSII or NIR (default: None)
  -i FRAMEID [FRAMEID ...], --frameid FRAMEID [FRAMEID ...]
                        image frame # to download. Argument accepts multiple
                        frames delimited by space. Image frames start at 1.
                        (default: None)
  -o OUTDIR, --outdir OUTDIR
                        Output directory for results. (default: None)
  -a DATE1, --date1 DATE1
                        Date for start of data series (YYYY-mm-dd). (default:
                        None)
  -z DATE2, --date2 DATE2
                        Date for end of data series (YYYY-mm-dd) (exclusive).
                        (default: None)
  -d, --append          add new files to existing directory (default: False)
```

`-c`, `-o`, and `-e` are required.

Metadata of each image downloaded will be saved to a CSV.

### 3. Utilise [PlantCV](https://github.com/danforthcenter/plantcv) to analyse your images!

## Example

Make sure you have LT-db-extractor.py in your PATH, e.g. install `cppcpyutils` to a conda environment

```sh
ipython LT-db-extractor.py -- \
--config ../cppcserver-local.config \
--outdir data/vis \
--camera vis \
--exper doi \
--append
```

The script will connect to the database server to query image and experimental metadata. It identifies the corresponding entries for each LemanTec snapshot and downloads the data file (blob) to the local machine via SFTP. The blob is converted to a png based on the config specified or in the case of a Walz PSII camera the final frame is saved as a .pim.

## Caveats

I decided on a filename format that works well with the PlantCV metadata parser.

`A1-doi-20200531T120429-VIS0-0.png`

The filename parts are delimited with '-' and include `id_tag`, `measurement_label`, `timestamp` in ISO format, `camera_label`, `frame`.

- `id_tag` = barcode of the tray
- `measurement_label` = experiment name
- `time_stamp` is the timestamp of the snapshot
- `camera_label` identifies the camera
- `frame` identifies the frame number of the snapshot

Some sleuthing was required to get this all to work well. If you open pgAdmin and connect to your database, you can run the following query to see the entries:

```sql
SELECT * FROM snapshot
INNER JOIN tiled_image ON snapshot.id = tiled_image.snapshot_id
INNER JOIN tile ON tiled_image.id = tile.tiled_image_id
INNER JOIN image_file_table ON image_file_table.id = tile.raw_image_oid
WHERE measurement_label = 'doi' --experiment name
```

Based on the resulting table I identified:

- a rotation flag `rotate_flip_type` and use the value stored in the database to rotate images correctly. It is not confirmed whether this transfers to other institutes.
- a `dataformat` column that identifies the format for each camera of the data (e.g. # bits) stored in the blob. Again, I don't know if this translates to cameras for other facilities. In our case the last frame of a PSII snapshot is actually the original .pim file native to the camera. this uses dataformat=100000
- image dimensions are actually stored in the table and in the future you should use that information for converting the blobs to images


## History

This script was originally written at the [Danforth Center](https://github.com/danforthcenter/data-science-tools) and this version was based on a [fork](https://github.com/CougPhenomics/data-engineering-tools) of a [fork by Adam Dimech](https://github.com/AdamDimech/data-science-tools). Future development will happen here.






