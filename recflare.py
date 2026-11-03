import requests

class returns:
    class accountInfo:
        def __init__(self):
            self.username = ""
            self.displayName = ""
            self.displayNameEmoji = ""
            self.profilePicUrl = ""
            self.joinedRecflare = ""
            self.playerExists = False
    class roomInfo:
        def __init__(self):
            self.roomExists = False
            self.roomName = ""
            self.roomDescription = ""
            self.roomVisits = 0
            self.roomCreatorUsername = ""
            self.roomMaxPlayers = 0
            self.roomThumbnailUrl = ""
            self.roomPublished = ""

class recflareApi:
    def getPlayerProfileInfo(self, username: str) -> returns.accountInfo:
        player = requests.get(f"https://accounts.recflare.net/account/search?name={username}")
        data = player.json()
        if not data:
            playerDoesntExistAccount = returns.accountInfo()
            playerDoesntExistAccount.playerExists = False
            return playerDoesntExistAccount
        data = player.json()[0]
        account = returns.accountInfo()
        account.username = data['username']
        account.displayName = data['displayName']
        account.displayNameEmoji = data['displayEmoji']
        account.profilePicUrl = f"https://img.recflare.net/{data['profileImage']}?width=512"
        account.joinedRecflare = data['createdAt'].split("T")[0]
        account.playerExists = True
        return account

    def getRoomInfo(self, roomName: str) -> returns.roomInfo:
        roomReq = requests.get(f"https://rooms.recflare.net/rooms?name={roomName}")
        data = roomReq.json()
        if not data:
            roomDoesNotExist = returns.roomInfo()
            roomDoesNotExist.roomExists = False
            return roomDoesNotExist
        data = roomReq.json()
        room = returns.roomInfo()
        room.roomName = data['Name']
        room.roomDescription = data['Description']
        room.roomVisits = data['Stats']['VisitCount']
        room.roomThumbnailUrl = f"https://img.recflare.net/{data['ImageName']}"
        room.roomPublished = data['PublishedAt'].split("T")[0]
        room.roomMaxPlayers = data['MaxPlayers']
        room.roomCreatorUsername = requests.get(f"https://accounts.recflare.net/account/{data['CreatorAccountId']}").json()['username']
        room.roomExists = True
        return room

    def getPlayersOnline(self) -> int:
        req = requests.get("https://www.recflare.net/server-status").json()
        return int(req["players"])

    def getHottestRoomName(self) -> str:
        req = requests.get("https://rooms.recflare.net/rooms/hot?take=1").json()
        return req["Results"][0]["Name"]