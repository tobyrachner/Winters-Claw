import discord

from scripts.get_embeds import stats_embed, traits_embed, augments_embed, units_embed
from scripts.process_data import process_stats, process_traits, process_augments, process_units
from views.baseview import View, EditButton, PageButton, NavigationButton

class StatsView(View):
    def __init__(self, cur, author, author_id, data, riot, puuid, icon_id, rank, count, days, set):
        super().__init__()

        self.cur = cur
        self.data = data
        self.author = author
        self.author_id = author_id
        self.riot = riot
        self.puuid = puuid
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
        self.sort_by = 'count'
        self.descending = True
        
        self.add_default_buttons()

    def add_default_buttons(self, style=discord.ButtonStyle.blurple, row=None):
        self.clear_items()
        data_style = discord.ButtonStyle.green
        if self.stat_type in ['traits', 'augments', 'units']:
            self.add_page_buttons(row=2)
            self.add_item(NavigationButton(self.set_sort_buttons, label='Sort', style=style, row=2))
            style = discord.ButtonStyle.gray
            data_style = discord.ButtonStyle.gray
        self.add_item(NavigationButton(self.set_data_buttons, label='Data', style=data_style, row=row))
        self.add_item(NavigationButton(self.set_gamemode_buttons, label='Gamemode', style=style, row=row))
        self.add_item(NavigationButton(self.set_scope_buttons, label='Scope', style=style, row=row))

    def add_page_buttons(self, row=None):
        self.add_item(PageButton(self.change_page, '<', -4, row=row))
        self.add_item(PageButton(self.change_page, '>', 4, row=row))

    async def set_default_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.add_default_buttons()
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

    async def set_scope_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons))
        self.add_item(NavigationButton(self.set_count_buttons, label='Last x games'))
        self.add_item(NavigationButton(self.set_time_buttons, label='Games during last'))
        self.add_item(EditButton(self.update_message, label='Whole Set', count='all'))
        await interaction.response.edit_message(view=self)

    async def set_count_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.clear_items()
        self.add_item(NavigationButton(self.set_scope_buttons))
        for num in [100, 50, 20, 10]:
            self.add_item(EditButton(self.update_message, label=str(num), count=num))
        await interaction.response.edit_message(view=self)

    async def set_time_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.clear_items()
        self.add_item(NavigationButton(self.set_scope_buttons))
        for label, days in [['Month', 30], ['Week', 7], ['24h', 1]]:
            self.add_item(EditButton(self.update_message, label=label, days=days))
        await interaction.response.edit_message(view=self)

    async def set_sort_buttons(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        self.clear_items()
        self.add_item(NavigationButton(self.set_default_buttons, row=2))
        for label, filter in [['Count', 'count'], ['Avg. Placement', 'avg'], ['Win%', 'win%'], ['Top 4%', 'top4%']]:
            self.add_item(EditButton(self.update_message, label=label, sort_by=filter))
        self.add_item(EditButton(self.update_message, style=discord.ButtonStyle.green, label='↓', descending=True, row=2))
        self.add_item(EditButton(self.update_message, style=discord.ButtonStyle.green, label='↑', descending=False, row=2))
        await interaction.response.edit_message(view=self)
    

    async def update_message(self, interaction, mode_name=None, gamemode=None, count=None, days=None, stat_type=None, sort_by=None, descending=None, toggle_match_ids=None):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
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
            elif stat_type == 'units':
                self.process_function = process_units
                self.embed_function = units_embed
            elif stat_type == 'augments':
                self.process_function = process_augments
                self.embed_function = augments_embed
        if sort_by:
            self.sort_by = sort_by
        if descending is not None:
            if self.sort_by == 'avg':
                descending = not descending
            self.descending = descending
                
        self.page_index = 0

        if sort_by is None and descending is None: 
            self.add_default_buttons()
            
        self.data, self.rank = self.process_function(self.cur, self.puuid, self.count, self.days, self.set, display_mode=self.gamemode, filter=self.sort_by, descending=self.descending)
        if not self.rank:
            self.rank = 'Unranked'

        embed = self.embed_function(self.data, self.author, self.riot, self.icon_id, self.rank, mode_name=self.mode_name, index=self.page_index)
        await interaction.response.edit_message(embed=embed, view=self)

    async def change_page(self, interaction, delta):
        if interaction.user.id != self.author_id:
            await interaction.response.edit_message()
            return
        if 0 <= self.page_index + delta < len(self.data[self.stat_type]):
            self.page_index += delta
            embed = self.embed_function(self.data, self.author, self.riot, self.icon_id, self.rank, mode_name=self.mode_name, index=self.page_index) 
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.edit_message()