from bs4 import BeautifulSoup as BSHTML
import urllib
import requests
import ray
import pandas as pd
import os

def crawl_the_soup(
    file_of_links="paintings/painting_dataset_2018.csv",
    save_folder="paintings/original_files/",
):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    df = pd.read_csv(file_of_links, sep=";")
    df.columns = ["img", "url", "subset", "labels"]
    df.drop(["img", "subset"], axis=1, inplace=True)
    print(df.shape)

    for i, row in df.iterrows():
        download_one.remote(i, row, save_folder)

@ray.remote
def download_one(i, row, save_folder):
    try:
        page = urllib.request.urlopen(row["url"])
        soup = BSHTML(page)
        images = soup.findAll("img")
    except:
        print("broken link")
        return

    for image in images:
        print(image["src"])
        try:
            row["labels"] = row["labels"].strip("'")[1:].replace(" ", "_")
            print(row)
            f = open(
                save_folder + "{}_{}.png".format(row["labels"].strip("'"), i), "wb"
            )
            f.write(requests.get(image["src"]).content)
            f.close()
        except:
            return
        return