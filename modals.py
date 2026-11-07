import discord

class staffAnnouncementModel(discord.ui.Modal, title="[Staff only] Announcement message"):
    modalSuccess = False
    modalMessage = ""
    defer = None
    messageInput = discord.ui.TextInput(
        label="Message", style = discord.TextStyle.long,
        placeholder="Hey all! ...", required = True
    )

    async def on_submit(self, interaction: discord.Interaction):
        message = self.messageInput.value
        if len(message) > 2000:
            self.modalMessage = "Message too long! Max is 2000 characters"
        else:
            self.modalSuccess = True
            self.modalMessage = message
        defer = await interaction.response.defer(ephemeral=True)
        return