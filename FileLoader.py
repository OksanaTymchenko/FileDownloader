from bs4 import BeautifulSoup
import requests
import os
import sys
import re

# url = 'https://www.kmu.gov.ua/meetings/zasidannya-kabinetu-ministriv-ukrayini-24-12-2019'

def GetParser(url):
	response = requests.get(url)
	return BeautifulSoup(response.content, 'html.parser')

def DirNameStrip(dir_name):
	if len(dir_name) > 60:
		dir_name = dir_name[:60]+'...'
	return dir_name

def GetDocumentsLink(url):
	soup = GetParser(url)
	event = soup.find(class_="news__title--text").string
	date_str = '\d+\-\d+\-\d+'
	publication_date = re.search(date_str, url).group()
	dir_name = DirNameStrip(' '.join([publication_date, event]))
	# publication_date = soup.find(class_="news__title--desc").string
	# publication_date = re.sub('\s+', '', publication_date)
	# publication_date = publication_date.split('опубліковано')[1]

	documents_link = soup.find(string=re.compile("Матеріали")).find_parent()
	documents_link = documents_link.find("a", href=True)
	if documents_link:
		os.mkdir(dir_name)
		os.chdir('./'+dir_name)
		return documents_link['href']
	return None


def FileLoader(url):	
	doc_link = GetDocumentsLink(url)
	if doc_link:
		base_link = doc_link.rsplit('/', maxsplit = 1)[0]+'/'
		soup = GetParser(doc_link)
		header = soup.div(class_="head")
		items = header[0].find_next_siblings()
		in_dir = False
		for i in items:
			if i['class'][0] == "head1":
				if in_dir:
					os.chdir("..")
				group_name = DirNameStrip(i.h3.string)
				os.mkdir(group_name)
				os.chdir('./'+group_name)
				in_dir = True
			else:
				item_name = i.h4
				if item_name:
					number = item_name.span.string
					name = DirNameStrip(number + item_name.contents[1])
					os.mkdir(name)
					os.chdir('./'+name)
					for a in i.find_all('a', href=True):
						file_link = base_link + a['href']
						filename = file_link.rsplit('/')[-1]
						myfile = requests.get(file_link)
						open('./'+filename, 'wb').write(myfile.content)
					os.chdir("..")

if __name__ == "__main__":
    FileLoader(sys.argv[1])
