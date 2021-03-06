from player import PlayerProfile
import re

BASE_URL = "https://www.transfermarkt.co.uk"


class Team:
	def __init__( self, url, name, scrapper):
		self.LeagueName = name
		soup = scrapper(url)

		#reading player table and filtering for offensive players
		playerTable = soup.find("table", class_="items")


		players = playerTable.find_all("a", class_="spielprofil_tooltip")[::2]
		offensivePlayers = filter( Team.isStrikerOrWinger, players)
		offensivePlayersUrls = [BASE_URL + player["href"] for player in offensivePlayers]
		print("\n Now Offensive players list \n")
		print(offensivePlayersUrls)
		print("\n")

#Team URL: https://www.transfermarkt.co.uk/ajax-amsterdam/startseite/verein/610/saison_id/2017
		
		URLname = re.search('(.*uk\/)(.*)(\/start.*)', url)
		TeamName =  (URLname.group(2))

		print("Team " + str(TeamName) + " From '" + str(url) + "'")

		#self.PlayerData = [PlayerProfile( playerUrl, scrapper) for playerUrl in offensivePlayersUrls]
		self.PlayersData = []
		for playerUrl in offensivePlayersUrls:
			try:
				NewPlayerProfile = PlayerProfile( playerUrl, scrapper)
				NewPlayerProfile.PlayerData["current league"] = self.LeagueName
				self.PlayersData.append( NewPlayerProfile)
			except:
				continue


	@staticmethod
	def isStrikerOrWinger( player):
		position = player.find_next("tr").text.strip().lower()
		return "wing" in position or "centre-forward" in position
