from ..utils import utils
import numpy as np
import numpy.core.multiarray
import cv2
import sys


def eval_asymmetric(mask):
    """
    :param mask: segmentation mask of mole.
    :return: ratio between uncommon pixels and common pixels
             of the 2 parts that divided from the center both horizontal and vertical.
    """
    aligned_mask = utils.align(mask)
    bias = 0.35  # for nice appearance in the bar (too avoid small scores)
    width_center = aligned_mask.shape[1] // 2
    height_center = aligned_mask.shape[0] // 2
    if aligned_mask.shape[1] % 2 == 0:
        left_half = aligned_mask[:, 0: width_center]
    else:
        left_half = aligned_mask[:, 0: width_center + 1]
    right_half = aligned_mask[:, width_center: aligned_mask.shape[1]]
    if aligned_mask.shape[0] % 2 == 0:
        upper_half = aligned_mask[0: height_center, :]
    else:
        upper_half = aligned_mask[0: height_center + 1, :]
    bottom_half = aligned_mask[height_center: aligned_mask.shape[0], :]
    left_half = cv2.flip(left_half, 1)
    bottom_half = cv2.flip(bottom_half, 0)
    or_vertical = cv2.bitwise_or(left_half, right_half)
    and_vertical = cv2.bitwise_and(left_half, right_half)
    result_vertical = cv2.bitwise_xor(or_vertical, and_vertical)
    or_horizontal = cv2.bitwise_or(upper_half, bottom_half)
    and_horizontal = cv2.bitwise_and(upper_half, bottom_half)
    result_horizontal = cv2.bitwise_xor(or_horizontal, and_horizontal)
    horizontal_score = np.sum(result_horizontal) / np.sum(or_horizontal)
    vertical_score = np.sum(result_vertical) / np.sum(or_vertical)
    result = (horizontal_score + vertical_score) / 2.0 + bias
    return min(1.0, result)

if __name__ == '__main__':
    seg_mask = cv2.imread('/home/haimzis/PycharmProjects/DL_training_preprocessing/Output/objects_extraction/annotations/ISIC_0014190_segmentation.png',  -1)
    print(eval_asymmetric(seg_mask))