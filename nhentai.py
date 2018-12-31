import shutil
import requests
import os
import argparse
from lxml import html

def Download_Single_File(path, url):
	response = requests.get(url, stream=True)
	if response.status_code == 200:
		with open(path, 'wb') as out_file:
			shutil.copyfileobj(response.raw, out_file)
		del response
		return 1
	else:
		return 0

def Download_prefix(Init, path ,url):
	Index = Init
	Prefixe = [".png",".jpg"]

	while True:		
		Exist = False
		print(url+str(Index)) #Commandline Output

		for Prefix in Prefixe:
			ip = str(Index)+Prefix
			Newpathpre = path+ip

			if os.path.isfile(Newpathpre):
				Exist = True
				break
			else:
				if Download_Single_File(Newpathpre, url+ip):
					Exist = True
					break
		if not Exist:
			break
		Index += 1

def Extract_Hentai_Index(tree):
	raw_html = tree.xpath('//*[@id="thumbnail-container"]/div[1]/a/img')
	coreurl = raw_html[0].get('data-src')
	Chapterurl = coreurl.split("/")[-2]
	Chapterurlcomplete =  "https://i.nhentai.net/galleries/"+Chapterurl+"/" 
	print("Gall: ", Chapterurlcomplete) #Commandline Output
	return Chapterurlcomplete

def Get_Hentai_name(tree):
	Special = "/","\\",":","*","?","\"","<",">","|",".",";"
	raw_html = tree.xpath('//*[@id="info"]/h1/text()')
	Name = raw_html[0]
	for i in range(len(Special)):
		Name = Name.replace(Special[i], "")

	return Name

def Download_Hentai_Chapter(path, url):
	response = requests.get(url, stream=True)
	if response.status_code == 200:
		tree = html.fromstring(response.content)
		Name = Get_Hentai_name(tree)
		Chapterurl = Extract_Hentai_Index(tree)
		print("Url: ", url)     #Commandline Output
		Newpath = path+"\\"+Name
		if not os.path.exists(Newpath):
	   		os.makedirs(Newpath)
		print("Name: ", Name)    #Commandline Output
		print("Path: ", Newpath) #Commandline Output
		Download_prefix(1 ,Newpath+"\\", Chapterurl)
	else:
		print("Url not reachable: " + url)

def Get_Hentai_Chapter_list(url):
	Urllist = []
	Index = 1

	while True:

		if "+" in url:
			Site_url = url+'&page='+str(Index)
		else:
			Site_url = url+'/?page='+str(Index)

		response = requests.get(Site_url, stream=True)
		if response.status_code == 200:
			tree = html.fromstring(response.content)

			try:
				Urltemp = tree.xpath('//*[@id="content"]/div[2]/div[1]/a')[0].get('href')
			except:	
				break

			for x in range(1,26):
				try:
					raw_html = tree.xpath('//*[@id="content"]/div[2]/div['+str(x)+']/a')
					Urllist.append('https://nhentai.net'+raw_html[0].get('href'))
				except:
					break

			Index += 1	
			print("Parse_Page: " + str(Index))	#Commandline Output
		else:
			break

	print(Urllist)                       #Commandline Output
	print(len(Urllist), " Manga found")  #Commandline Output	
	return Urllist	
	
def Download_all_Hentai_Chapter(path, url):
	Urllist = Get_Hentai_Chapter_list(url)

	for Urlentry in Urllist:
		Download_Hentai_Chapter(path, Urlentry)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='nhentai Downloader')
	parser.add_argument('-m','--Manga', action='store_false')
	parser.add_argument('-t','--Tag', action='store_false')
	parser.add_argument('-u', '--Url',
		action="store", dest="Url",
		help="Url for Chapter or Manga", default="")
	parser.add_argument('-d', '--destination',
		action="store", dest="destination",
		help="Path for Manga files", default="")	
	
	args = parser.parse_args()

	if (args.Tag ^ args.Manga):

		if not args.Tag:
			Download_all_Hentai_Chapter(args.destination, args.Url)
		if not args.Manga:
			Download_Hentai_Chapter(args.destination, args.Url)
	else:
		print("Usage: use -m or -t")