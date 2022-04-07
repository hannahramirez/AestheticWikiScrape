import requests
from bs4 import BeautifulSoup


def collect_urls(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    with open("aesthetics.txt", "w") as aesthetics:
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
                url = fin.readline().strip()

                # goes through the list of relative urls
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
                    titles = soup.find_all(attrs={'data-source': 'title1'})
                    related = soup.find_all(attrs={'data-source': 'related_aesthetics'})

                    # print(related)
                    # iterate through the list of titles and related aesthetics
                    for t, r in zip(titles, related):
                        # get the name of the aesthetic page
                        name = t.get_text()
                        # this was me writing a node list in case I needed it
                        # but I didn't end up need it
                        nodes.write(relative_path + "," + name + "\n")

                        # printing so I know how far in the list I am
                        print(name)

                        # finds all the hyperlinks of the related aesthetic
                        a_tags = r.find_all('a')
                        for a in a_tags:
                            # writes the adjacency list
                            # format: aesthetic,related aesthetic
                            edges.write(name + "," + a.get_text() + "\n")


if __name__ == "__main__":
    aesthetics_url = "https://aesthetics.fandom.com/wiki/List_of_Aesthetics"
    # step 1: getting all the relative urls off the wiki
    # collect_urls(aesthetics_url)
    # step 2: getting all the relationships between aesthetics
    related_aesthetics()
