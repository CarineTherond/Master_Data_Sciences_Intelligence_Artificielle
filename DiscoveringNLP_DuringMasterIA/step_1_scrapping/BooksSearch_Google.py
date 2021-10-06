import sys
cheminMonGitHub = 'D:/DocsDeCara/Boulot/IA_ML/MonGitHub/repBooksProjet/Books_project/WebScrapper/'
sys.path.append(cheminMonGitHub)
    
import Parser_csv_BooksList as P
    
import pandas as pd
import time
import re


def GoogleSearchFunction(isbn = None, title = None, author = None):
    ''' Find information on internet about the book entered in function's arguments 
        Either isbn = ..., Or title = ..., author = ... '''
    
    #3 kinds of books identifiers
    ISBNdict = {"ISBN_10": 0, "ISBN_13": 0, "OtherID": 0}
    
    #Reset of scrapping results
    ISBNdict["ISBN_10"] = ""
    ISBNdict["ISBN_13"] = ""   
    ISBNdict["OtherID"] = ""
    autGoogle = []
    titleSearched = ''
    autSearched = ''
    pubSearched = ''
    pubData = ''
    catSearched = ''
    descSearched = ''
    langSearched = ''
    imageSearched = ''
    pageSearched = 0

    ISBNfound = False
    AUTHORfound = False
    repGoogle = ''
    
    try:
        #Information on a book is searched thanks to its ISBN_10
        if (isbn is not None):
            
            ISBNdict["ISBN_10"] = isbn

            #Request format for a search on Google Book web site
            #=> We have to format the ISBN so that it is written on 10 digits => {0:0>10s}
            requeteIsbnGoogle = "https://www.googleapis.com/books/v1/volumes?q=isbn:{0:0>10s}".format(ISBNdict["ISBN_10"])
    
            try:
                #In case where a book reference has been found: information is returned as a json file
                repGoogle = pd.read_json(requeteIsbnGoogle)
                ISBNfound = True
            except:
                #In case where a book reference has NOT been found                
                repGoogle = pd.read_json(requeteIsbnGoogle, typ = 'series')
                ISBNfound = False
            
        
        #Information on a book is searched thanks to its title & author
        else:
            if ((title != None) and (author != None)):

                titleSearched = title.encode('ascii', 'ignore').decode('ascii')
                autSearched = author.encode('ascii', 'ignore').decode('ascii')
                #We keep only the author familly name
                autSearchedInternal = autSearched.lower().split()[-1]
                
                #Request format for a search on Google Book web site
                #=> We must take care of ' (replace('\'', '')) and space (replace(' ','%20'))
                requeteTitleGoogle = "https://www.googleapis.com/books/v1/volumes?q=title:%s" % (titleSearched.replace('\'', '').replace(' ','%20'))
                
                #Information is returned as a json file
                repGoogle = pd.read_json(requeteTitleGoogle) 
                
                #The Title has been found on Google Books
                #We only analyse the first book's reference retrieved => repTitleGoogle['items'][0]
                if (repGoogle['totalItems'][0] != 1):
    
                    if ('authors' in repGoogle['items'][0]['volumeInfo']):
                        
                        #All authors proposed by Google
                        autGoogle = repGoogle['items'][0]['volumeInfo']['authors']
                        
                        #Among all authors proposed by Google, we search correspondance with the first provided author
                        j = 0
                        while ((j < len(autGoogle)) and (AUTHORfound == False)):
                            
                            if (autSearchedInternal in autGoogle[j].lower()):
                                AUTHORfound = True  
                                ISBNfound = True
                                
                            j += 1

        #ISBN or title/author has been recognized on Google Books
        if (ISBNfound == True):
            #Additional feature searched : correct title inside Google Books
            titleSearched = repGoogle['items'][0]['volumeInfo']['title']
            
            #Additional feature searched : subtitles
            if 'subtitle' in repGoogle['items'][0]['volumeInfo']:
                titleSearched = titleSearched + ' : ' + repGoogle['items'][0]['volumeInfo']['subtitle']
            
            #Additional feature searched : all provided ISBN values
            #'industryIdentifiers' stands for ISBN_10, ISBN_13 or OtherID
            if ('industryIdentifiers' in repGoogle['items'][0]['volumeInfo']):
                
                #Among all identifiers type proposed by Google, we search "ISBN_10", "ISBN_13" or "OtherID"
                for k in range(len(repGoogle['items'][0]['volumeInfo']['industryIdentifiers'])):
                    
                    if repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_10":
                        ISBNdict["ISBN_10"] = repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                        #print("ISBN 10", ISBNdict["ISBN_10"], type(ISBNdict["ISBN_10"]))
                        ISBNfound = True
                        
                    elif repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['type'] == "ISBN_13":
                        ISBNdict["ISBN_13"] = repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                        #print("ISBN 13", ISBNdict["ISBN_13"], type(ISBNdict["ISBN_13"]))
                        ISBNfound = True
                        
                    else:
                        ISBNdict["OtherID"] = repGoogle['items'][0]['volumeInfo']['industryIdentifiers'][k]['identifier']
                        ISBNfound = True

            #Additional feature searched : correct author name
            if ('authors' in repGoogle['items'][0]['volumeInfo']):
                autSearched = repGoogle['items'][0]['volumeInfo']['authors'][0]
                
            #Additional feature searched : publisher
            if ('publisher' in repGoogle['items'][0]['volumeInfo']):
                pubSearched = repGoogle['items'][0]['volumeInfo']['publisher']
                                    
            #Additional feature searched : year
            if ('publishedDate' in repGoogle['items'][0]['volumeInfo']):
                pubData = repGoogle['items'][0]['volumeInfo']['publishedDate']
                pubData = re.search("[0-9]{4,4}", pubData)[0]

            #Additional feature searched : book's category
            if ('categories' in repGoogle['items'][0]['volumeInfo']):
                catSearched = repGoogle['items'][0]['volumeInfo']['categories'][0]

            #Additional feature searched : book's description
            if ('searchInfo' in repGoogle['items'][0]):
                descSearched = repGoogle['items'][0]['searchInfo']['textSnippet']                    

            #Additional feature searched : language
            if ('language' in repGoogle['items'][0]['volumeInfo']):
                langSearched = repGoogle['items'][0]['volumeInfo']['language']

            #Additional feature searched : book's image
            if ('imageLinks' in repGoogle['items'][0]['volumeInfo']):
                imageSearched = repGoogle['items'][0]['volumeInfo']['imageLinks']['smallThumbnail']

            #Additional feature searched : number of page
            if ('pageCount' in repGoogle['items'][0]['volumeInfo']):
                pageSearched = repGoogle['items'][0]['volumeInfo']['pageCount']

        return (ISBNfound, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                           pubData, pubSearched, catSearched, descSearched, langSearched, imageSearched, pageSearched, '', '', '', ''])

    except:
        #In case where an exception occurs, the reset values are returned
        return (False, [ISBNdict["ISBN_10"], ISBNdict["ISBN_13"], ISBNdict["OtherID"], titleSearched, autSearched, \
                           pubData, pubSearched, catSearched, descSearched, langSearched, imageSearched, pageSearched, '', '', '', ''])



def GoogleSearch(f, SaveFileName, theColumns, ind_start, ind_end, Re = False):
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
    #Scrapping on Google book web site
    ret, refBook = GoogleSearchFunction(isbn = csvLineParsed[0])
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
        ret, refBook = GoogleSearchFunction(isbn = csvLineParsed[0])
        
        if (ret == False):
            #No information has been found thanks to book's ISBN
            #So a 2nd search is performed thanks to book's title & author
            ret, refBook = GoogleSearchFunction(title = csvLineParsed[1], author = csvLineParsed[2].split(';')[-1])
        
        if (ret == False):
            #No information has been found thanks with the 2 previous scrapping
            NotFoundBooks += 1

        #Information scrapped saved inside dataframe
        pdT.loc[0] = refBook
        
        #Line of f which has been completed is written inside another file
        pdT.loc[0:1].to_csv(SaveFileName, sep = ';', index = False, mode = 'a', header = False)

        #Google doesn't like when too much requests are performed...
        #time.sleep(10.0)
    
    return NotFoundBooks



    
if __name__ == "__main__":
#Example of Google Requests:
############################
    #'Classical Mythology' found with ISBN - no subtitle - ISBN found: https://www.googleapis.com/books/v1/volumes?q=isbn:0195153448
    
    #'Flu' found with ISBN - with subtitle - ISBN found: https://www.googleapis.com/books/v1/volumes?q=isbn:0374157065
    
    #'Pride and Prejudice' NOT found with ISBN:https://www.googleapis.com/books/v1/volumes?q=isbn:055321215X
    # => found with title - Other identifier than isbn: https://www.googleapis.com/books/v1/volumes?q=title:Pride%20and%20Prejudice
    
    #'Jogn Doe' NOT found with IBBN: https://www.googleapis.com/books/v1/volumes?q=isbn:1552041778
    # => found with title : https://www.googleapis.com/books/v1/volumes?q=title:Jane%20Doe
    # => But author on Google is wrong, so book considered as NOT FOUND
    
    #'Beloved (Plume Contemporary Fiction)' NOT found with ISBN: https://www.googleapis.com/books/v1/volumes?q=isbn:0452264464
    # => Several references found with title: https://www.googleapis.com/books/v1/volumes?q=title:Beloved%20(Plume%20Contemporary%20Fiction)
    # => But those references are not the one searched (but only the first reference is used), so book considered as NOT FOUND

    #Problem with unknown characters, for example 'title = Die Mars- Chroniken. Roman in Erz?¤hlungen' triggers exception 
    #Exception: ('There is un problem: ', UnicodeEncodeError('ascii', 'GET /books/v1/volumes?q=title:Die%20Mars-%20Chroniken.%20Roman%20in%20Erz?¤hlungen. HTTP/1.1', 74, 75, 'ordinal not in range(128)'))
    #=> The solutyion is title.encode('ascii', 'ignore').decode('ascii') = Die Mars- Chroniken. Roman in Erz?hlungen

    #'PLEADING GUILTY' found with ISBN: https://www.googleapis.com/books/v1/volumes?q=isbn:0671870432
    
#Search result
############################
    #path toward BookCrossing original database (the one to be completed)
    cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
    cheminBookCrossing = cheminBookCrossing.replace('\\', '/')
    
    #path toward file on which scrapping results are saved
    cheminGoogleBooks = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\Scrapped_GoogleBooks/'
    cheminGoogleBooks = cheminGoogleBooks.replace('\\', '/')
    SaveFileName = cheminGoogleBooks + 'GoogleBooks_InternetSearch_25_04_2021.csv'

    #Missing (inside BookCrossing database) books information to retrieve thanks to scrapping
    theColumns = ['ISBN_10', 'ISBN_13', 'OtherID', 'Book-Title', 'Book-Author', \
                        'Year-Of-Publication', 'Publisher', 'Category', 'Description', 'Language', \
                        'Image', 'Pages', 'Awards', "Author's genre", 'Same serie', 'average_rating']

    #List of books to search on Google
    f = open(cheminBookCrossing + 'Extrait1000_BX-Books.csv', encoding="utf8", errors="replace")
    f.readline()
    
    #Google search function
    NotFoundBooks = GoogleSearch(f, SaveFileName, theColumns, 0, 15, Re = True) 

    print("Not found books: %d" % NotFoundBooks)
    f.close()   
    
    
 
