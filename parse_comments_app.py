import urllib.request
import re
import spacy
from bs4 import BeautifulSoup
from generate_poem import generate_poem

nlp = spacy.load("en_core_web_lg")

chrome_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "sec-ch-ua": "\"Not A(Brand\";v=\"99\", \"Google Chrome\";v=\"121\", \"Chromium\";v=\"121\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "upgrade-insecure-requests": "1",
    "referrer": "https://old.reddit.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}

def parse_results(soup):
    #PUT EACH SEARCH RESULT INTO AN ARRA
    data = soup.find_all(attrs={"class": "search-result-header"})

    URLs = []

    for i in range(len(data)):
        #CONVERT EACH SEARCH RESULT AS USABLE URL
        data[i] = BeautifulSoup(str(data[i]), "html.parser").a["href"]

        #FIND INSTANT WHERE /comments/ IS SPECIFIED IN URL
        f = re.search("/comments/", data[i])

        #MAKE SURE THAT THE URL IS A LINK TO A COMMENTS PAGE
        if(f is not None):
            #ADD URL TO THE ARRAY WITH "+none" INSERTED TO SPECIFY NO CUSTOM CSS
            URLs.append(data[i][0:f.start()] + "+none" + data[i][f.start():])

    return URLs
    
    
regex = re.compile("\s+")

def parse_comments(URLs, dictionary, current_count, target_count):
    for i in URLs:
        #OPEN EACH STORED SEARCH URL
        request = urllib.request.Request(url=i, headers=chrome_headers)

        try:
            response = urllib.request.urlopen(request)
            
            html = response.read()
            
            soup = BeautifulSoup(html, "html.parser")

            #PUT EACH COMMENT INTO AN ARRAY
            comments = soup.find_all("div", {"class":"md"})

            for j in comments:
                #PROCESS EACH COMMENT INTO A READABLE STRING WITHOUT HTML TAGS
                comment = BeautifulSoup(str(j), "html.parser").get_text()

                #ANALYSE COMMENTS
                current_count = count_words(comment, dictionary, current_count)

                #IF THE WORD COUNT HAS EXCEEDED THE TARGET, THEN BREAK THE LOOP
                if(current_count >= target_count):
                    break
                    
                   

        except Exception as inst:
            print(type(inst))
            print(inst.args)
            
            print(inst)

        #IF THE WORD COUNT HAS EXCEEDED THE TARGET, THEN BREAK THE LOOP
        if(current_count >= target_count):
            break
    
    return current_count

def count_words(comment, dictionary, current_count):
    #LOWER-CASE FOR EASINESS
    comment = comment.lower()
    
    comment = re.sub(regex, " ", comment)

    comment = nlp(comment)

    texts = [str(token.text) for token in comment]
    deps = [str(token.dep_) for token in comment]
    tags = [str(token.tag_) for token in comment]

    for i in range(len(comment)):
        #sequence = tuple(tags[i:state_size+i])
        text = texts[i]
        dep = deps[i]
        tag = tags[i]

        if(tag not in dictionary["classes"]):
            dictionary["classes"][tag] = []

        dictionary["classes"][tag].append(text)
        
        tag_index = len(dictionary["classes"][tag])-1
        
        if(dep not in dictionary["dependencies"]):
            dictionary["dependencies"][dep] = {}
            
        if(tag not in dictionary["dependencies"][dep]):
            dictionary["dependencies"][dep][tag] = []

        dictionary["dependencies"][dep][tag].append(tag_index)
        
        current_count += 1

    return current_count

def generate_poem_from_comments(search_term):
    #CREATE NESTED DICTIONARY STRUCTURE FOR EACH OF THE WORD CLASSES
    comment_model = {
        "classes": {},
        "dependencies": {}
    }

    word_count = 0

    target_count = 20000

    #FORMAT SEARCH TERM
    search_term.lower()
    search_term = re.sub("[^\w\s]", "", search_term)
    search_term = re.sub("\s", "+", search_term)

    #INITIAL SEARCH URL
    search_url = "https://old.reddit.com/search/?q="+search_term+"&restrict_sr=&sort=relevance&t=all"

    while(word_count < target_count):
        URLs = []
        
        request = urllib.request.Request(url=search_url, headers=chrome_headers)
        response = urllib.request.urlopen(request)
        html = response.read()

        soup = BeautifulSoup(html, "html.parser")

        #PARSE THE URL OF THE RESULTS
        URLs = parse_results(soup)

        #PARSE THE COMMENTS
        word_count = parse_comments(URLs, comment_model, word_count, target_count)

        #"CLICK" NAV BUTTON. THE BUTTON SHOULD BE LAST IN THE ARRAY
        nav_button = soup.find_all(attrs={"rel": "nofollow next"})

        #IF THERE ARE NO MORE PAGES TO LOAD, THEN BREAK THE LOOP
        if(len(nav_button) == 0):
            print("No more results to load. Check that there are no spelling mistakes in your search term")
            
            return None
            
            break

        #UPDATE PARSER IF TARGET COUNT HAS NOT BEEN EXCEEDED
        search_url = BeautifulSoup(str(nav_button[-1]), "html.parser").a["href"]

    for i in comment_model:
        print(i)
        print(comment_model[i])
        
    poem = generate_poem(comment_model)
    
    return poem