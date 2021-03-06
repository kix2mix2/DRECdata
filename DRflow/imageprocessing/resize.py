import os
import sys
import PIL.ImageOps
import cv2
import numpy as np
from PIL import Image
import ray


def resize_img(file, save_dir, dim=[50, 50], crop=False):
    filename = save_dir + file.split("/")[-1]
    if os.path.exists(filename):
        print("Skipping...")
    try:
        # img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        img = Image.open(r"{}".format(file))
        # print(img.size)
    except:
        print(sys.exc_info())
        print("FAILURE reading!")
        return


    if crop:
        width, height = img.size  # Get dimensions

        left = (width - 2250) / 2
        top = (height - 2250) / 2
        right = (width + 2250) / 2
        bottom = (height + 2250) / 2

        img = img.crop((left, top, right, bottom))


    # for i in [0, 1]:
    #     if img.size[i] < dim[i]:
    #         dim[i] = img.size[i]

    # print(img.size)
    dim = tuple(dim)
    try:
        # resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        resized = img.resize(dim, resample=0)

    except:
        print("FAILURE resizing!")
        return

    # if resized.shape[0]<200:
    #     resized = cv2.resize(img, dim, interpolation = cv2.INTER_NEAREST)
    print(resized.size)
    print("Saving to: {}".format(save_dir + file.split("/")[-1]))
    # cv2.imwrite(filename, resized)
    resized.save(filename)

@ray.remote
def resize_all(input_folder, output_folder="size", dim=[50, 50]):
    # if destination folder doesn't exist, create it
    save_dir = output_folder
    print(save_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # list or files in this folder
    files = os.listdir(input_folder)
    for i, f in enumerate(files):
        print(i, f)
        # if file is a directory of images
        if (
            os.path.isdir(input_folder + "/" + f)
            and not f.startswith(".")
            and not f.startswith("_")
        ):
            subfiles = os.listdir(input_folder + "/" + f)
            for ff in subfiles:
                if ff.endswith(".png") or ff.endswith(".jpg"):
                    resize_img(input_folder + f + "/" + ff, save_dir, dim=dim)

        # if file is an image
        elif f.endswith(".png") or f.endswith(".jpg"):
            if f.endswith(".jpg"):
                new_name = input_folder + f.split(".")[0] + ".png"
                os.rename(input_folder + f, new_name)
                resize_img(new_name, save_dir, dim=dim)
            else:
                resize_img(input_folder + f, save_dir, dim=dim)
        else:
            print("The method did not work for this file.")
        print("------")


def rename_data(folder):
    files = os.listdir(folder)

    for f in files:
        if f.startswith("."):
            continue
        new_f = f.split("-")[-1]
        if not os.path.exists(folder + new_f):
            os.mkdir(folder + new_f)

        print(new_f)
        for img in os.listdir(folder + new_f):
            # print(img)
            new_img = f + "_" + img.split("_")[-1]
            # print(new_img)
            os.replace(folder + new_f + "/" + img, folder + new_f + "/" + new_img)


def save_images(data, label, name="MNIST"):
    # create folder for each dataset
    save_folder = os.getcwd() + "/" + name + "/"
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    save_folder += "thumbnails/"
    if not os.path.exists(save_folder):
        os.mkdir(save_folder)

    print(save_folder)
    print(data.shape)

    # if data is in image version
    if len(data.shape) > 2:
        pass
    # if data is flat
    if len(data.shape) == 2:
        for i in range(data.shape[0]):
            img = np.array(data[i].reshape(28, 28)).astype(np.uint8)

            img = Image.fromarray(img)

            img = PIL.ImageOps.invert(img)

            img.save(save_folder + "{}_{}.png".format(label[i], i))
