from typing import Any
import discord
from scripts.get_embeds import stats_embed
from scripts.process_data import process_stats

class EditButton(discord.ui.Button):
    def __init__(self, function, style=discord.ButtonStyle.blurple, label='X', gamemode=None, count=None, days=None):
        super().__init__(style=style, label=label)
        self.function = function
        self.gamemode = gamemode
        self.count = count
        self.days = days

    async def callback(self, interaction: discord.Interaction):
        await self.function(gamemode=self.gamemode, count=self.count, days=self.days)
        await interaction.response.edit_message()

class NavigationButton(discord.ui.Button):
    def __init__(self, function, label='X', gamemode=None):
        super().__init__(style=discord.ButtonStyle.grey, label=label)
        self.function = function

    async def callback(self, interaction: discord.Interaction):
        await self.function(interaction)


class StatsView(discord.ui.View):
    def __init__(self, cur, data, author, riot, server, icon_id, rank, count, days, set):
        super().__init__()
        self.default_buttons()

        self.cur = cur
        self.data = data
        self.author = author
        self.riot = riot
        self.server = server
        self.icon_id = icon_id
        self.rank = rank
        self.gamemode = ''
        self.count = count
        self.days = days
        self.set = set

    def default_buttons(self):
        self.clear_items()
        self.add_item(NavigationButton(self.set_gamemode_buttons, label='Change Gamomode'))
        self.add_item(NavigationButton(self.set_scope_buttons, label='Change Scope'))

    async def set_default_buttons(self, interaction):
        self.default_buttons()
        await interaction.response.edit_message(view=self)

    async def set_gamemode_buttons(self, interaction):
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        for label, gamemode in [['All Modes', 'all'], ['Standard', 'standard'], ['Hyper Roll', 'turbo'], ['Double Up', 'pairs']]:
            self.add_item(EditButton(self.update_message, label=label, gamemode=gamemode))
        await interaction.response.edit_message(view=self)

    async def set_scope_buttons(self, interaction):
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        self.add_item(NavigationButton(self.set_count_buttons, label='Last x games'))
        self.add_item(NavigationButton(self.set_time_buttons, label='Games since'))
        await interaction.response.edit_message(view=self)

    async def set_count_buttons(self, interaction):
        self.clear_items()
        self.add_item(NavigationButton(self.set_scope_buttons))
        for num in [100, 50, 20, 10]:
            self.add_item(EditButton(self.update_message, label=str(num), count=num))
        await interaction.response.edit_message(view=self)

    async def set_time_buttons(self, interaction):
        self.clear_items()
        self.add_item(NavigationButton(self.set_scope_buttons))
        for label, days in [['Month', 30], ['Week', 7], ['24h', 1]]:
            self.add_item(EditButton(self.update_message, label=label, days=days))
        await interaction.response.edit_message(view=self)
    

    async def update_message(self, gamemode=None, count=None, days=None):
        if count or days:
            self.count = count
            self.days = days
        if gamemode:
            self.gamemode = gamemode

        self.data = process_stats(self.cur, self.riot, self.server, self.count, self.days, self.set)

        embed = stats_embed(self.data, self.author, self.riot, self.icon_id, self.rank, self.gamemode)
        await self.message.edit(embed=embed, view=self)

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)