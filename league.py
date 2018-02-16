import re
from team import Team

BASE_URL = "https://www.transfermarkt.co.uk"

class League:
	def __init__( self, name, url, scrapper):
		self.LeagueName = name
		soup = scrapper(url)
		teamsTable = soup.find("table", class_="items")
		teamUrls = teamsTable.find_all("a", class_="vereinprofil_tooltip", id=re.compile("\d+"))[::2]
		teamUrls = [BASE_URL + teamUrl["href"] for teamUrl in teamUrls]
		print ("Leagues: Capture all of the links:\n")
		print ("Teams: \n")
		print (teamUrls)

		# USe the Team class for all of the url .
		self.TeamsData = [ Team(teamUrl, self.LeagueName, scrapper) for teamUrl in teamUrls]
