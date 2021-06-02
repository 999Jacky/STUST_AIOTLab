import numpy as np

im_width = 640
im_height = 480


def del_repeat_box(boxs: dict, scores: dict, min_scores):
    img_map = np.zeros((im_height + 1, im_width + 1))
    for i in range(0, len(boxs)):
        if scores[i] >= min_scores:
            ymin, xmin, ymax, xmax = boxs[i]
            pos = np.array([xmin * im_width, xmax * im_width,
                            ymin * im_height, ymax * im_height], dtype=np.float64)
            posInt = pos.astype(np.int32)
            (left, right, top, bottom) = posInt
            box_size = (right - left) * (bottom - top)
            map_count = img_map[np.where(img_map[top:bottom, left:right] > 0)].size
            if map_count < box_size * 0.8:
                img_map[top:bottom, left:right] = 1
            else:
                scores[i] = 0
    return scores


def get_pos_range(boxs: dict, scores: dict, min_scores):
    minx = 999
    miny = 999
    maxx = 0
    maxy = 0
    for i in range(0, len(boxs)):
        if scores[i] >= min_scores:
            ymin, xmin, ymax, xmax = boxs[i]
            pos = np.array([xmin * im_width, xmax * im_width,
                            ymin * im_height, ymax * im_height], dtype=np.float64)
            posInt = pos.astype(np.int32)
            (left, right, top, bottom) = posInt
            if left < minx:
                minx = left
            if right > maxx:
                maxx = right
            if top < miny:
                miny = top
            if bottom > maxy:
                maxy = bottom
    return np.array([minx, maxx, miny, maxy])


def get_crop_img(img, boxs: dict, scores: dict, min_scores):
    minx, maxx, miny, maxy = get_pos_range(boxs, scores, min_scores)
    i = img[miny:maxy, minx:maxx, :]
    return i
