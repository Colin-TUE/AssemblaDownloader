import requests
import json
import os
import config

# Basic values
headers = {'X-API-Key': config.key, 'X-API-Secret': config.secret}
basicurl = 'https://api.assembla.com/v1/'
spaceurl = basicurl + 'spaces.json'


# Returns the url of the document list for space {@code space}
def docsurl(space):
    return basicurl + 'spaces/' + space + '/documents.json'


# Returns the url for the location of the file {@code docid} in space {@code space}
def locationurl(space, docid):
    return basicurl + 'spaces/' + space + '/documents/' + docid + '/download.json'


# Returns the url for the wiki list for space {@code space}
def wikisurl(space):
    return basicurl + ' spaces/' + space + '/wiki_pages.json'


# Returns the url of the specific wiki with id {@code id} in space {@code space}
def wikiurl(space, wikiid):
    return basicurl + ' spaces/' + space + '/wiki_pages/' + wikiid + '.json'


# Makes sure the directory exists
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


# First we fetch all spaces from this user
spaces_req = requests.get(spaceurl, headers = headers)
spaces_json = json.loads(spaces_req.text)

# Print each of the spaces and ask which to download from
for i in range(len(spaces_json)):
    print(str(i) + ": " + spaces_json[i]['name'])

picked = -1
while picked < 0 or picked >= len(spaces_json):
    picked = int(input("Which space to download documents from?"))

space_id = picked

#Print choice for selection of file type
print(str(0) + ": Documents")
print(str(1) + ": Wiki pages")

picked = -1
while picked < 0 or picked >= 2:
    picked = int(input("Which type of files to download?"))

file_type_picked = picked

if(file_type_picked is 0):
    # Then download all files from that space
    j = 1
    space = spaces_json[space_id]['id']
    download_doc_location = config.download_dir + spaces_json[space_id]['name'] + "/Documents"
    ensure_dir(download_doc_location)
    docs_req = requests.get(docsurl(space), headers = headers, params = {'per_page': 10, 'page': j})
    try:
        docs_json = json.loads(docs_req.text)
    except json.decoder.JSONDecodeError as e:
        print("No files to download at all:")
        docs_json = []

    while len(docs_json) is not 0:
        for i in range(len(docs_json)):
            # print("Downloading: " + docs_json[i]['name'])
            # actually download file
            with open(download_doc_location + docs_json[i]['name'], 'wb') as handle:
                response = requests.get(locationurl(space, docs_json[i]['id']), stream = True,
                                        headers = headers)
                if not response.ok:
                    # Something went wrong
                    print("Cannot download file: " + docs_json[i]['name'])
                for block in response.iter_content(1024):
                    handle.write(block)

        # got to next page in possible
        j += 1
        docs_req = requests.get(docsurl(space), headers = headers, params = {'per_page': 10, 'page': j})
        try:
            docs_json = json.loads(docs_req.text)
        except json.decoder.JSONDecodeError as e:
            print("No more files to download:")
            docs_json = []
    print("Finished downloading files to " + download_doc_location)

elif(file_type_picked is 1):
    # Then download all wikis from that space
    j = 1
    space = spaces_json[space_id]['id']
    download_wiki_location = config.download_dir + spaces_json[space_id]['name'] + "/Wiki"
    ensure_dir(download_wiki_location)
    wiki_req = requests.get(wikisurl(space), headers = headers, params = {'per_page': 10,
                                                                          'page': j})
    try:
        wiki_json = json.loads(wiki_req.text)
        #TODO: fix this and check why there are no wiki pages
    except json.decoder.JSONDecodeError as e:
        print("No files to download at all:")
        wiki_json = []

    while len(wiki_json) is not 0:
        for i in range(len(wiki_json)):
            # print("Downloading: " + docs_json[i]['name'])
            # actually download file

            #TODO: add parent directories here for structure

            with open(download_wiki_location + wiki_json[i]['page_name'], 'w') as handle:
                response = requests.get(wikiurl(space, wiki_json[i]['id']), stream = True,
                                        headers = headers)
                if not response.ok:
                    # Something went wrong
                    print("Cannot download wiki: " + wiki_json[i]['page_name'])
                else:
                    handle.write(wiki_json['contents'])

        # got to next page in possible
        j += 1
        docs_req = requests.get(docsurl(space), headers = headers, params = {'per_page': 10, 'page': j})
        try:
            wiki_json = json.loads(wiki_req.text)
        except json.decoder.JSONDecodeError as e:
            print("No more files to download:")
            wiki_json = []
    print("Finished downloading files to " + download_wiki_location)
