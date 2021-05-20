import glob
import logging
import os
import time
from pathlib import Path

import cv2
import numpy as np
import skimage
import skimage.filters as sk_filters
from skimage import img_as_ubyte, io
from skimage.color import rgb2gray

import BaseImage

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def load_image(file_name, image_work_size):
    image = BaseImage.BaseImage(
        file_name,
        params=dict(
            image_work_size=image_work_size,
            mask_statistics="relative2mask",
            confirm_base_mag="False",
        ),
    )
    return image


def tissue_segmentation_simple(image, image_work_size):
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


def identifyBlurryRegions(image, image_work_size, blur_radius, blur_threshold):
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


def blurry_action(image, percent_blurry):
    logger.warning(f"Need to rescan, too blurry {percent_blurry*100} {image['filename']}")


def main(folder, filetype):
    start = time.time()
    files = glob.glob(str(Path(folder) / f"*.{filetype}"))
    image_work_size = "1.25x"
    blur_radius = 7
    blur_threshold = 0.05
    blur_max = 0.05
    logger.info(f"Files to process {files}")
    for file_name in files:
        image = load_image(file_name, image_work_size)
        tissue_segmentation_simple(image, image_work_size)
        percent_blurry = identifyBlurryRegions(
            image, image_work_size, blur_radius, blur_threshold
        )
        if percent_blurry > blur_max:
            blurry_action(image, percent_blurry)
    end = time.time()
    logger.info(f"Total time to process {end-start}")


if __name__ == "__main__":
    folder = "data"
    filetype = "svs"
    main(folder, filetype)
