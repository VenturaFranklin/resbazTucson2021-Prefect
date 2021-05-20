import glob
import logging
import os
import time
from pathlib import Path

import cv2
import numpy as np
import prefect
import skimage
import skimage.filters as sk_filters
from prefect import Flow, Parameter, case, task, Client
from skimage import img_as_ubyte, io
from skimage.color import rgb2gray

import BaseImage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@task
def load_image(file_name, image_work_size):
    logger = prefect.context.get("logger")
    image = BaseImage.BaseImage(
        file_name,
        params=dict(
            image_work_size=image_work_size,
            mask_statistics="relative2mask",
            confirm_base_mag="False",
        ),
    )
    return image


@task
def tissue_segmentation_simple(image, image_work_size):
    logger = prefect.context.get("logger")
    logger.info(fr"{image['filename']} - \ttissue_segmentation_simple")
    img = image.getImgThumb(image_work_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = 255 - img
    img[img == 255] = 0
    otsu_thresh_value = sk_filters.threshold_otsu(img)
    img = img > otsu_thresh_value
    img = img.astype("uint8") * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    img = cv2.dilate(img, kernel, iterations=3)
    io.imsave(
        image["outdir"] + os.sep + image["filename"] + "_tissue_seg.png",
        img_as_ubyte(img),
    )
    image["img_mask_use"] = img
    return None


@task
def identifyBlurryRegions(image, image_work_size, blur_radius, blur_threshold):
    logger = prefect.context.get("logger")
    logger.info(f"{image['filename']} - \tidentifyBlurryRegions")
    img = image.getImgThumb(image_work_size)
    img = rgb2gray(img)
    img_laplace = np.abs(skimage.filters.laplace(img))
    mask = skimage.filters.gaussian(img_laplace, sigma=blur_radius) <= blur_threshold
    mask = skimage.transform.resize(
        mask, image.getImgThumb(image["image_work_size"]).shape, order=0
    )[
        :, :, 1
    ]  # for some reason resize takes a grayscale and produces a 3chan
    img = image["img_mask_use"] & (mask > 0)
    mask = rgb2gray(mask)
    io.imsave(
        image["outdir"] + os.sep + image["filename"] + "_blurry.png", img_as_ubyte(mask)
    )
    image["img_mask_blurry"] = (img * 255) > 0
    prev_mask = image["img_mask_use"]
    image["img_mask_use"] = image["img_mask_use"] & ~image["img_mask_blurry"]
    image.addToPrintList(
        "percent_blurry",
        BaseImage.printMaskHelper(
            image["mask_statistics"],
            prev_mask,
            image["img_mask_use"],
        ),
    )
    return float(image["percent_blurry"])


@task
def blurry_action(image, percent_blurry):
    logger = prefect.context.get("logger")
    logger.warning(
        f"Need to rescan, too blurry {percent_blurry*100} {image['filename']}"
    )


@task
def check_blurry(percent_blurry, blur_max):
    return percent_blurry > blur_max


def define_flow():
    with Flow("Image QC Flow") as flow:
        image_work_size = Parameter("image_work_size")
        file_name = Parameter("file_name")
        blur_radius = Parameter("blur_radius")
        blur_threshold = Parameter("blur_threshold")
        blur_max = Parameter("blur_max")
        image = load_image(file_name, image_work_size)
        result = tissue_segmentation_simple(image, image_work_size)
        percent_blurry = identifyBlurryRegions(
            image,
            image_work_size,
            blur_radius,
            blur_threshold,
            upstream_tasks=[result],
        )
        blurry = check_blurry(percent_blurry, blur_max)
        with case(blurry, True):
            blurry_action(image, percent_blurry)
        flow.visualize(filename="pipeline_viz")
    return flow


def main(folder, filetype):
    start = time.time()
    files = glob.glob(str(Path(folder) / f"*.{filetype}"))
    image_work_size = "1.25x"
    blur_radius = 7
    blur_threshold = 0.05
    blur_max = 0.05
    logger.info(f"Files to process {files}")
    flow = define_flow()
    flow.register(project_name="Image QC")
    client = Client()
    flow_id = client.register(flow=flow, project_name="Image QC")
    for file_name in files:
        client.create_flow_run(
            flow_id=flow_id,
            run_name="Image QC RUN",
            parameters=dict(
                file_name=file_name,
                image_work_size=image_work_size,
                blur_radius=blur_radius,
                blur_threshold=blur_threshold,
                blur_max=blur_max,
            ),
        )
    end = time.time()
    logger.info(f"Total time to process {end-start}")


if __name__ == "__main__":
    folder = "data"
    filetype = "svs"
    main(folder, filetype)
    # define_flow()
