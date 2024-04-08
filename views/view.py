import discord

class EditButton(discord.ui.Button):
    def __init__(self, function, style=discord.ButtonStyle.blurple, label='X', row=None, gamemode=None, mode_name=None, count=None, days=None, stat_type=None, sort_by=None, descending=None):
        super().__init__(style=style, label=label, row=row)
        self.function = function
        self.gamemode = gamemode
        self.mode_name = mode_name
        self.count = count
        self.days = days
        self.stat_type = stat_type
        self.sort_by = sort_by
        self.descending = descending

    async def callback(self, interaction: discord.Interaction):
        await self.function(interaction, gamemode=self.gamemode, mode_name=self.mode_name, count=self.count, days=self.days, stat_type=self.stat_type, sort_by=self.sort_by, descending=self.descending)

class NavigationButton(discord.ui.Button):
    def __init__(self, function, label='X', style=discord.ButtonStyle.gray, row=None):
        super().__init__(style=style, label=label, row=row)
        self.function = function

    async def callback(self, interaction: discord.Interaction):
        await self.function(interaction)

class PageButton(discord.ui.Button):
    def __init__(self, function, label, delta, style=discord.ButtonStyle.green, row=None):
        super().__init__(style=style, label=label, row=row)
        self.function = function
        self.delta = delta

    async def callback(self, interaction: discord.Interaction):
        await self.function(interaction, self.delta)

class View(discord.ui.View):
    def __init__(self):
        super().__init__()

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)