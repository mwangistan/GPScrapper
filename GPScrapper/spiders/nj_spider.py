import scrapy
import json
from scrapy.http import Request, FormRequest
from scrapy_splash import SplashRequest

script = """

	function main(splash)
	  splash:go(splash.args.url)
	  splash:wait(30)

	  if splash.args.title_id ~= nil then
	  	if string.len(splash.args.title_id) == 4 then
			local id = '#'..splash.args.title_id
			local href = splash:select(id..'>.tcfrmg>a')
	  		href:mouse_click()
	  		splash:wait(10)
	  	else
	  		local title_length = string.len(splash.args.title_id)
	  		local loop_times = (title_length - 4)/3
	  		local original_id = '#'..string.sub(splash.args.title_id, 0, 4)
	  		href = splash:select(original_id..'>.tcfrmg>a')
	  		href:mouse_click()
	  		splash:wait(10)

	  		local start_position = 2
  			local step = 3
  			if splash.args.text == 'get' then
	  			for i = 1,loop_times do
	  				start_position = start_position + step
	  				id = string.sub(splash.args.title_id, start_position, start_position+step-1)
	  				local full_id = original_id..id
	  				original_id = full_id

	  				if i==loop_times then
	  					href = splash:select(full_id..'>.tcfrmg:last-child>a')
			  			href:mouse_click()
	  					splash:wait(10)
	  				else
	  					href = splash:select(full_id..'>.tcfrmg>a')
	  					href:mouse_click()
	  					splash:wait(10)
	  				end 
	  			end 				
  			else
	  			for i = 1,loop_times do
	  				start_position = start_position + step
	  				id = string.sub(splash.args.title_id, start_position, start_position+step-1)
	  				local full_id = original_id..id
	  				original_id = full_id
	  				href = splash:select(full_id..'>.tcfrmg>a')
	  				href:mouse_click()
	  				splash:wait(10)

	  			end
	  		end
	  	end

	  else
	  	local href2 = splash:select('.tcfrmg>a')
	  	href2:mouse_click()
	  	splash:wait(10)
	  end

	  return splash.html()
	end
"""

class BlogSpider(scrapy.Spider):

	'''
		Spider to extract all pieces of the new jersey administrative code	

	'''

	name = 'nj_administrative_code'
	start_url = 'https://www.lexisnexis.com/hottopics/njcode/sendSearch.asp?disptoc=on'
	titles = []
	current_title_id = ''
	getPreviousTitles = False

	def start_requests(self):

		yield SplashRequest(url=self.start_url, callback=self.parse_titles, args={'timeout':300, 'lua_source':script},
			headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'},endpoint='execute'
		)

	def parse_titles(self, response):
		#save title then click next link
		if self.current_title_id == '':
			self.titles.append(response.xpath('//tr[@id="TAAB"]').css('td.tcfrmgNS ::text').extract())
			index = response.xpath('//tr/@*').extract().index('TAAB')+1
			new_title_id = response.xpath('//tr/@*').extract()[index]
			self.current_title_id = new_title_id
			yield SplashRequest(url=self.start_url, callback=self.parse_titles, args={'title_id':new_title_id, 'timeout':300, 'lua_source':script},headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}, endpoint='execute')


		else:
			title = response.xpath('//tr[@id="'+self.current_title_id+'"]').css('td.tcfrmgNS ::text').extract()
			if len(title) == 0 and self.getPreviousTitles == False:
				#Process Text
				textTitle = response.xpath('//tr[@id="'+self.current_title_id+'"]').css('td.tcfrmg ::text').extract()
				AllTitles = ''
				for title in self.titles:
					titleStr = str(title[0]) + str(title[1]) + '; '
					AllTitles+=titleStr
				AllTitles = AllTitles + textTitle[0].encode('ascii', 'ignore')+textTitle[1].encode('ascii', 'ignore')+textTitle[2].encode('ascii', 'ignore')+textTitle[3].encode('ascii', 'ignore')
				del self.titles[:]
				self.titles.append(AllTitles)

				new_title_id = self.current_title_id
				index = response.xpath('//tr/@*').extract().index(self.current_title_id)+1
				self.current_title_id = response.xpath('//tr/@*').extract()[index] 
				yield SplashRequest(url=self.start_url, callback=self.parse_text, args={'title_id':new_title_id, 'timeout':300, 'lua_source':script, 'text':'get'},headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}, endpoint='execute')


			elif len(title) == 0 and self.getPreviousTitles == True:
				self.getPreviousTitles == False
				textTitle = response.xpath('//tr[@id="'+self.current_title_id+'"]').css('td.tcfrmg ::text').extract()
				AllTitles = ''
				
				main_parent_id = self.current_title_id[0:4]
				main_parent = response.xpath('//tr[@id="'+main_parent_id+'"]').css('td.tcfrmgNS ::text').extract()
				self.titles.append(main_parent)

				id_length = len(self.current_title_id)
				loop_times = (id_length - 4)/3
				start_position = 1
				step = 3

				for i in range(0, loop_times):
					start_position = start_position + step
					title_id = self.current_title_id[start_position:start_position+step]
					main_parent_id += title_id
					if self.current_title_id == main_parent_id:
						pass
					else:
						title = response.xpath('//tr[@id="'+main_parent_id+'"]').css('td.tcfrmgNS ::text').extract()
					self.titles.append(title)

				for title in self.titles:
					titleStr = str(title[0]) + str(title[1]) + '; '
					AllTitles+=titleStr

				AllTitles += textTitle[0].encode('ascii', 'ignore')+textTitle[1].encode('ascii', 'ignore')+textTitle[2].encode('ascii', 'ignore')+textTitle[3].encode('ascii', 'ignore')

				del self.titles[:]
				self.titles.append(AllTitles)

				new_title_id = self.current_title_id
				index = response.xpath('//tr/@*').extract().index(self.current_title_id)+1
				self.current_title_id = response.xpath('//tr/@*').extract()[index] 
				yield SplashRequest(url=self.start_url, callback=self.parse_text, args={'title_id':new_title_id, 'timeout':300, 'lua_source':script, 'text':'get'},headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}, endpoint='execute')


			elif len(title) != 0 and self.getPreviousTitles == True:
				#Get all parent titles

				self.getPreviousTitles = False
				if len(self.current_title_id) == 4:
					#this is a parent title
					self.titles.append(title)
					index = response.xpath('//tr/@*').extract().index(self.current_title_id)+1
					new_title_id = response.xpath('//tr/@*').extract()[index]
					self.current_title_id = new_title_id
					yield SplashRequest(url=self.start_url, callback=self.parse_titles, args={'title_id':new_title_id, 'timeout':300, 'lua_source':script},headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}, endpoint='execute')


				else:
					main_parent_id = self.current_title_id[0:4]
					main_parent = response.xpath('//tr[@id="'+main_parent_id+'"]').css('td.tcfrmgNS ::text').extract()
					self.titles.append(main_parent)

					id_length = len(self.current_title_id)
					loop_times = (id_length - 4)/3
					start_position = 1
					step = 3
					for i in range(0, loop_times):
						start_position = start_position + step
						title_id = self.current_title_id[start_position:start_position+step]
						main_parent_id += title_id
						title = response.xpath('//tr[@id="'+main_parent_id+'"]').css('td.tcfrmgNS ::text').extract()
						self.titles.append(title)


					index = response.xpath('//tr/@*').extract().index(self.current_title_id)+1
					new_title_id = response.xpath('//tr/@*').extract()[index]
					self.current_title_id = new_title_id
					yield SplashRequest(url=self.start_url, callback=self.parse_titles, args={'title_id':self.current_title_id, 'timeout':300, 'lua_source':script},headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}, endpoint='execute')


			else:
				self.titles.append(title)
				index = response.xpath('//tr/@*').extract().index(self.current_title_id)+1
				new_title_id = response.xpath('//tr/@*').extract()[index]
				self.current_title_id = new_title_id
				yield SplashRequest(url=self.start_url, callback=self.parse_titles, args={'title_id':new_title_id, 'timeout':300, 'lua_source':script},headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}, endpoint='execute')
		


	def parse_text(self, response):
		text = response.xpath('//div[@id="bodystyle"]/text()').extract()
		fullText = ''
		for text in text:
			fullText+=text
		jsonBody = {'text':fullText.replace('\n', ''), 'title':self.titles[0].replace('\n', '')}

		del self.titles[:]
		self.getPreviousTitles = True

		with open('results.json', 'ab') as f:
			f.write(json.dumps(jsonBody) + "\n\n")

		yield SplashRequest(url=self.start_url, callback=self.parse_titles, args={'title_id':self.current_title_id, 'timeout':300, 'lua_source':script},headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0'}, endpoint='execute')


