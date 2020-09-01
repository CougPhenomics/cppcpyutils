import os
from plantcv import plantcv as pcv
import cppcpyutils as cppc
import re
import json
import numpy as np


def copy_metadata(args):
    '''Copy metadata for each image so it can be used for each ROI
    Inputs:
        args: commandline info from running the workflow
    Returns:
        args: updated args to include filename metadata
    '''

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


def iterate_rois(img, c, h, rc, rh, args, masked=True, gi=False, shape=False, hist=True, hue=False):
    '''Analyze each ROI separately and store results
    Inputs:
        img: rgb image
        c: object contours
        h: object countour hierarchy
        rc: roi contours
        rh: roi contour hierarchy
        threshold_mask: mask from threshold steps
        args: commandline info from running the workflow
        masked: boolean, whether to print masked images for each roi
        gi: grayscale image that contains greenness index values. default is False to skip print.
        shape: boolean, whether to print object shapes
        hist: boolean, whether to print colorhistogram
        hue: boolean, whether to print the hue false color
    Returns:
        final_mask: binary image of plant mask that includes both threshold and roi filter steps
    '''

    final_mask = np.zeros(shape=np.shape(img)[0:2], dtype='uint8')

    # Compute greenness
    if gi:
        gi = cppc.util.greenness_index(img=img, mask=final_mask+1)

    for i, rc_i in enumerate(rc):
        rh_i = rh[i]

        # Add ROI number to output. Before roi_objects so result has NA if no object.
        pcv.outputs.add_observation(
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
                grnindex = cppc.util.mean(gi, plant_mask)
                grnindexstd = cppc.util.std(gi, plant_mask)
                pcv.outputs.add_observation(
                    variable='greenness_index',
                    trait='mean normalized greenness index',
                    method='g/sum(b+g+r)',
                    scale='[0,1]',
                    datatype="<class 'float'>",
                    value=float(grnindex),
                    label='/1')

                pcv.outputs.add_observation(
                    variable='greenness_index_std',
                    trait='std normalized greenness index',
                    method='g/sum(b+g+r)',
                    scale='[0,1]',
                    datatype="<class 'float'>",
                    value=float(grnindexstd),
                    label='/1')

            # Analyze all colors
            colorhist = pcv.analyze_color(img, plant_mask, 'all')
            img_h = pcv.rgb2gray_hsv(img, 'h')

            # Analyze the shape of the current plant
            shape_img = pcv.analyze_object(img, plant_object, plant_mask)
            plant_area = pcv.outputs.observations['area']['value'] * cppc.pixelresolution**2
            pcv.outputs.add_observation(
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
        # Here I will name the results file with the ROI ID combined with the original result filename
        basename, ext = os.path.splitext(args.result)
        filename = basename + "-roi" + str(i) + ext
        # Save the existing metadata to the new file
        with open(filename, "w") as r:
            json.dump(args.metadata, r)
        pcv.print_results(filename=filename)
        # The results are saved, now clear out the observations so the next loop adds new ones for the next plant
        pcv.outputs.clear()

        if args.writeimg and obj_area != 0:
            if shape:
                imgdir = os.path.join(args.outdir, 'shape_images', args.plantbarcode)
                os.makedirs(imgdir, exist_ok=True)
                pcv.print_image(shape_img, os.path.join(imgdir, args.imagename + '-roi' + str(i) + '-shape.png'))

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
                hue_img = pcv.visualize.pseudocolor(img_h*2, obj=None,
                                                    mask=plant_mask,
                                                    cmap=cppc.viz.get_cmap('hue'),
                                                    axes=False,
                                                    min_value=0, max_value=179,
                                                    background='black', obj_padding=0)
                hue_img = cppc.viz.add_scalebar(hue_img,
                                    pixelresolution=cppc.pixelresolution,
                                    barwidth=10,
                                    barlabel='1 cm',
                                    barlocation='lower left')
                hue_img.set_size_inches(6, 6, forward=False)
                hue_img.savefig(os.path.join(imgdir, args.imagename + '-roi' + str(i) + '-hue.png'),
                                bbox_inches='tight',
                                dpi=300)
                hue_img.clf()

            if gi is not False:
                # save grnness image of entire tray but only 1 plant
                imgdir = os.path.join(args.outdir, 'grnindex_images')
                os.makedirs(imgdir, exist_ok=True)
                gi_img = pcv.visualize.pseudocolor(
                    gi, obj=None, mask=plant_mask, cmap='viridis', axes=False, min_value=0.3, max_value=0.6, background='black', obj_padding=0)
                gi_img = cppc.viz.add_scalebar(gi_img,
                                    pixelresolution=cppc.pixelresolution,
                                    barwidth=10,
                                    barlabel='1 cm',
                                    barlocation='lower left')
                gi_img.set_size_inches(6, 6, forward=False)
                gi_img.savefig(os.path.join(imgdir, args.imagename + '-roi' + str(i) + '-greenness.png'), bbox_inches='tight', dpi=300)
                gi_img.clf()

        # end roi loop
    return final_mask
