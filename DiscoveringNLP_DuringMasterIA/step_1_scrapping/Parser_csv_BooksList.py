import re

    
def ParserCsvInputBookCrossing(currentLine, Re = False):
    """ line of BookCrossing database needs to be correctly parsed  """
    
    #Case where spliting with only " is enough : values of the 8 columns will be retrieved
    if Re == False:
        L = currentLine.split('"')
        
        #For each value, 2 " are used as delimiters, so one out of two split results is empty
        return [L[i] for i in range(16) if i%2 == 1]

    #Case where more advanced splitting is needed to retrieve values of the 8 columns
    else:
        #Separator of columns inside the csv file is ";"
        L = currentLine.split(';')
        if len(L) == 8:
            return L
       
        #The 8 values have not been retrieved with previous split, " is used inside values
        #Book-Title - Book-Author split is not OK, so all the other values are retrieved thanks to regular expressions
        else:
            #               ISBN             Year           image         image          image
            g = re.search('([0-9X]+);(.+);([0-9]{4,4})(.+)(;http.+.jpg)+(;http.+.jpg)+(;http.+.jpg)+', currentLine)
    
            #The 2nd group is Book-Title and Book-Author; so the 2 values must now be separated
            g_2 = g[2].split('"')
            if len(g_2) == 1:
                g_2_12 = g[2].split(';')
            else:
                g_2_12 = [g_2[i] for i in range(len(g_2)) if not (g_2[i] == '' or g_2[i] == ';')]
         
            #Values of the 8 columns have been retrieved
            return [x.strip(';') for x in [g[1], g_2_12[0], g_2_12[1], g[3], g[4], g[5], g[6], g[7]]]
    
    
if __name__ == "__main__":
    #path toward BookCrossing original database (the one to be completed)
    cheminBookCrossing = 'D:\DocsDeCara\Boulot\IA_ML\DSTI\Programme\ML_with_Python\Projet\Donnees\BookCrossing/'
    cheminBookCrossing = cheminBookCrossing.replace('\\', '/')

    f = open(cheminBookCrossing + 'BX-Books.csv', encoding="utf8", errors="replace")
    f.readline()
    
    for i in range(10):
        print(ParserCsvInputBookCrossing(f.readline()))
        print()

    f.close()
 
