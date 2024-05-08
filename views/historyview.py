import discord

from views.baseview import View, PageButton, EditButton, NavigationButton
from scripts.process_data import process_history
from scripts.get_embeds import history_embed

class HistoryView(View):
    def __init__(self, cur, author_id, matches, riot, puuid, icon_id, rank, index=0):
        super().__init__()
        self.cur = cur
        self.author_id = author_id
        self.matches = matches
        self.riot = riot
        self.puuid = puuid
        self.icon_id = icon_id
        self.rank = rank
        self.index = index

        self.stat_type = 'general'
        self.gamemode = None
        self.mode_name = 'All Modes'
        self.show_match_ids = False

        self.add_default_butons()

    def add_default_butons(self):
        self.clear_items()
        self.add_item(PageButton(self.change_page, '<', -6))
        self.add_item(PageButton(self.change_page, '>', 6))
        self.add_item(NavigationButton(self.set_data_buttons, 'Data', style=discord.ButtonStyle.blurple))
        self.add_item(NavigationButton(self.set_gamemode_buttons, 'Gamemode', style=discord.ButtonStyle.blurple))
        self.add_item(EditButton(self.update_message, style=discord.ButtonStyle.grey, label='Match IDs', toggle_match_ids=True))

    async def set_default_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.add_default_butons()
        await interaction.response.edit_message(view=self)

    async def set_data_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        self.add_item(EditButton(self.update_message, label='General', stat_type='general'))
        self.add_item(EditButton(self.update_message, label='Traits', stat_type='traits'))
        self.add_item(EditButton(self.update_message, label='Units', stat_type='units'))
        self.add_item(EditButton(self.update_message, label='Augments', stat_type='augments'))
        await interaction.response.edit_message(view=self)

    async def set_gamemode_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        for label, gamemode in [['All Modes', 'all'], ['Ranked', 'ranked'], ['Hyper Roll', 'turbo'], ['Double Up', 'pairs']]:   # add ['Normal', 'normal'] for only unranked games
            self.add_item(EditButton(self.update_message, label=label, gamemode=gamemode, mode_name=label))
        await interaction.response.edit_message(view=self)

    async def change_page(self, interaction, delta):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        if 0 <= self.index + delta < len(self.matches):
            self.index += delta

        embed = history_embed(self.matches, self.riot, self.icon_id, self.rank, stat_type=self.stat_type, index=self.index, show_ids=self.show_match_ids)

        await interaction.response.edit_message(embed=embed)

    async def update_message(self, interaction, mode_name=None, gamemode=None, count=None, days=None, stat_type=None, sort_by=None, descending=None, toggle_match_ids=None):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.add_default_butons()
        if gamemode:
            self.index = 0
            self.gamemode = gamemode
            self.mode_name = mode_name
            if gamemode == 'all':
                self.gamemode = None
        if stat_type:
            self.stat_type = stat_type
        if toggle_match_ids:
            self.show_match_ids = not self.show_match_ids

        matches = process_history(self.cur, self.puuid, self.stat_type, self.gamemode)
        embed = history_embed(matches, self.riot, self.icon_id, self.rank, stat_type=self.stat_type, index=self.index, show_ids=self.show_match_ids)

        await interaction.response.edit_message(embed=embed, view=self)