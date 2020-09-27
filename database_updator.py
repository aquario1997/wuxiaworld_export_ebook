#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 4.14
# In conjunction with Tcl version 8.6
#	Aug 13, 2018 03:57:27 PM
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
import shutil
import sys
import locale
import codecs
import os
import os.path
import sqlite3 as sql
from bs4 import BeautifulSoup
import re
import json
import traceback

parent = None
conn = None
cursor = None
exclusion_novel_list = [
	# 'Condemning the Heavens',
	# 'Blue Phoenix'
]
expeled_novel_list = [
	'Coiling Dragon'
]
alt_cover_list = {
	# '7 Killers': 'https://image.ibb.co/fAgv6U/7k.png',
	'Warlock of the Magus World': 'https://image.ibb.co/gEOTt9/600.jpg',
	'Overthrowing Fate': 'https://image.ibb.co/m6SWyK/otf.png',
	'Legends of Ogre Gate': 'https://image.ibb.co/myNLse/loog_1.png',
	'Blue Phoenix': 'https://image.ibb.co/i4q6Xe/bp_1.png',
	'The Divine Elements': 'https://image.ibb.co/ceG58K/tde_1.png',
	'Condemning the Heavens': 'https://image.ibb.co/mTK8TK/cth_1.png'
	}
exception_names_list = {#for finding them on novelupdates.com
		'Legend of the Dragon King': 'the-legend-of-the-dragon-king',
		'Soul Land 2: The Unrivaled Tang Sect': 'douluo-dalu-2-the-unrivaled-tang-sect',
		'Soul Land 3: Legend of the Dragon King': 'the-legend-of-the-dragon-king',
		'Desolate Era': 'the-desolate-era',
		'Stellar Transformations': 'stellar-transformation',
		'Overlord of Blood and Iron': 'the-overlord-of-blood-and-iron'
	}

def download(link, file_name, ur_data=None):
	url = urllib.request.Request(
		link,
		data=ur_data,
		headers={
			   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		  }
		)
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
		 shutil.copyfileobj(response, out_file)

def get_cookie(link):
	url = urllib.request.Request(
		link,
		data=None,
		headers={
			   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		  }
		)
		
	response = urllib.request.urlopen(url)
	cookie = ''
	rep = response.getheader('set-cookie')
	rep = rep.split('secure, ')
	for coo in rep:
		tib = coo.split(';')[0].split('=')
		if tib[0] == '_csrfToken':
			cookie = tib[1]
	return cookie

def insert_wuxiaworld_novel(name, url):
	global conn, cursor, alt_cover_list, exception_names_list
	dir = os.path.dirname(os.path.realpath(__file__))
	if os.name == 'nt':
		dir = os.path.expanduser("~") + os.sep + "wuxiaworld_export_ebook"
		if os.path.isdir(dir) is False:
			os.mkdir(dir)
		if os.path.isdir(dir + os.sep + "tmp") is False:
			os.mkdir(dir + os.sep + "tmp")
		if os.path.isdir(dir + os.sep + "export") is False:
			os.mkdir(dir + os.sep + "export")
	#name
	#url
	autors = ''
	img = ''
	if name in expeled_novel_list: return
	translator = ''
	synopsis = ''
	
	filename_novelupdate = dir+os.sep+"tmp"+os.sep+"novel_"+urllib.parse.quote(name)+".html"
	filename_wuxiaworld = dir+os.sep+"tmp"+os.sep+"wuxia_"+urllib.parse.quote(name)+".html"
	
	url_novelupdate = ''
	if name in exception_names_list: url_novelupdate = "https://www.novelupdates.com/series/"+exception_names_list[name]+"/"
	else: url_novelupdate = "https://www.novelupdates.com/series/"+name.lower().replace("&", 'and').replace("’", '').replace("'", '').replace(":", '').replace(" ", '-')+"/"
	
	try: download(url, filename_wuxiaworld)
	except Exception as e:
		print('URL: {}, URLError: {} - {}'.format(url, e.code, e.reason))
	else:
		try: download(url_novelupdate, filename_novelupdate)
		except Exception as e:
			print('URL: {}, URLError: {} - {}'.format(url_novelupdate, e.code, e.reason))
			filename_novelupdate = None
		
		fileHandle1 = open(filename_wuxiaworld, "r", encoding = "utf8")
		if filename_novelupdate is not None:
			#Get data from novelupdates.com
			fileHandle2 = open(filename_novelupdate, "r", encoding = "utf8")
			soup = BeautifulSoup(fileHandle2, 'html.parser')
			if name in alt_cover_list:
				img = alt_cover_list[name]
			else: img = soup.find(class_='seriesimg').find('img').get('src')
			synopsis = soup.find(id='editdescription').get_text()
			autors = ''
			dom_authors = soup.find(id='showauthors').find_all('a')
			for aut in dom_authors:
				if autors != '': autors += ', '
				autors += aut.string
			soup = None
			fileHandle2.close()
			os.remove(filename_novelupdate)
			
			#Get data from wuxiaworld.com
			soup = BeautifulSoup(fileHandle1, 'html.parser')
			nov = soup.find(class_='novel-body')
			translator = nov.find_all('dd')[0].get_text()
			soup = None
			fileHandle1.close();
			os.remove(filename_wuxiaworld)
		else:
			#Get data from wuxiaworld.com
			soup = BeautifulSoup(fileHandle1, 'html.parser')
			nov = soup.find(class_='media media-novel-index')
			if name in alt_cover_list: img = alt_cover_list[name]
			else: img = nov.find('img').get('src')
			dom_authors = None
			if nov is not None:
				dom_authors = nov.find_all('p')
				dom_authors += nov.find_all('dl')
				for aut in dom_authors:
					if len(aut.contents) >= 1:
						strmade = ''
						for piece in aut.contents:
							if piece.string is not None:
								strmade += piece.string
						if 'Author:' in strmade or 'Translator:' in strmade:
							clean = strmade.replace('Author:', '').replace('Translator:', '').replace("\n", '').replace(
								"\r", '').replace("\t", '').strip()
							if clean not in autors:
								if autors != '': autors += ', '
								autors += clean
							
				dom_translators = nov.find_all('dl')
				for aut in dom_translators:
					if len(aut.contents) >= 1:
						strmade = ''
						for piece in aut.contents:
							if piece.string is not None:
								strmade += piece.string
						if 'Translator:' in strmade:
							clean = strmade.replace('Translator:', '').replace("\n", '').replace("\r", '').replace("\t", '').strip()
							if clean not in translator and clean not in autors:
								if translator != '': translator += ', '
								translator += clean
			
			fileHandle1.close();
			os.remove(filename_wuxiaworld)
			
		cursor.execute("INSERT INTO Information(NovelName,link,autor,cover,limited,translator,synopsis,source) VALUES(?,?,?,?,?,?,?,?)", (name, url, autors, img, limit, translator, synopsis, 'wuxiaworld.com'))
		conn.commit()

def start():
	global conn, cursor, parent
	dir = os.path.dirname(os.path.realpath(__file__))
	if os.name == 'nt':
		dir = os.path.expanduser("~") + os.sep + "wuxiaworld_export_ebook"
	conn = sql.connect(dir+os.sep+"novels.db")
	cursor = conn.cursor()
	
	if os.path.isdir(dir+os.sep+'tmp') is False:
		os.mkdir(dir+os.sep+'tmp')
		
	list_novel = []
	
	filename = dir+os.sep+"tmp"+os.sep+"wuxiaworld_updates.json"
	baseurl = 'https://www.wuxiaworld.com/api/novels/search'
	if parent is not None: parent.emit(['Database Update, Download Wuxiaworld Ongoing novel list', 1])
	else: print('>> Download Wuxiaworld Ongoing novel list')
	try:
		request = urllib.request.Request(
		baseurl,
		data=bytes('{"title":"","tags":[],"language":"Any","genres":[],"active":null,"sortType":"Name","sortAsc":true,"searchAfter":0,"count":9999}', 'utf-8'),
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36',
			'content-type': 'application/json;charset=UTF-8'
			}
		)
		with urllib.request.urlopen(request) as response, open(filename, 'wb') as out_file:
			shutil.copyfileobj(response, out_file)
	except HTTPError as e:
		# Return code error (e.g. 404, 501, ...)
		print('URL: {}, HTTPError: {} - {}'.format(baseurl, e.code, e.reason))
	except URLError as e:
		# Not an HTTP-specific error (e.g. connection refused)
		print('URL: {}, URLError: {}'.format(baseurl, e.reason))
	else:
		cursor.execute("DELETE FROM 'Information'")
		conn.commit()
		
		with open(filename, 'r',  encoding = "utf8") as file:
			data = json.load(file)
			#print(data)
			#print(data['items'])
			for nov in data['items']:
				# print(nov)
				#print(nov['name'])
				if nov['sneakPeek'] is False:
					list_novel.append({'name': nov['name'], 'url': 'https://www.wuxiaworld.com/novel/'+nov['slug']})
		os.remove(filename)
	
	"""
	filename = dir+os.sep+"tmp"+os.sep+"wuxiaworld_completed.html"
	baseurl = 'https://www.wuxiaworld.com/tag/completed'
	if parent is not None: parent.emit(['Database Update, Download Wuxiaworld Finished novel list', 1])
	else: print('>> Download Wuxiaworld Finished novel list')
	try:
		download(baseurl, filename)
	except HTTPError as e:
		# Return code error (e.g. 404, 501, ...)
		print('URL: {}, HTTPError: {} - {}'.format(baseurl, e.code, e.reason))
	except URLError as e:
		# Not an HTTP-specific error (e.g. connection refused)
		print('URL: {}, URLError: {}'.format(baseurl, e.reason))
	else:
		fileHandle = open(filename, "r", encoding = "utf8")
		soup = BeautifulSoup(fileHandle, 'html.parser')
		tab = soup.find(class_="media-list genres-list")
		novels_dom = tab.find_all(class_="media")
		for title in novels_dom:
			name = title.find('h4').string.replace('’', "'").strip()
			if name not in exclusion_novel_list:
				url = title.find('a').get('href')
				list_novel.append({'name': name, 'url': 'https://www.wuxiaworld.com'+url})
		fileHandle.close()
		os.remove(filename)
	"""
	
	baseurl = 'https://www.webnovel.com'
	cookie = ''
	if parent is not None: parent.emit(['Database Update, Get webnovel.com cookie', 1])
	else: print('>> Download Wuxiaworld Finished novel list')
	try:
		cookie = get_cookie(baseurl)
	except HTTPError as e:
		# Return code error (e.g. 404, 501, ...)
		print('URL: {}, HTTPError: {} - {}'.format(baseurl, e.code, e.reason))
	except URLError as e:
		# Not an HTTP-specific error (e.g. connection refused)
		print('URL: {}, URLError: {}'.format(baseurl, e.reason))
	else:
		print(cookie)
		#https://www.webnovel.com/apiajax/search/PageAjax?_csrfToken=mC5uuDqyBFhY9KB5j29dzhiNnLUIHmQApnufp398&isExternal=0&pageSize=20&pageIndex=3&keywords=%
		
		
	pos = 1.0
	step = 99.0 / float(len(list_novel))
	# print(list_novel)
	for novel in list_novel:
		pos += step
		if parent is not None: parent.emit(['Database Update, Processing "{}"'.format(novel['name']), int(pos)])
		else: print('=> Processing:', novel['name'])
		try:
			insert_wuxiaworld_novel(novel['name'], novel['url'])
		except:
			traceback.print_exc()
		
	cursor = None
	conn.close()
	print('< Database Update Completed')
if __name__ == '__main__':
	start()
