from typing import Any
import discord
from scripts.get_embeds import stats_embed, traits_embed, augments_embed
from scripts.process_data import process_stats, process_traits, process_augments

class EditButton(discord.ui.Button):
    def __init__(self, function, style=discord.ButtonStyle.blurple, label='X', gamemode=None, mode_name=None, count=None, days=None, stat_type=None):
        super().__init__(style=style, label=label)
        self.function = function
        self.gamemode = gamemode
        self.mode_name = mode_name
        self.count = count
        self.days = days
        self.stat_type = stat_type

    async def callback(self, interaction: discord.Interaction):
        await self.function(interaction, gamemode=self.gamemode, mode_name=self.mode_name, count=self.count, days=self.days, stat_type=self.stat_type)

class NavigationButton(discord.ui.Button):
    def __init__(self, function, label='X', style=discord.ButtonStyle.gray):
        super().__init__(style=style, label=label)
        self.function = function

    async def callback(self, interaction: discord.Interaction):
        await self.function(interaction)

class PageButton(discord.ui.Button):
    def __init__(self, function, label, delta, style=discord.ButtonStyle.green):
        super().__init__(style=style, label=label)
        self.function = function
        self.delta = delta

    async def callback(self, interaction: discord.Interaction):
        await self.function(interaction, self.delta)

class StatsView(discord.ui.View):
    def __init__(self, cur, data, author, riot, server, icon_id, rank, count, days, set):
        super().__init__()

        self.cur = cur
        self.data = data
        self.author = author
        self.riot = riot
        self.server = server
        self.icon_id = icon_id
        self.rank = rank
        self.count = count
        self.days = days
        self.set = set
        
        self.process_function = process_stats
        self.embed_function = stats_embed
        self.stat_type = 'general'
        self.page_index = 0
        self.gamemode = ''
        self.mode_name = 'All Modes'
        
        self.add_default_buttons()

    def add_default_buttons(self, style=discord.ButtonStyle.blurple):
        self.clear_items()
        if self.stat_type in ['traits', 'augments']:
            #style = discord.ButtonStyle.gray
            self.add_page_buttons()
        self.add_item(NavigationButton(self.set_gamemode_buttons, label='Gamemode', style=style))
        self.add_item(NavigationButton(self.set_data_buttons, label='Data', style=style))
        self.add_item(NavigationButton(self.set_scope_buttons, label='Scope', style=style))

    def add_page_buttons(self):
        self.add_item(PageButton(self.change_page, '<', -4))
        self.add_item(PageButton(self.change_page, '>', 4))

    async def set_default_buttons(self, interaction):
        self.add_default_buttons()
        await interaction.response.edit_message(view=self)

    async def set_gamemode_buttons(self, interaction):
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        for label, gamemode in [['All Modes', 'all'], ['Ranked', 'ranked'], ['Hyper Roll', 'turbo'], ['Double Up', 'pairs']]:   # add ['Normal', 'normal'] for only unranked games
            self.add_item(EditButton(self.update_message, label=label, gamemode=gamemode, mode_name=label))
        await interaction.response.edit_message(view=self)

    async def set_data_buttons(self, interaction):
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        self.add_item(EditButton(self.update_message, label='General', stat_type='general'))
        self.add_item(EditButton(self.update_message, label='Traits', stat_type='traits'))
        self.add_item(EditButton(self.update_message, label='Augments', stat_type='augments'))
        await interaction.response.edit_message(view=self)

    async def set_scope_buttons(self, interaction):
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        self.add_item(NavigationButton(self.set_count_buttons, label='Last x games'))
        self.add_item(NavigationButton(self.set_time_buttons, label='Games during last'))
        self.add_item(EditButton(self.update_message, label='Whole Set', count='all'))
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
    

    async def update_message(self, interaction, mode_name=None, gamemode=None, count=None, days=None, stat_type=None):
        if count or days:
            self.count = count
            self.days = days
            if count == 'all':
                self.count = None
        if gamemode:
            self.gamemode = gamemode
            self.mode_name = mode_name
            if gamemode == 'all':
                self.gamemode = None
        if stat_type:
            self.stat_type = stat_type
            if stat_type == 'general':
                self.process_function = process_stats
                self.embed_function = stats_embed
            elif stat_type == 'traits':
                self.process_function = process_traits
                self.embed_function = traits_embed
            elif stat_type == 'augments':
                self.process_function = process_augments
                self.embed_function = augments_embed
                
        self.page_index = 0

        self.add_default_buttons()
            
        self.data, self.rank = self.process_function(self.cur, self.riot, self.server, self.count, self.days, self.set, display_mode=self.gamemode)
        if not self.rank:
            self.rank = 'Unranked'

        embed = self.embed_function(self.data, self.author, self.riot, self.icon_id, self.rank, mode_name=self.mode_name, index=self.page_index)
        await interaction.response.edit_message(embed=embed, view=self)

    async def change_page(self, interaction, delta):
        if 0 <= self.page_index + delta < len(self.data[self.stat_type]):
            self.page_index += delta
            embed = self.embed_function(self.data, self.author, self.riot, self.icon_id, self.rank, mode_name=self.mode_name, index=self.page_index) 
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.edit_message()


    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)