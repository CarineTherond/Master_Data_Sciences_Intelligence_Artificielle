import sys
cheminMonGitHub = 'D:/DocsDeCara/Boulot/IA_ML/MonGitHub/repBooksProjet/Books_project/WebScrapper/'
sys.path.append(cheminMonGitHub)
    
import Parser_csv_BooksList as P

import pandas as pd
import re
import time
import requests
from urllib.request import urlopen
import bs4
   

def GoodReadsSearchFunction(isbn = None, title = None, author = None):
    ''' Find information on internet about the book entered in function's arguments 
        Either isbn = ..., Or title = ..., author = ... '''
    
    #3 kinds of books identifiers
    ISBNdict = {"ISBN_10": 0, "ISBN_13": 0, "OtherID": 0}
    
    #Reset of scrapping results
    ISBNdict["ISBN_10"] = ""
    ISBNdict["ISBN_13"] = ""   
    ISBNdict["OtherID"] = ""
    autGoodReads = ''
    titleSearched = ''
    autSearched = ''
    pubSearched = ''
    pubData = ''
    catSearched = ''
    descSearched = ''
    awardsSearched = ''
    languageSearched = ''
    pagesSearched = 0
    authorGenreSearched = ''
    goodreadsLinksSeriesList = []
    avgRating = ""

    AUTHORfound = False
    ISBNfound = False
    
    try:
        #Information on a book is searched thanks to its ISBN
        if(isbn is not None):
            ISBNdict["ISBN_10"] = isbn
    
            #GoodReads URL to find a book thanks to its ISBN
            #=> We have to format the ISBN so that it is written on 10 digits => {0:0>10s}
            urlIdBookGoodReads_start = "https://www.goodreads.com/search?q={0:0>10s}".format(ISBNdict["ISBN_10"])
            urlIdBookGoodReads_end = '&qid='
            bookUrlForSearch = urlIdBookGoodReads_start + urlIdBookGoodReads_end
            
            #Web page where to find information on book linked to this ISBN
            source = urlopen(bookUrlForSearch)
            #'bookTitle' is searched in order to recognise a relevant page
            soup = bs4.BeautifulSoup(source, 'html.parser')
            ISBNfound = (soup.find("h1", id="bookTitle") != None)

        #Information on a book is searched thanks to its title & author
        else:    
            if ((title != None) and (author != None)):
                #GoodReads URL to find a book thanks to its title & author
                urlIdBookGoodReads_start = 'https://www.goodreads.com/search?utf8=%E2%9C%93&q='
                urlIdBookGoodReads_end = '&search_type=books'
                
                titleSearched = title.encode('ascii', 'ignore').decode('ascii')
                autSearched = author.encode('ascii', 'ignore').decode('ascii')
                #We keep only the author familly name
                autSearchedInternal = autSearched.lower().split()[-1]
                
                bookUrlForSearch = urlIdBookGoodReads_start + titleSearched.replace(' ', '+') + '+' + autSearchedInternal.replace(' ', '+') + urlIdBookGoodReads_end

                #Web page where to find information on book linked to this title & author
                sourceIdBookGoodReads = urlopen(bookUrlForSearch)
                soupIdBookGoodReads = bs4.BeautifulSoup(sourceIdBookGoodReads, 'html.parser')
                
                #First we have to find the book page: we need GoodReads identifier of the book 
                #Search of the reference compliant with title and author provided, among all proposed books references
                booksReference = soupIdBookGoodReads.find_all("a", class_="bookTitle")
                j = 0
                #Title is correctly found, but author is not always the correct one: a check is needed
                while ((j < len(booksReference)) and (AUTHORfound == False)):
                    autGoodReads = booksReference[j].find_next("a", class_="authorName").text
                    
                    if (autSearchedInternal in autGoodReads.lower()):
                        AUTHORfound = True
                    j += 1    
                
                #Now we go to the selected book's page
                if (AUTHORfound == True):
                    source = urlopen('https://www.goodreads.com' + booksReference[j-1]["href"]) 
                    soup = bs4.BeautifulSoup(source, 'html.parser')
                    ISBNfound = True

        #Now we are on the specific book's web page: additional information are searched
        #ISBN or title/author has been recognized on Google Books
        if ISBNfound:
            #Additional feature searched : rating of the book
            if soup.find("span", itemprop="ratingValue"):
                avgRating = soup.find("span", itemprop="ratingValue").text.strip()

            #Additional feature searched : correct title inside GoodReads
            titleSearched = soup.find("h1", id="bookTitle").text
            titleSearched = titleSearched.replace('\n', '').strip()
            
            #Search of ISBN (10 and / or 13), language and awards => same web parser on the web page
            searchForISBN_Lang_Awards = soup.find("div", id="bookDataBox").find_all("div", class_="clearFloats")
            #But now, the different information (ISBN, language, awards & serie) need to be sorted  
            for i in range(len(searchForISBN_Lang_Awards)):
                
                #Additional feature searched : all ISBN values are searched
                if searchForISBN_Lang_Awards[i].find("div", "infoBoxRowTitle").text == 'ISBN':
                    isbnFull = searchForISBN_Lang_Awards[i].find("div", "infoBoxRowItem")
                    
                    #ISBN_10 and ISBN_13 are provided
                    if isbnFull.find("span", class_="greyText"):
                        ISBNdict["ISBN_10"] = isbnFull.text.split(isbnFull.find("span", class_="greyText").text)
                        ISBNdict["ISBN_10"] = ISBNdict["ISBN_10"][0].replace('\n', '').strip()
                        ISBNdict["ISBN_13"] = isbnFull.find("span", class_="greyText").text
                        ISBNdict["ISBN_13"] = ISBNdict["ISBN_13"].split('(ISBN13: ')[1].replace(")", '')
                    #Only ISBN_10 is provided
                    else:
                        ISBNdict["ISBN_10"] = isbnFull.text

                #Additional feature searched : language
                if searchForISBN_Lang_Awards[i].find("div", "infoBoxRowTitle").text == 'Edition Language':
                    languageSearched = searchForISBN_Lang_Awards[i].find("div", "infoBoxRowItem").text
                    #In order to be compliant with GoogleBooks names
                    if (languageSearched == 'English'):
                        languageSearched = 'en'
            
                #Additional feature searched : awards
                if searchForISBN_Lang_Awards[i].find("div", "infoBoxRowTitle").text == 'Literary Awards':
                    awardsSearched = searchForISBN_Lang_Awards[i].find("div", "infoBoxRowItem").text
                    awardsSearched = awardsSearched.strip()
            
            #Additional feature searched : published date and publisher => same web parser on the web page      
            searchForPublished = soup.find("div", id="details").find_all("div", class_="row")
            for i in range(len(searchForPublished)):
                if 'Published' in searchForPublished[i].text:
                    #Current published date and additional information on first publication date is also provided
                    if (searchForPublished[i].find("nobr", class_="greyText")):
                        infoFirstPublished = searchForPublished[i].find("nobr", class_="greyText")
                        tempPublished = searchForPublished[i].text.split(infoFirstPublished.text)
                        tempPublished = tempPublished[0].strip().replace('\n', '').replace('Published', '').split('by')
                        pubData = tempPublished[0].strip()
                        pubData = re.search("[0-9]{4,4}", pubData)[0]
                        pubSearched = tempPublished[1].strip()
                    #Only current published date is provided
                    else:
                        tempPublished = searchForPublished[i].text.strip().replace('\n', '').replace('Published', '').split('by')
                        pubData = tempPublished[0].strip()
                        pubData = re.search("[0-9]{4,4}", pubData)[0]
                        pubSearched = tempPublished[1].strip()

            #Additional feature searched : pages number
            searchForPages = soup.find("div", id="details").find_all("div", class_="row")
            for i in range(len(searchForPages)):
                if 'pages' in searchForPages[i].text:
                    pagesSearched = searchForPublished[i].text
                    pagesSearched = pagesSearched.split(',')[-1].split('pages')[0].strip()
        
            #Additional feature searched : book's category
            if (soup.find("a", class_="actionLinkLite bookPageGenreLink")):
                catSearched = soup.find_all("a", class_="actionLinkLite bookPageGenreLink")[0].text
            
            #Additional feature searched : search for knowing if book is part of a serie
            #=> If yes, we keep the URL of the other mentionned books of the serie
            if soup.find("div", class_="seriesList"):
                if (soup.find("div", class_="seriesList").find_next("h2").text == 'Other books in the series'):
                    #We go to this specific book serie web page
                    linkTowardSeries = soup.find("div", class_="seriesList").find_next("h2").find_next("a")["href"]
                    r = requests.get('https://www.goodreads.com' + linkTowardSeries)
                    
                    #We keep all the other books reference of this serie
                    seriesList = re.findall('href="/book/show/[0-9]+', str(r.content))
                    goodreadsLinksSeriesList = [seriesList[i].replace('href="', 'https://www.goodreads.com') for i in range(len(seriesList)) if i%2 == 0]
        
            #Additional feature searched : author genre
            #we need to find the URL of author page first
            autSearched = soup.find("a", class_="authorName").text
            sourceAuthor = urlopen(soup.find("a", class_="authorName")["href"])
            soupAuthor = bs4.BeautifulSoup(sourceAuthor, 'html.parser')
            
            #On the author web site page, we search for the author genre
            searchForAuthorGenre = soupAuthor.find_all("div", class_="dataTitle")
            for i in range(len(searchForAuthorGenre)):
                if (searchForAuthorGenre[i].text == "Genre"):
                    authorGenreSearched = searchForAuthorGenre[i].find_next("div", class_="dataItem").text.split(',')[0]
                    authorGenreSearched = authorGenreSearched.replace('\n', '').strip()
    
        return (ISBNfound, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                pubData, pubSearched, catSearched, descSearched, languageSearched, '', pagesSearched, awardsSearched, \
                authorGenreSearched, goodreadsLinksSeriesList, avgRating])
    
    except:
        #In case where an exception occurs, the reset values are returned
        return (False, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                pubData, pubSearched, catSearched, descSearched, languageSearched, '', pagesSearched, awardsSearched, \
                authorGenreSearched, goodreadsLinksSeriesList, avgRating])    


def GoodReadsSearch(f, SaveFileName, theColumns, ind_start, ind_end, Re = False):
    """ Lines (books partial information) inside f must be completed thanks to scrapping
        Inputs :
            f                 file identifier, file in which books ISBN, title or author are read
            SaveFileName      file path in which save the scr&apping results
            theColumns        names of information to find thanks to scrapping
            ind_start         line to start reading f
            ind_end           line to stop reading f
            Re                boolean indicating whether a specific parsing must be used to retrieve SBN, title or author from f
        Outputs:
            number of books not completed among ind_start - ind_end lines of f
    """

    #Number of f lines not completed thanks to scrapping (information not found on the web)
    NotFoundBooks = 0    
    #Information scrapped will be saved in this dataframe
    pdT = pd.DataFrame(columns = theColumns)

    #The file must be read only from ind_start
    for i in range(0, ind_start-1): 
        f.readline()
    
    #1st line of f to be completed
    #Information of line must be correctly read
    csvLineParsed = P.ParserCsvInputBookCrossing(f.readline(), Re)
    #Scrapping on GoodReads web site
    ret, refBook = GoodReadsSearchFunction(isbn = csvLineParsed[0])
    #Information scrapped saved inside dataframe
    pdT.loc[0] = refBook
    #Line of f which has been completed is written inside another file
    pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'w')

    #Following lines of f to be completed
    for i in range(ind_start+1, ind_end):  
        
        #Information of line must be correctly read
        csvLineParsed = P.ParserCsvInputBookCrossing(f.readline(), Re)
        
        #Defaults status of scrapping
        ret = False
        #Scrapping thanks to book's ISBN
        ret, refBook = GoodReadsSearchFunction(isbn = csvLineParsed[0])
        
        if (ret == False):
            #No information has been found thanks to book's ISBN
            #So a 2nd search is performed thanks to book's title & author
            ret, refBook = GoodReadsSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
            
        if (ret == False):
            #No information has been found thanks with the 2 previous scrapping
            NotFoundBooks += 1

        #Information scrapped saved inside dataframe
        pdT.loc[0] = refBook
        #Line of f which has been completed is written inside another file
        pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'a', header = False)
        
    return NotFoundBooks


    
if __name__ == "__main__":
    
#Example of GoodReads Requests:
############################
    #Direct search on the GoodReads web site with title 'Jane Doe' and author name 'Kaiser'
    #=> the URL used it then: 'https://www.goodreads.com/search?utf8=%E2%9C%93&q=jane+doe+kaiser&search_type=books'

    #On the html code of the previous direct search, there are: <div id="1730953" and <div id="9675352" 
    #=> It's GoodReads book's identifiers 

    #=> Then with the following request, we are on the book web page : 'https://www.goodreads.com/book/show/1730953'
    
    #Example of book with 'Literary Awards': The Millionaire Next Door: The Surprising Secrets of America's Wealthy 
    #=> 'https://www.goodreads.com/book/show/998'

    #Example of book inside a serie: Asterix the Gaul
    #=> direct search: https://www.goodreads.com/search?utf8=%E2%9C%93&search%5Bquery%5D=asterix+the+gaulois&commit=Search&search_type=books
    #=> URL of GoodReads book's page: 'https://www.goodreads.com/book/show/71292'
    
#Search result
############################
    #path toward BookCrossing original database (the one to be completed)
    cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_nonStats\Projet\Donnees\BookCrossing/'
    cheminBookCrossing = cheminBookCrossing.replace('\\', '/')
    
    #path toward file on which scrapping results are saved
    cheminGoodReads = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_nonStats\Projet\Donnees\GoodReads/'
    cheminGoodReads = cheminGoodReads.replace('\\', '/')
    SaveFileName = cheminGoodReads + 'bothWebSites_InternetSearch_25_01_2021.csv'

    #Missing (inside BookCrossing database) books information to retrieve thanks to scrapping
    theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', \
                        'Year-Of-Publication', 'Publisher', 'Category', 'Description', 'Language', \
                        'Image', 'Pages', 'Awards', "Author's genre", 'Same serie', 'average_rating']
    
    #List of books to search on Google
    f = open(cheminBookCrossing + 'Extrait1000_BX-Books.csv', encoding="utf8", errors="replace")
    f.readline()
    
    #Google search function
    NotFoubndBooks = GoodReadsSearch(f, SaveFileName, theColumns, 0, 2, Re = True) 

    print("Not found books: %d" % NotFoubndBooks)
    f.close()   



