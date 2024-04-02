import discord
from scripts.get_embeds import stats_embed

class StatsView(discord.ui.View):
    
    async def update_message(self, display_mode):
        data, author, riot, icon_id, rank = self.embed_data
        embed = stats_embed(data, author, riot, icon_id, rank, display_mode)
        await self.message.edit(embed=embed, view=self)

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.interaction.edit_original_response(view=self)
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)


    @discord.ui.button(label="All Modes", 
                       style=discord.ButtonStyle.blurple)
    async def all(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_message('all')
    

    @discord.ui.button(label="Standard", 
                       style=discord.ButtonStyle.grey)
    async def standard(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_message('standard')
        
        
    @discord.ui.button(label="Hyper Roll", 
                       style=discord.ButtonStyle.gray)
    async def turbo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_message('turbo')
        

    @discord.ui.button(label="Double Up", 
                       style=discord.ButtonStyle.green)
    async def pairs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await self.update_message('pairs')