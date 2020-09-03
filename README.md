# cppcpyutils

Utilities for image processing pipelines at the Compact Plants Phenomics Center at Washingtion State University - Pullman. Pipelines are designed around [PlantCV](https://github.com/danforthcenter/plantcv)

## Installation

Install latest release

`pip install cppcpyutils`

Install dev version

`pip install git+https://github.com/CougPhenomics/cppcpyutils.git`

## Use

There are two components to the package:

1. A command line interface to download images from the LemnaTec database which is documented [here](docs/LT_db_extractor.md)
2. A python package that wraps some commonly used processes in the PlantCV workflows.

At the top of a PlantCV workflow starts with:

```python
#!/usr/bin/env python
import os
import argparse
import cppcpyutils as cppc
from plantcv import plantcv as pcv
```

In the workflow you will need to assign `cppc.pixelresolution` to the pixel resolution of the camera you are analyzing.

The main user facing function is `cppc.roi.iterate_rois()` which will run a loop through each roi and save to the PlantCV Outputs for each plant.

You have some options for which outputs to compute and save but plant_area (in mm<sup>2</sup>) and shape dimensions are always saved. Optionally you can save greenness index (`gi`) with a pseudocolor image, all color information (`hist`) with the histogram saved, or just hsv (`hue`) with a hue pseudocolor image


