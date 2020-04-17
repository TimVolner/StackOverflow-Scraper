#Created 6/14/19
#Last Updated 6/24/19 6:45PM PCT

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

import os
import re

def simple_get(url):
    
    #Try getting content from url. If it is HTML or XML it will return the content, otherwise it returns NONE
    try:
        with closing(get(url, stream=True)) as cont:
            return(cont.text if is_good_response(cont) else None)

    except RequestException as e:
        log_error('Could Not Connect To {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(cont):
    
    # Determine whether the response is HTML or XML and return True/False
    content_type = cont.headers['Content-Type'].lower()
    return (cont.status_code == 200 and content_type is not None and content_type.find('html') > -1)

def log_error(e):
    
    # Easy to mody function for errors. I may add an error log txt in the future
    # For now, just pass over the html trying to be read
    pass

def write_code_file(soup, libs, inp_all):
    
    # Variables. dict for replacing certain html characters with specific characters
    dic = {'</code>,' : '\n**************************************************************************\n', '&gt;':'>', '&lt;' : '<'}
    lib_in_data = False
    
    # Search for code within the content
    for l in str(soup.find_all('code')).split('<code>'):
        
        # Return True if any one of the user requested libraries are visible in code
        if inp_all == 'ONE':
            for i in libs:
                if i in l:
                    lib_in_data = True
        
        # If 'ONE' is not entered by user, check if all the requested libraries are visible in the code and return True if so
        else:
            lib_in_data = (True if all(i in l for i in libs) else False)
        
        # if code has user requested libraries, replace html tags with characters and write code to file        
        if lib_in_data:
            l = list(l.replace(i, j) for i, j in dic.items())
            
            # Only add code if there are at least 10 lines of code
            if l.count('\n') > 10:
                with open('code.txt', 'a') as f:
                    f.write(l) 
                    print("Added Code")

def parse_html(soup, html_list):

    hl = []
    
    # search the content of html for more htmls for stackoverflow to automate htmls and add individual htmls to list, hl
    for l in str(soup.find_all('a')).split('href'):
        l = l.replace('href=,', '\n')
        
        for i in l.split('"'):
            hl.append(i)
    
    html_list = is_acc_html(hl, html_list)
    
    return(html_list)
    
def is_acc_html(hl, html_list):
    
    
    # determine if the found html's will be worth scraping for code, if so, add to html_list
    for i in hl:
        
        try:   
            if i not in html_list:
            
                if 'https://stackoverflow.com/questions/' in i:
                    html_list.append(i)
                
                elif '/questions/' in i:
                    i = 'https://stackoverflow.com' + i
                    html_list.append(i)
                    
        except:
            pass
    
    return(html_list)

def main():
    a = open('code.txt', 'w')
    a.close()

    # Determine which libraries the user wants to search for and at what frequency the libraries are visible in the code
    inp_libs = input("What Libraries would you like to search for? (Separate with a comma and a space, ie , )\n")
    inp_all = input("\nLook for code which has ONE of these or ALL of these? (Input 'ONE' or 'ALL'):\n")
    
    # take user input and separate into list
    libs = inp_libs.split(", ")

    # set beginning html here. If user is search all libraries input, we will make the search slightly more efficient
    html_list = (["https://stackoverflow.com/questions/tagged/" + libs[0]] if inp_all == 'ALL' else ["https://stackoverflow.com/questions/"])
  
    used_html = []    

    # Run this program until all htmls have been scraped
    while html_list != []:
        
        for html in html_list:
        
            # if the html has not been used, continue the program
            if html not in used_html:
            
                # retrieve content from html
                raw_html = simple_get(html)
                
                if raw_html != None:
                    
                    soup = BeautifulSoup(raw_html, "lxml")
                    
                    write_code_file(soup, libs, inp_all)
                    html_list = parse_html(soup, html_list)
                    html_list.remove(html) 
            
            else:
                html_list.remove(html)
            
            used_html.append(html)
                   
main()