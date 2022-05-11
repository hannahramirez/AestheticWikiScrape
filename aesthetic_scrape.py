import os
import shutil

import requests
from bs4 import BeautifulSoup
import json
import cv2
import numpy as np
from sklearn.cluster import KMeans
import re


def collect_urls(url, fileName):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    with open(fileName, "w") as aesthetics:
        for a in soup.findAll('a'):
            if a.parent.name == 'li':
                aesthetics.write(a["href"] + "\n")
    # after this i manually cleaned up the list of any urls that were not an aesthetic
    # and made all absolute urls into relative urls (there was only a couple)
    # I then manually put the base url as the first line


def related_aesthetics():
    # opening the aesthetic file to reference
    with open("aesthetics.txt", "r") as fin:
        with open("nodes.csv", "w") as nodes:
            nodes.write("relative_path,label\n")
            with open("edges.csv", "w") as edges:
                # first line of document is the base url
                url = "https://aesthetics.fandom.com"

                # this list is for debugging purposes
                excluded = []
                deleted = []

                for relative_path in fin:
                    relative_path = relative_path.strip()
                    # get url for the specific aesthetic
                    path = (url + relative_path)
                    # print(path)

                    # grabs html from the individual aesthetic page
                    page = requests.get(path)
                    soup = BeautifulSoup(page.content, "html.parser")
                    # print(soup)

                    # get titles of aesthetic & the table with the related aesthetics
                    infoboxes = soup.findAll("aside", attrs={
                        "class": "portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default"})
                    page_name = soup.find(attrs={"class": "page-header__title"}).get_text().strip()

                    # break

                    if page_name == "List of Deleted Pages and Why":
                        excluded.append("deleted: " + relative_path)
                        deleted.append(relative_path)
                        continue

                    if infoboxes:
                        for box in infoboxes:
                            title = box.find(attrs={'data-source': 'title1'})
                            related = box.find_all(attrs={'data-source': 'related_aesthetics'})

                            if title and related:
                                title = title.get_text().strip()
                                nodes.write(title + ',' + path + "\n")
                                a_tags = related[0].find_all('a')
                                for a in a_tags:
                                    if a["href"] not in deleted:
                                        edges.write(title + "," + a.get_text() + "\n")
                            elif related:
                                nodes.write(page_name + ',' + path + '\n')
                                a_tags = related.find_all('a')
                                for a in a_tags:
                                    if a["href"] not in deleted:
                                        edges.write(title + "," + a.get_text() + "\n")
                            elif title:
                                nodes.write(page_name + ',' + path + "\n")
                            else:
                                excluded.append("error: " + page_name + "\n" + str(infoboxes))
                    else:
                        nodes.write(page_name + ',' + path + '\n')

                    print(page_name)
                print(excluded)


def grab_pictures():
    if os.path.isfile("images"):
        shutil.rmtree("images")
    os.mkdir("images")
    no_img = 0
    no_img_names = ""
    with open("aesthetics.txt", 'r') as aesthetics:
        with open("nodes_v2.csv", 'w') as output:
            # first line of document is the base url
            url = aesthetics.readline().strip()

            # goes through the list of relative urls
            for relative_path in aesthetics:
                relative_path = relative_path.strip()
                # get url for the specific aesthetic
                path = (url + relative_path)
                # print(path)

                # grabs html from the individual aesthetic page
                page = requests.get(path)
                soup = BeautifulSoup(page.content, "html.parser")
                # print(soup)

                # get titles of aesthetic & the table with the related aesthetics
                titles = soup.find_all(attrs={'data-source': 'title1'})
                images = soup.find_all("a", attrs={'class': 'image-thumbnail'})
                if len(images) == 0:
                    try:
                        name = titles[0].get_text()
                        file_name = "images/" + name.strip().replace(" ", "_").replace("/", "_") + ".png"
                        image_link = soup.find("img", attrs={"class": "thumbimage"})["src"]
                        r = requests.get(image_link).content
                        print(file_name)
                        with open(file_name, "wb+") as image:
                            image.write(r)
                        output.write(name + "," + file_name + "\n")
                    except:
                        print(relative_path)
                        no_img += 1
                        no_img_names += relative_path + "\n"
                else:
                    for t, i in zip(titles, images):
                        name = t.get_text()
                        file_name = "images/" + name.strip().replace(" ", "_").replace("/", "_") + ".png"
                        image_link = i["href"]
                        r = requests.get(image_link).content
                        print(file_name)
                        with open(file_name, "wb+") as image:
                            image.write(r)
                        output.write(name + "," + file_name + "\n")

    print(no_img)
    print(no_img_names)


def image_addresses():
    color_list = set()
    no_img = []
    no_text = []
    errors = {}
    with open("data.json", 'r') as jsonFile:
        data = json.load(jsonFile)
        nodes = data["nodes"]
        edges = data["edges"]
        for n in nodes:
            print(n["label"])
            name = n["label"]
            url = n["attributes"]["url"]

            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            images = soup.find_all("a", attrs={'class': 'image-thumbnail'})

            image_object = {}
            if len(images) == 0:
                try:
                    image_link = soup.find("img", attrs={"class": "thumbimage"})["src"]
                except:
                    name = n["label"]
                    no_img.append(name)
                    print(name + ": no image")

            else:
                image_link = images[0]["href"]
            if image_link:
                revision = image_link.find('/revision')
                if revision >= 0:
                    image_object["image"] = image_link[:revision]
                else:
                    image_object["image"] = image_link
                file_name = "images/" + name.strip().replace(" ", "_").replace("/", "_") + ".png"
                try:
                    pass
                    # r = requests.get(image_link).content
                    # with open(file_name, "wb+") as image:
                    #     image.write(r)
                    #
                    #     src_img = cv2.imread(file_name)
                    #     average_color_row = np.average(src_img, axis=0)
                    #     average_color = np.average(average_color_row, axis=0)
                    #     colors = [round(c) for c in average_color]
                    #     n["color"] = 'rgb(' + str(colors[0]) + ',' + str(colors[1]) + ',' + str(colors[2]) + ')'
                    # for e in edges:
                    #     if e["source"] == name:
                    #         e["color"] = n["color"]
                except Exception as inst:
                    errors[name.lower()] = inst

                n["attributes"].update(image_object)

            bold = soup.find_all('b')
            i = None
            for b in bold:
                if b.get_text().lower() == n['label'].lower():
                    i = b
                    break;

            string = ''
            if not i:
                i = soup.find('aside', attrs={
                    'class': 'portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default'})
                if i:
                    i = i.next_sibling
                else:
                    i = soup.find(id='history')
                    if i:
                        i = i.next_sibling
            try:
                while i and i.name != 'p':
                    string += i.get_text()
                    i = i.next_sibling
                    if not i:
                        break
                if not string.strip():
                    name = n['label'].lower()
                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        if name in str(p).lower() and 'aside' not in str(p):
                            string = p.get_text()
                            break
                if not string.strip():
                    no_text.append(name)
                    continue
                text_object = {"description": str(string)}
                n["attributes"].update(text_object)
            except:
                no_text.append(n['label'])



        print(len(no_img))
        print(no_img)

        print(len(no_text))
        print(no_text)

        print(len(errors))
        print(errors)
        with open("data_mod.json", 'w') as jsonOutput:
            new_data = json.dumps(data)
            jsonOutput.write(new_data)


def kMeansColor():
    color_list = set()
    no_img = []
    no_text = []
    errors = {}
    with open("data.json", 'r') as jsonFile:
        data = json.load(jsonFile)
        nodes = data["nodes"]
        edges = data["edges"]
        for n in nodes:
            print(n["label"])
            name = n["label"]
            url = n["attributes"]["url"]

            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            images = soup.find_all("a", attrs={'class': 'image-thumbnail'})

            image_object = {}
            if len(images) == 0:
                try:
                    image_link = soup.find("img", attrs={"class": "thumbimage"})["src"]
                except:
                    name = n["label"]
                    no_img.append(name)
                    print(name + ": no image")

            else:
                image_link = images[0]["href"]
            if image_link:
                revision = image_link.find('/revision')
                if revision >= 0:
                    image_object["image"] = image_link[:revision]
                else:
                    image_object["image"] = image_link
                file_name = "images/" + name.strip().replace(" ", "_").replace("/", "_") + ".png"
                try:
                    r = requests.get(image_link).content
                    # with open(file_name, "wb+") as image:
                    #     image.write(r)
                    #     src_img = cv2.imread(file_name)
                    #     src_image = cv2.cvtColor(src_img, cv2.COLOR_BGR2RGB)
                    #     reshape_img = src_image.reshape((src_image.shape[0] * src_image.shape[1], 3))
                    #     KM_cluster = KMeans(n_clusters=5).fit(reshape_img)
                    #     hold = visualize_Dominant_colors(KM_cluster, KM_cluster.cluster_centers_)
                    #
                    #     colors = [round(c) for c in hold[0][1]]
                    #     n["color"] = 'rgb(' + str(colors[0]) + ',' + str(colors[1]) + ',' + str(colors[2]) + ')'
                    # for e in edges:
                    #     if e["source"] == name:
                    #         e["color"] = n["color"]
                except Exception as inst:
                    errors[name.lower()] = inst
                    print(inst)

                n["attributes"].update(image_object)

            bold = soup.find_all('b')
            i = None
            for b in bold:
                if b.get_text().lower() == n['label'].lower():
                    i = b
                    break;

            string = ''
            if not i:
                i = soup.find('aside', attrs={
                    'class': 'portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default'})
                if i:
                    i = i.next_sibling
                else:
                    i = soup.find(id='history')
                    if i:
                        i = i.next_sibling
            try:
                while i and i.name != 'p':
                    string += i.get_text()
                    i = i.next_sibling
                    if not i:
                        break
                if not string.strip():
                    name = n['label'].lower()
                    paragraphs = soup.find_all('p')
                    for p in paragraphs:
                        if name in str(p).lower() and 'aside' not in str(p):
                            string = p.get_text()
                            break
                text_object = {"description": str(string)}
                n["attributes"].update(text_object)
            except:
                no_text.append(n['label'])



        print(len(no_img))
        print(no_img)

        print(len(no_text))
        print(no_text)

        print(len(errors))
        print(errors)
        with open("data_mod.json", 'w') as jsonOutput:
            new_data = json.dumps(data)
            jsonOutput.write(new_data)


def visualize_Dominant_colors(cluster, C_centroids):
    C_labels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    (C_hist, _) = np.histogram(cluster.labels_, bins = C_labels)
    C_hist = C_hist.astype("float")
    C_hist /= C_hist.sum()

    rect_color = np.zeros((50, 300, 3), dtype=np.uint8)
    img_colors = sorted([(percent, color) for (percent, color) in zip(C_hist, C_centroids)], reverse=True)
    print(img_colors)
    return img_colors


def compare_sets():
    nodes = set()
    edges = set()
    with open("nodes.csv", 'r') as node_file:
        node_file.readline()
        for line in node_file:
            aes = line.strip().split(",")
            nodes.add(aes[0])
    with open("edges.csv", 'r') as edge_file:
        for line in edge_file:
            aes = line.strip().split(',')
            for a in aes:
                edges.add(a)

    print("node file: " + str(len(nodes)))
    print("edges file: " + str(len(edges)))

    difference = edges - nodes
    print("edges file: " + str(len(difference)))
    print(difference)



    with open("not_listed.csv", 'w') as missed:
        for d in difference:
            fixed = d.replace(" ", "_")
            missed.write("/wiki/" + fixed + "\n")

    # with open("edges_cleaned.csv", 'w')


def test(url, name):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    aside = soup.find('aside', attrs={
        'class': 'portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default'})
    print(aside.next_sibling)

    paragraphs = soup.find_all('p')
    for p in paragraphs:
        if name in str(p).lower():
            print(p)

def comparePages(allPages_file, list_file ):
    url = "https://aesthetics.fandom.com"
    pageSet = set()
    listSet = set()
    with open(allPages_file, 'r') as pages:
        for line in pages:
            pageSet.add(line.strip())
    with open(list_file, 'r') as lists:
        for line in lists:
            listSet.add(line.strip())

    notOnList = pageSet - listSet
    deleted = listSet - pageSet

    excluded = []
    redirected = []

    finalList = []

    for relative_path in notOnList:
        relative_path = relative_path.strip()
        # get url for the specific aesthetic
        path = (url + relative_path)
        print(path)

        # grabs html from the individual aesthetic page
        page = requests.get(path)
        soup = BeautifulSoup(page.content, "html.parser")
        page_name = soup.find(attrs={"class": "page-header__title"}).get_text().strip()
        save = str(soup.get_text()).lower()
        print(save)
        if page_name == "List of Deleted Pages and Why":
            excluded.append("deleted: " + relative_path)
            continue
        elif "redirected" in save:
            print(save)
            redirected.append(relative_path)
        else:
            finalList.append(relative_path)


    with open("not_listed.txt", 'w') as notList:
        organized = sorted(finalList)
        for a in organized:
            notList.write(a + '\n')

    with open("deleted.txt", 'w') as deletedFile:
        organized = sorted(deleted)
        for a in organized:
            deletedFile.write(a + '\n')

    print(excluded)

    print(redirected)


def colorFix():
    with open("data_mod.json", "r") as jsonFile:
        data = json.load(jsonFile)
        nodes = data["nodes"]
        edges = data["edges"]

        color = set()

        for n in nodes:
            color.add(n["color"])

        # for e in edges:
        #     if e["source"] == name:
        #         e["color"] = n["color"]

        print(len(color))
        print(color)






if __name__ == "__main__":
    # this was from my previous attempt
    # aesthetics_url = "https://aesthetics.fandom.com/wiki/List_of_Aesthetics"
    # collect_urls(aesthetics_url, 'list.txt')

    # i discovered not all aesthetics were linked from the list of aesthetics page so I had to go to all pages and
    # scrape the aesthetics from there, but it was segmented into pages i cleaned the data by hand to remove
    # duplicates, irrelevant pages, and all header/footer links

    # collect_urls("https://aesthetics.fandom.com/wiki/Special:AllPages", "all_1.txt")
    # collect_urls("https://aesthetics.fandom.com/wiki/Special:AllPages?from=Index+of+Nation-Based+Aesthetics", "all_2.txt")
    # collect_urls("https://aesthetics.fandom.com/wiki/Special:AllPages?from=Traditional+Romainian", "all_3.txt")

    # step 1: getting all the relative urls off the wiki
    # step 2: getting all the relationships between aesthetics
    # related_aesthetics()
    # grab_pictures()
    # compare_sets()
    # image_addresses()
    # kMeansColor()
    # test("https://aesthetics.fandom.com/wiki/Chaotic_Academia", 'chaotic academia')
    colorFix()
    # comparePages("all.txt", "list.txt")
