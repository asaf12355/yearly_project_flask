import cv2
import numpy as np

def find_object_coords(object_mask, coords=None):  # crop_coords = [ymin, ymax, xmin, xmax]
    if coords is None:
        min_y = 0
        max_y = object_mask.shape[0] - 1
        min_x = 0
        max_x = object_mask.shape[1] - 1
    else:
        min_y = coords[0]
        max_y = coords[1]
        min_x = coords[2]
        max_x = coords[3]

    # y coords
    while not object_mask[min_y, min_x:max_x].any():
        min_y += 1
    while not object_mask[max_y, min_x:max_x].any():
        max_y -= 1

    # x coords
    while not object_mask[min_y:max_y, min_x].any():
        min_x += 1
    while not object_mask[min_y:max_y, max_x].any():
        max_x -= 1

    return [min_y, max_y, min_x, max_x]


def cut_roi_from_mask(mask, coords):  # crop_coords = [ymin, ymax, xmin, xmax]
    return mask[coords[0]: coords[1], coords[2]: coords[3]]


def rotate(mask, angle):
    """
    :param mask: segmentation mask
    :param angle: angle of rotation
    :return: rotated segmentation mask without information loss
    """
    height, width = mask.shape[:2]  # image shape has 3 dimensions
    image_center = (
    width / 2, height / 2)  # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

    rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

    # rotation calculates the cos and sin, taking absolutes of those.
    abs_cos = abs(rotation_mat[0, 0])
    abs_sin = abs(rotation_mat[0, 1])

    # find the new width and height bounds
    bound_w = int(height * abs_sin + width * abs_cos)
    bound_h = int(height * abs_cos + width * abs_sin)

    # subtract old image center (bringing image back to origo) and adding the new image center coordinates
    rotation_mat[0, 2] += bound_w / 2 - image_center[0]
    rotation_mat[1, 2] += bound_h / 2 - image_center[1]

    # rotate image with the new bounds and translated rotation matrix
    rotated_mat = cv2.warpAffine(mask, rotation_mat, (bound_w, bound_h))
    return rotated_mat


def align(mask):
    """
    :param mask: segmentation mask of mole.
    :return: aligned segmentation mask of the mole.
    """
    alignment_res = mask.copy()
    best_rotation_size = mask.shape[0]
    for angle in range(0, 180):
        res = rotate(mask, angle)
        res = cut_roi_from_mask(res, find_object_coords(res))
        if best_rotation_size < res.shape[0]:
            best_rotation_size = res.shape[0]
            alignment_res = res
    for i in range(0, alignment_res.shape[1]):
        for j in range(0, alignment_res.shape[0]):
            if alignment_res[j, i].any():
                alignment_res[j, i] = 255
    return alignment_res


def find_center_coords(mask_original_coords):  # crop_coords = [ymin, ymax, xmin, xmax]
    ymin, ymax, xmin, xmax = mask_original_coords
    center_coords = (ymax - ymin // 2, xmax - xmin // 2)
    return center_coords


def distance(coords1, coords2):
    return ((coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2) ** 0.5


def find_object_radius(mask_original_coords):
    center = find_center_coords(mask_original_coords)
    radius = max(distance(center, (mask_original_coords[0], mask_original_coords[0])),
                 distance(center, (mask_original_coords[0], mask_original_coords[1])),
                 distance(center, (mask_original_coords[1], mask_original_coords[0])),
                 distance(center, (mask_original_coords[1], mask_original_coords[1])))
    return radius


def reference_object_1ISL_recognition(reference_obj_image):
    ISL1_SIZE = 18  # mm
    roi = cv2.imread(reference_obj_image)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (15, 15), 0)
    circles = cv2.HoughCircles(gray_blur, cv2.HOUGH_GRADIENT, 2, roi.shape[0], param1=50, param2=30, minRadius=0, maxRadius=0)
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        cv2.circle(roi, (i[0], i[1]), i[2], (0, 255, 0), 2)
        cv2.circle(roi, (i[0], i[1]), 2, (0, 0, 255), 3)
    # font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.putText(roi, "coin", (0, 400), font, 0.5, (0, 0, 0), 2, cv2.LINE_AA)
    # cv2.imshow('Detected coins', roi)
    # cv2.waitKey()

    return circles[0][0], ISL1_SIZE


if __name__ == '__main__':
    pass
