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