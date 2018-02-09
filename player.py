from bs4 import BeautifulSoup as bs
import re
import pandas as pd

CURRENT_YEAR = 17
N_SEASON_HISTORY = 1


class PlayerProfile:
	def __init__(self, playerUrl, pageScrapper):
		urlPerfPage = playerUrl.replace("profil","leistungsdatendetails")
		trophies = playerUrl.replace("profil","erfolge")
		soup = pageScrapper( playerUrl)

		title = list()
		titleIMG = list()
		wonNum = list()

		playerAttributes = {}

		#scrapping profile page information

		playerAttributes["name"] = soup.find("div", class_="dataMain").find("h1").text
		StoredAttributes = ["Age:", "Height:", "Nationality:", "Position:", "Foot:", "Current club:",
							"In the team since:", "Contract until:", "Player agents:","Social media:",
							"JerseyNum", "Profile", "NxtPosition", "CurrentValue", "Trophies", "TDetails",
							"TNum", "Availability","Current international:","International caps/goals:"
							]
		
		for entry in soup.find("table", class_="auflistung").find_all("th"):
			key = entry.text.strip()
			val = entry.find_next_sibling().text

		
			if key in StoredAttributes:
				playerAttributes[ key[:-1].lower()] = val.strip()

		# make sure that the type is a string:
		if "JerseyNum" in StoredAttributes:
			playerAttributes["JerseyNum"] = (soup.find("div", class_="dataName").find("span").text).replace('#',"")

		#cleaning some entries

		if "height" in playerAttributes:
			#converting height in meters str to cm int 
			meter, centimeters = re.search("(\d),(\d+)",playerAttributes["height"]).groups()
			playerAttributes["height"] = int(meter)*100 + int(centimeters)
		
		# Later have to only add href so .get('href') - "Social media:",
		# ((soup.find("div", class_="socialmedia-icons").find_all("a")))
		accs = list()
		if "Social media:" in StoredAttributes:
			links = (soup.find("div", class_="socialmedia-icons"))
			if links is not None:
				for ea in (links.find_all("a")):
					accs.append(ea.get('href'))
			else:
				accs.append("NONE")
			playerAttributes['social media'] = accs
			
		if "nationality" in playerAttributes:
			if "\xa0" in playerAttributes["nationality"]:
				playerAttributes["nationality"] = playerAttributes["nationality"].replace("\xa0", " ")
		
		if "position" in playerAttributes:
			playerAttributes["position"] = "CF" if "Centre-Forward" in playerAttributes["position"] else "W"
		
		if "age" in playerAttributes:
			playerAttributes["age"] = int( playerAttributes["age"])

		# PICTURE OF EACH PLAYER IF AVAILABLE
		if "Profile" in StoredAttributes: 
			link = soup.find("div", {"class":"dataBild"})
			playerAttributes["Profile"] = link.img["src"]

		# Next Position that they can play
		nxtL = list()
		if "NxtPosition" in StoredAttributes:
			nxt = (soup.find("div", class_="nebenpositionen"))
			if nxt is not None:
				nx = (nxt.get_text().replace("\n","").replace("Other position(s):","").split("\t"))
				for each in nx:
					if len(each)>0:
						nxtL.append(each.strip())
			else:
				nxtL.append("None")
			playerAttributes["NxtPosition"] = nxtL

        
		Cval = list()
		# Market Information
		if "CurrentValue" in StoredAttributes:
			mkt = (soup.find("div", class_="dataMarktwert"))
			if mkt is not None:
				Cval = mkt.get_text(strip=True).replace("Last change: ","-").split("-")
			else:
				print("No Appraisal Yet.")
				Cval = ("No Market Evaluation Yet")
			playerAttributes["CurrentValue"] = Cval


		# Trophies
		tps = list()
		if "Trophies" in StoredAttributes:
			tr = (soup.find("div", class_="dataErfolge"))
			if tr is not None:
				tro = (tr.find_all("a"))
				tps = tro
				# playerAttributes["Trophies"] = tro
			else: 
				tps = "NO TROPHIES WON YET"
			playerAttributes["Trophies"] = tps
		
		# Cleanse the trophies
		if "Trophies" in playerAttributes:
			if "NO TROPHIES WON YET" in playerAttributes["Trophies"]:
				playerAttributes["Trophies"] = "NONe"
			else:
				for er in playerAttributes["Trophies"]:
					title.append(er["title"])
				# Find the Images and number time won.
					titleIMG.append(er.find('img')['src'])
					wonNum.append((er.get_text(strip=True)))
				
				for ims in titleIMG:
					if ims == "/images/icons/mehr_erfolge.png":
						titleIMG.pop()

				for tts in title:
					if tts == "All titles & victories":
						title.pop()	

				playerAttributes["Trophies"] = title
			# playerAttributes["Trophies"] = "NONe" if "NO TROPHIES WON YET" in playerAttributes["Trophies"] else "WORKING ON IT" 
		
		# Images of the trophies.
		if "TDetails" in StoredAttributes:
			playerAttributes["TDetails"] = titleIMG

		if "TNum" in StoredAttributes:
			playerAttributes["TNum"] = wonNum

		
		# Check if they are available to play, suspended or injured
		# Then add the information into a list
		inj = list()
		if "Availability" in StoredAttributes:		
			injured = (soup.find("div", class_="verletzungsbox"))
			if injured is not None:
				print("Not Available")
				inj = (injured.find("div", class_="text").get_text(strip=True).split("Return "))
			else:
				inj.append("Available To Play")
			playerAttributes["Availability"] = inj



		# International Goals
		basicINT = list()
		for entry in soup.find("div", class_="dataBottom").find_all("span"):
			basicINT.append (entry.get_text(strip=True)) 
		if 'International caps/goals:' in StoredAttributes:
			if 'International caps/goals:' in basicINT:
				print("Have International Experience")
				playerAttributes['International caps/goals:']=(basicINT[(basicINT.index('International caps/goals:'))+ 1])
			else:
				playerAttributes['International caps/goals:']=("No International Caps Yet.")

		# print (playerAttributes)
		# print (len(playerAttributes))

		#scrapping performance page information
		soup = pageScrapper(urlPerfPage)
		performanceColumns = ("season","competition", "games", "goals", "assists", "cards", "minutes")
		performanceRows = pd.DataFrame( {col:[] for col in performanceColumns})

		for row in soup.find("div", class_="responsive-table").find("tbody").find_all("tr"):
			rowContents = PlayerProfile.readRow( row)
			year = rowContents[0]
			if re.match( "\d{4}", year):
				year = int( year[2:])
				year = "%02d/%02d" %(year-1, year)
				rowContents[0] = year
			if not re.match( "\d{2}\/\d{2}", year):
				raise ValueError("Wrong format for played year")
			if int( year[:2]) < CURRENT_YEAR - N_SEASON_HISTORY:
				break

			# print(urlPerfPage)
			#print( rowContents)

			performanceRows = performanceRows.append( {col:val for col, val in zip(performanceColumns, rowContents)}, ignore_index=True)
		performanceDF = performanceRows.groupby("season").sum()
		performanceDetailsDF = performanceRows.groupby(["season", "competition"]).sum()


		
		#converting to serie
		performanceSeries = pd.Series( {"%s %s" %(row, col): performanceDF[col][row] for row in performanceDF.index for col in performanceDF.columns})
		performanceDetailsSeries = pd.Series( {"%s %s" %(row, col): performanceDetailsDF[col][row] for row in performanceDetailsDF.index for col in performanceDetailsDF.columns})

		self.PlayerData = pd.Series( playerAttributes).append(performanceSeries).append(performanceDetailsSeries)
		print( "\t%s done" %self.PlayerData["name"])



		
		
	def __str__(self):
		return "Performance profile for %s" % self.PlayerData["name"]

	def __repr__(self):
		return "< profile of %s >" % self.PlayerData["name"]

	@staticmethod
	def readRow( row):
		cells = row.find_all( "td")
		cells = list( map( lambda x : x.text.strip(), cells))
		# print(cells)

		year = cells[0]
		comp = cells[2]
		games_played = cells[4]
		goals_scored = cells[6]
		assists = cells[7]
		cds = cells[-2]
		minutes_played = cells[-1]

		games_played = int(games_played) if games_played != "-" else 0
		goals_scored = int(goals_scored) if goals_scored != "-" else 0
		assists = int(assists) if assists != "-" else 0
		minutes_played = int( minutes_played[:-1].replace(".","")) if minutes_played != "-" else 0
		return [year, comp, games_played, goals_scored, assists, cds, minutes_played]