# -*- coding: utf-8 -*-
import scrapy

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import time
import json

class NotifiedListSpider(scrapy.Spider):

	name = 'Notified_List'
	allowed_domains = ['']
	start_urls = ['https://sistemanotificaciones.portal.gub.uy/']

	start_url = 'https://sistemanotificaciones.portal.gub.uy/'
	notified_url = 'https://sistemanotificaciones.portal.gub.uy/eNotifications/pages/views/view_enotificaciones.xhtml?state=8'
	notified_detail = 'https://sistemanotificaciones.portal.gub.uy/eNotifications/pages/documentos/enotification.xhtml'

	#  =========== [import google chrome selenium drive] ===========

	print ('==================  [loading Selenium, please wait just second ... ]  ====================')

	crome_path = r"C:\cromedriver\chromedriver.exe"

	chrome_options = Options()

	#  =========== [define options] ===========

	prefs = {'profile.managed_default_content_settings.images':2}
	chrome_options.add_experimental_option("prefs", prefs)

	chrome_options.add_argument("headless")
#	chrome_options.add_argument("log-level=3")
	
	driver = webdriver.Chrome(crome_path, chrome_options=chrome_options) 
	driver.maximize_window()

	driver.get(start_url)

	
	def forward_pagination(self, nstep, number):
		time.sleep(2)

		self.driver.get(self.notified_url)

		N = nstep
		print ('==================== [current pagination: ' + str(N+1) + ' ,current row: '+ str(number+1) + '] ====================' )

		while N > 0:

			time.sleep(1)
			next_pagination = self.driver.find_element_by_xpath('//*[@id="formPrincipal:tabla_documentos_paginator_bottom"]/span[4]')
			next_pagination.click()

			time.sleep(1)
			N = N -1

	def Processing_Each_Items(self, number, a_element):

		nPagination = int(number/20)
		
		self.forward_pagination(nPagination, number)
		
		a_xpath = self.driver.find_element_by_xpath(a_element)
		a_xpath.click()

		# getting detail information as json format
		try:
			self.item_detail()
		except Exception as e:
			print ('Table Format is broken!')

	def item_detail(self):

		object_item_array = {}
		
		time.sleep(2)
		self.driver.get(self.notified_detail)

		# getting detail information as json format

		main_content = self.driver.find_element_by_xpath('//div[@class="notificationRichTextContent"]')

		for tb_elemet in main_content.find_elements_by_xpath('.//table/tbody'):

			trCount = 1

			for tr_element in tb_elemet.find_elements_by_xpath('.//tr'):

				td_elements = tr_element.find_elements_by_xpath('.//td')
				nLen = len(td_elements)

				tdCount = 0

				KEY = ''
				VALUE = ''
				VALUE_LIST = []

				
				for td_element in td_elements:
					
					if (nLen > 2) and (trCount == 1):
						pass

					else:
						subject_id = td_element.text

						if tdCount == 0:
							KEY = subject_id

						else:
							if nLen > 2:
								VALUE_LIST.append(subject_id)
							else:
								VALUE = subject_id
					tdCount = tdCount + 1

				if KEY!='':
					if nLen > 2:
						object_item_array[KEY] = VALUE_LIST
					else:
						object_item_array[KEY] = VALUE
					
				trCount = trCount + 1

		para_elemet = main_content.find_element_by_xpath('.//p[1]')
		para_version = self.detect_MONTO(main_content.text)

		object_item_array["MONTO UR"] = para_version
		object_item_array["Text"] = para_elemet.text

		json_data = json.dumps(object_item_array)
		print (json_data)

	def detect_MONTO(self, arg):

		try:

			str_first = arg.split('MONTO UR:')
			str_second = str_first[1].split('\n')
			version_str = ''.join(str(str_second[0]).split())

		except Exception as e:
			version_str = ""

		return version_str



	def parse(self, response):

		username = self.driver.find_element_by_name("username")
		userpwd = self.driver.find_element_by_name("password")

		username.send_keys('18401519')
		userpwd.send_keys('TJUANGOSA')

		submit = self.driver.find_element_by_xpath('//input[@type="submit"]')
		submit.click()

		print ('>>>>>>>>>>>>>>>>>>>>>>> [Login Passed Successfully!] >>>>>>>>>>>>>>>>>>>>>>>>>>>')
		self.driver.get(self.notified_url)
		
		Atag_xpath_Array = []

		nRowCount = 0
		nRowIndex = 0

		while True:

			next_pagination = self.driver.find_element_by_xpath('//*[@id="formPrincipal:tabla_documentos_paginator_bottom"]/span[4]')
			next_Attr = next_pagination.get_attribute('class')

			if "ui-state-disabled" in next_Attr:
				print ('Scanning End !')

				table_element = self.driver.find_element_by_xpath('//*[@id="formPrincipal:tabla_documentos_data"]')

				for tr_elemet in table_element.find_elements_by_xpath('.//tr'):

					A_element = tr_elemet.find_element_by_xpath('.//td/a')
					A_element_Id = A_element.get_attribute('id')

					xpath_string = "//a[@id='" + A_element_Id + "']"
					Atag_xpath_Array.append(xpath_string)		

				break
				
			elif "ui-state-hover" in next_Attr:
				pass

			else:
				#  =========== [Processing One Item Detail] ===========

				table_element = self.driver.find_element_by_xpath('//*[@id="formPrincipal:tabla_documentos_data"]')

				for tr_elemet in table_element.find_elements_by_xpath('.//tr'):

					A_element = tr_elemet.find_element_by_xpath('.//td/a')
					A_element_Id = A_element.get_attribute('id')

					xpath_string = "//a[@id='" + A_element_Id + "']"
					Atag_xpath_Array.append(xpath_string)
					
				next_pagination.click()
				
		print ('======================  [Selenium Scraping Started !]  ========================')
		print ("Total Rows:" + str(len(Atag_xpath_Array)))

		for each_xpath in Atag_xpath_Array:
			
			self.Processing_Each_Items(nRowIndex, each_xpath)
			nRowIndex = nRowIndex + 1
