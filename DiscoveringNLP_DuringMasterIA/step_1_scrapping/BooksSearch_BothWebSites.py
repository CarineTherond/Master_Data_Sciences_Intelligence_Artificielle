import sys
cheminMonGitHub = 'D:/DocsDeCara/Boulot/IA_ML/MonGitHub/repBooksProjet/Books_project/WebScrapper/'
sys.path.append(cheminMonGitHub)
    
import Parser_csv_BooksList as P
import BooksSearch_GoodReads as GR
import BooksSearch_Google as G
    
import pandas as pd
import requests
from urllib.request import urlopen
import bs4
import re
import warnings


def GoodReadsPartialSearchFunction(isbn =  None):
    """ Additional scrapping performed on GoodReads web site,
        in case where a first scrapping has been successfully performed on GoogleBooks
        (as not all the expected books information are on GoogleBooks)
    """

    #Reset of scrapping results
    awardsSearched = ''
    authorGenreSearched = ''
    goodreadsLinksSeriesList = []
    avgRating = ""

    ISBNfound = False
    
    try:
        #GoodReads URL to find a book thanks to its ISBN
        #=> We have to format the ISBN so that it is written on 10 digits => {0:0>10s}
        urlIdBookGoodReads_start = "https://www.goodreads.com/search?q={0:0>10s}".format(isbn)
        urlIdBookGoodReads_end = '&qid='
        bookUrlForSearch = urlIdBookGoodReads_start + urlIdBookGoodReads_end
        
        #Web page where to find information on book linked to this ISBN
        source = urlopen(bookUrlForSearch)
        #'bookTitle' is searched in order to recognise a relevant page
        soup = bs4.BeautifulSoup(source, 'html.parser')
        ISBNfound = (soup.find("h1", id="bookTitle") != None)


        #Now we are on the specific book's web page: additional information are searched
        if ISBNfound:
            #Additional feature searched : average rating of the book
            if soup.find("span", itemprop="ratingValue"):
                avgRating = soup.find("span", itemprop="ratingValue").text.strip()

            #Additional feature searched : awards
            searchForISBN_Lang_Awards_Series = soup.find("div", id="bookDataBox").find_all("div", class_="clearFloats")
            for i in range(len(searchForISBN_Lang_Awards_Series)):
                if searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowTitle").text == 'Literary Awards':
                    awardsSearched = searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowItem").text.strip()

                #Additional feature searched : language
                if searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowTitle").text == 'Edition Language':
                    languageSearched = searchForISBN_Lang_Awards_Series[i].find("div", "infoBoxRowItem").text
                    #In order to be compliant with GoogleBooks names
                    if (languageSearched == 'English'):
                        languageSearched = 'en'
    
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
            sourceAuthor = urlopen(soup.find("a", class_="authorName")["href"])
            soupAuthor = bs4.BeautifulSoup(sourceAuthor, 'html.parser')
            
            #On the author web site page, we search for the author genre
            searchForAuthorGenre = soupAuthor.find_all("div", class_="dataTitle")
            for i in range(len(searchForAuthorGenre)):
                if (searchForAuthorGenre[i].text == "Genre"):
                    authorGenreSearched = searchForAuthorGenre[i].find_next("div", class_="dataItem").text.split(',')[0]
                    authorGenreSearched = authorGenreSearched.replace('\n', '').strip()
    
    
        return (ISBNfound, [awardsSearched, authorGenreSearched, goodreadsLinksSeriesList, avgRating])
    
    except:
        #In case where an exception occurs, the reset values are returned
        return (False, [awardsSearched, authorGenreSearched, goodreadsLinksSeriesList, avgRating])    
    


def internetSearch(f, SaveFileName, theColumns, ind_start, ind_end, Re = False):
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
    
    #Number of f lines not completed thanks to this scrapping (information not found on the web)
    NotFoundBooks_ind = 0   
    #Current f line indicator : complementary information found or not on the web
    NotFoundBooks_bool = True
    
    #Information scrapped will be saved in this dataframe
    pdT = pd.DataFrame(columns = theColumns)

    #The file must be read only from ind_start
    for i in range(0, ind_start-1): 
        f.readline()
        
    #1st line of f to be completed
    #Information of line must be correctly read
    csvLineParsed = P.ParserCsvInputBookCrossing(f.readline(), Re)
    #Scrapping on Google Book web site
    ret, refBookGoogle = G.GoogleSearchFunction(isbn = csvLineParsed[0])
    #Information scrapped saved inside dataframe
    pdT.loc[0] = refBookGoogle 
    #Line of f which has been completed is written inside another file
    pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'w')
    
    #Following lines of f to be completed
    for i in range(ind_start+1, ind_end):    
        #Defaults status of the 3 different steps of scrapping
        retGoogle = False
        retGoodReads = False
        retPartial = False

        lili = f.readline()
        #Information of line must be correctly read
        csvLineParsed = P.ParserCsvInputBookCrossing(lili, Re)
        
        #First we use Google Books web site: 1st scrapping step = search fastest
        retGoogle, refBookGoogle = G.GoogleSearchFunction(isbn = csvLineParsed[0])
        
        if (retGoogle == False):

            #if ISBN not found on Google Books, we try on Google Reads (2nd scrapping step)
            retGoodReads, refBookGoodReads = GR.GoodReadsSearchFunction(isbn = csvLineParsed[0])
            
            if (retGoodReads == False):
                #if ISBN not found (on Google Books and on Good Reads), 
                #we try search on GoodReads only a search with title and author(3rd scrapping step)
                retGoodReads, refBookGoodReads = GR.GoodReadsSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
                
                if (retGoodReads == True):
                    #A unique reference for all scrapping steps  (3rd scrapping step succeded)
                    refBook = refBookGoodReads
                    NotFoundBooks_bool = False
                else:
                    #None of the 3 scrapping steps worked
                    NotFoundBooks_ind += 1
            else:
                #A unique reference for all scrapping steps (2nd scrapping step succeded)
                refBook = refBookGoodReads
                NotFoundBooks_bool = False
                
        else:
            #A unique reference for all scrapping steps (1st scrapping step succeded)
            refBook = refBookGoogle
            NotFoundBooks_bool = False
            
            #If ISBN found on Google Books, we even so complete some columns with GoodReads search
            retPartial, refBookPartial = GoodReadsPartialSearchFunction(isbn = csvLineParsed[0])
            if (retPartial == True):
                #previous refBook is then completed with the GoodReads information
                refBook[-4:] = refBookPartial

        if NotFoundBooks_bool != True:
            #Information scrapped saved inside dataframe
            pdT.loc[0] = refBook
            #Line of f which has been completed is written inside another file
            pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'a', header = False)
            NotFoundBooks_bool = True

        
    return NotFoundBooks_ind



    
if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.warn("Let this be your last warning")
        warnings.simplefilter("ignore")

        #path toward BookCrossing original database (the one to be completed)
        cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_nonStats\Projet\Donnees\GoodBooks\goodbooks-10k-master\goodbooks-10k-master/'
        cheminBookCrossing = cheminBookCrossing.replace('\\', '/')

        #path toward file on which scrapping results are saved
        cheminCommon = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_nonStats\Projet\Donnees/'
        cheminCommon = cheminCommon.replace('\\', '/')
        SaveFileName = cheminCommon + 'bothWebSites_InternetSearch_25_01_2021.csv'

        #Missing (inside BookCrossing database) books information to retrieve thanks to scrapping
        theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', \
                            'Year-Of-Publication', 'Publisher', 'Category', 'Description', 'Language', \
                            'Image', 'Pages', 'Awards', "Author's genre", 'Same serie', 'average_rating']
    
        #List of books to search on Google
        f = open(cheminBookCrossing + 'books.csv', encoding="utf8", errors="replace")
        f.readline()
        
        #Google search function
        NotFoundBooks = internetSearch(f, SaveFileName, theColumns, 0, 10, Re = True) 
    
        print("Not found books: %d" % NotFoundBooks)
        f.close()   
    
    
 
