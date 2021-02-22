import os
from plantcv import plantcv as pcv
import cppcpyutils as cppc
import re
import json
import numpy as np


def copy_metadata(args):
    """Copy metadata for each image so it can be used for each ROI

    Parameters
    ----------
        args : dict
            commandline info from running the workflow

    Returns
    -------
        updated args to include filename metadata : dict

    """

    # The result file should exist if plantcv-workflow.py was run
    if os.path.exists(args.result):
        # Open the result file
        results = open(args.result, "r")
        # The result file would have image metadata in it from plantcv-workflow.py, read it into memory
        args.metadata = json.load(results)
        # Close the file
        results.close()
        # Delete the file, we will create new ones
        os.remove(args.result)
        args.plantbarcode = args.metadata['metadata']['plantbarcode']['value']
        print('\n')
        print(args.plantbarcode,
              args.metadata['metadata']['timestamp']['value'],
              sep=' - ')
    else:
        # If the file did not exist (for testing), initialize metadata as an empty string
        args.metadata = {}
        regpat = re.compile(args.regex)
        args.plantbarcode = re.search(regpat, args.image).groups()[0]

    return args


def write_output(args, i):
    """Write Outputs for a single ROI

    Parameters
    ----------
    args : dict
        commandline arguments and image metadata
    i : int
        ROI number

    Returns
    -------

    Notes
    -----
    Side effect of printing a json file to disk

    """
    # Here I will name the results file with the ROI ID combined with the original result filename
    basename, ext = os.path.splitext(args.result)
    filename = basename + "-roi" + str(i) + ext
    # Save the existing metadata to the new file
    with open(filename, "w") as r:
        json.dump(args.metadata, r)
    pcv.print_results(filename=filename)
    # The results are saved, now clear out the observations so the next loop adds new ones for the next plant
    pcv.outputs.clear()


def iterate_rois(img, c, h, rc, rh, args, masked=True, gi=False, shape=False, hist=True, hue=False):
    """Analyze each ROI separately and store results

    Parameters
    ----------
    img : ndarray
        rgb image
    c : list
        object contours
    h : list
        object countour hierarchy
    rc : list
        roi contours
    rh : list
        roi contour hierarchy
    threshold_mask : ndarray
        binary image (mask) from threshold steps
    args : dict
        commandline arguments and metadata from running the workflow
    masked : boolean
        whether to print masked rgb images for each roi
    gi : boolean
        whether to print greenness index false color
    shape : boolean
        whether to print object shapes on an image
    hist : boolean
        whether to print color histogram
    hue : boolean
        whether to save hsv color info and print the hue false color image

    Returns
    -------
        binary image of plant mask that includes both threshold and roi filter steps : ndarray

    """

    final_mask = np.zeros(shape=np.shape(img)[0:2], dtype='uint8')

    # Compute greenness
    if gi:
        img_gi = cppc.compute.greenness_index(img=img, mask=final_mask+1)

    if hue:
        img_h = pcv.rgb2gray_hsv(img, 'h')

    for i, rc_i in enumerate(rc):
        rh_i = rh[i]

        # Add ROI number to output. Before roi_objects so result has NA if no object.
        pcv.outputs.add_observation(
            sample='default',
            variable='roi',
            trait='roi',
            method='roi',
            scale='int',
            datatype=int,
            value=i,
            label='#')

        roi_obj, hierarchy_obj, submask, obj_area = pcv.roi_objects(
            img, roi_contour=rc_i, roi_hierarchy=rh_i, object_contour=c, obj_hierarchy=h, roi_type='partial')

        if obj_area == 0:

            print('\t!!! No object found in ROI', str(i))
            pcv.outputs.add_observation(
                sample='default',
                variable='plantarea',
                trait='plant area in sq mm',
                method='observations.area*pixelresolution^2',
                scale=cppc.pixelresolution,
                datatype="<class 'float'>",
                value=0,
                label='sq mm')

        else:

            # Combine multiple objects
            # ple plant objects within an roi together
            plant_object, plant_mask = pcv.object_composition(
                img=img, contours=roi_obj, hierarchy=hierarchy_obj)

            final_mask = pcv.image_add(final_mask, plant_mask)

            if gi:
                # Save greenness for individual ROI
                grnindex = cppc.utils.mean(img_gi, plant_mask)
                grnindexstd = cppc.utils.std(img_gi, plant_mask)
                pcv.outputs.add_observation(
                    sample='default',
                    variable='greenness_index',
                    trait='mean normalized greenness index',
                    method='g/sum(b+g+r)',
                    scale='[0,1]',
                    datatype="<class 'float'>",
                    value=float(grnindex),
                    label='/1')

                pcv.outputs.add_observation(
                    sample='default',
                    variable='greenness_index_std',
                    trait='std normalized greenness index',
                    method='g/sum(b+g+r)',
                    scale='[0,1]',
                    datatype="<class 'float'>",
                    value=float(grnindexstd),
                    label='/1')

            # Analyze all colors
            if hist:
                colorhist = pcv.analyze_color(img, plant_mask, 'all')
            elif hue:
                _ = pcv.analyze_color(img, plant_mask, 'hsv')

            # Analyze the shape of the current plant (always do this even if shape is False so you can get plant_area)
            img_shape = pcv.analyze_object(img, plant_object, plant_mask)
            plant_area = pcv.outputs.observations['default']['area']['value'] * cppc.pixelresolution**2
            pcv.outputs.add_observation(
                sample='default',
                variable='plantarea',
                trait='plant area in sq mm',
                method='observations.area*pixelresolution^2',
                scale=cppc.pixelresolution,
                datatype="<class 'float'>",
                value=plant_area,
                label='sq mm')
        # end if-else

        # At this point we have observations for one plant
        # We can write these out to a unique results file
        write_output(args, i)

        if args.writeimg and obj_area != 0:
            if shape:
                imgdir = os.path.join(args.outdir, 'shape_images', args.plantbarcode)
                os.makedirs(imgdir, exist_ok=True)
                pcv.print_image(img_shape, os.path.join(imgdir, args.imagename + '-roi' + str(i) + '-shape.png'))

            if hist:
                imgdir = os.path.join(args.outdir, 'colorhist_images', args.plantbarcode)
                os.makedirs(imgdir, exist_ok=True)
                pcv.print_image(colorhist, os.path.join(imgdir, args.imagename + '-roi' + str(i) + '-colorhist.png'))

            if masked:
                # save masked rgb image for entire tray but only 1 plant
                imgdir = os.path.join(args.outdir, 'maskedrgb_images')
                os.makedirs(imgdir, exist_ok=True)
                img_masked = pcv.apply_mask(img, plant_mask, 'black')
                pcv.print_image(
                    img_masked,
                    os.path.join(imgdir,
                                 args.imagename + '-roi' + str(i) + '-masked.png'))

            if hue:
                # save hue false color image for entire tray but only 1 plant
                imgdir = os.path.join(args.outdir, 'hue_images')
                os.makedirs(imgdir, exist_ok=True)
                fig_hue = pcv.visualize.pseudocolor(img_h*2, obj=None,
                                                    mask=plant_mask,
                                                    cmap=cppc.viz.get_cmap('hue'),
                                                    axes=False,
                                                    min_value=0, max_value=179,
                                                    background='black', obj_padding=0)
                fig_hue = cppc.viz.add_scalebar(fig_hue,
                                    pixelresolution=cppc.pixelresolution,
                                    barwidth=10,
                                    barlabel='1 cm',
                                    barlocation='lower left')
                fig_hue.set_size_inches(6, 6, forward=False)
                fig_hue.savefig(os.path.join(imgdir, args.imagename + '-roi' + str(i) + '-hue.png'),
                                bbox_inches='tight',
                                dpi=300)
                fig_hue.clf()

            if gi:
                # save grnness image of entire tray but only 1 plant
                imgdir = os.path.join(args.outdir, 'grnindex_images')
                os.makedirs(imgdir, exist_ok=True)
                fig_gi = pcv.visualize.pseudocolor(img_gi,
                                                   obj=None,
                                                   mask=plant_mask,
                                                   cmap='viridis',
                                                   axes=False,
                                                   min_value=0.3,
                                                   max_value=0.6,
                                                   background='black',
                                                   obj_padding=0)
                fig_gi = cppc.viz.add_scalebar(
                    fig_gi,
                    pixelresolution=cppc.pixelresolution,
                    barwidth=10,
                    barlabel='1 cm',
                    barlocation='lower left')
                fig_gi.set_size_inches(6, 6, forward=False)
                fig_gi.savefig(os.path.join(
                    imgdir,
                    args.imagename + '-roi' + str(i) + '-greenness.png'),
                               bbox_inches='tight',
                               dpi=300)
                fig_gi.clf()

        # end roi loop
    return final_mask
