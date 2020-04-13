import requests
import datetime
from bs4 import BeautifulSoup, element

jMemberIndex = "Junior Member\n</h3>"
gt = "https://www.gametracker.com"
gtquery = gt + "/server_info/TTT.DEFYclan.com:27015/top_players/?query="
maxDays = 30 * 6


def getMembers():
    # text = requests.get("http://defyclan.com/roster").text
    text = requests.get("http://defyclan.com/roster").text

    members = text[text.index(jMemberIndex) + len(jMemberIndex):]
    members = members[:members.index("</div>")]

    soup = BeautifulSoup(members, "html.parser")
    tables = soup.find_all("a")

    members = []

    for tag in tables:
        tag: element.Tag
        members.append(tag.text)
    return members


def main():
    members = getMembers()
    results = {}

    for member in members:
        link = gtquery + member.replace(" ", "+")
        result = requests.get(link).text
        memberPage = BeautifulSoup(result, "html.parser")
        links = memberPage.find_all(attrs={"class": "table_lst table_lst_spn"})

        for tag in links:
            tag: element.Tag
            targetLink = gt + tag.find_all("a", href=True)[4]["href"]
            # print(targetLink)
            info: PlayerInfo = getPlayerInfo(member, targetLink)
            daysSince = getDaysSince(info.getLastSeen())
            # print(member + " was last on " + str(daysSince) + " day(s) ago")
            print("{} was last on {} day{} ago".format(member, daysSince, "" if daysSince == 1 else "s"))
            results[member] = int(daysSince)
            break
        if member not in results:
            results[member] = maxDays

    results: dict = dict(sorted(results.items(), key=lambda kv: (kv[1], kv[0]), reverse=True))

    with open("output.txt", "w+", encoding="utf-8") as f:
        for member, days in results.items():
            f.write("{} was last on {} day{} ago\n".format(member, days, "" if days == 1 else "s"))


def getPlayerInfo(name, link):
    text = requests.get(link).text
    soup = BeautifulSoup(text, "html.parser")
    dataTable: element.Tag = soup.find_all("div", "item_float_left")[2]
    firstSeen: str = dataTable.contents[4]
    lastSeen: str = dataTable.contents[8]
    pinfo = PlayerInfo(name)
    pinfo.setFirstSeen(firstSeen.strip())
    pinfo.setLastSeen(lastSeen.strip())
    return pinfo


def getDaysSince(date):
    if "," not in date:
        return 0
    dt = datetime.datetime.strptime(date, "%b %d, %Y %I:%M %p")
    return (datetime.datetime.now() - dt).days


class PlayerInfo(object):
    def __init__(self, name):
        self.lastSeen = "Jan 01, 1970 12:00 PM"
        self.firstSeen = "Jan 01, 1970 12:00 PM"

    def getName(self):
        return self.name

    def getLastSeen(self):
        return self.lastSeen

    def setLastSeen(self, lastSeen):
        self.lastSeen = lastSeen

    def getFirstSeen(self):
        return self.firstSeen

    def setFirstSeen(self, firstSeen):
        self.firstSeen = firstSeen


main()
