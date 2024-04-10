from scripts.process_data import process_single_match
from scripts.get_embeds import single_match_embed
from views.baseview import View, PageButton

class MatchView(View):
    def __init__(self, cur, match_ids, riot, server, icon_id, rank, id_index=0):
        super().__init__()

        self.cur = cur
        self.match_ids = match_ids
        self.server = server
        self.riot = riot
        self.icon_id = icon_id
        self.rank = rank
        self.id_index = id_index

        self.add_page_butons()

    def add_page_butons(self):
        self.add_item(PageButton(self.change_page, '<', -1))
        self.add_item(PageButton(self.change_page, '>', 1))

    async def change_page(self, interaction, delta):
        if 0 <= self.id_index + delta < len(self.match_ids):
            self.id_index += delta

        data = process_single_match(self.cur, self.riot, self.server, self.match_ids[self.id_index])

        embed = single_match_embed(data, None, self.riot, self.icon_id, self.rank)

        await interaction.response.edit_message(embed=embed)