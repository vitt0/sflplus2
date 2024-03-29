from typing import TYPE_CHECKING, Any
import json
from PIL import Image
import pandas as pd
from pandas import DataFrame
import asyncio
import aiohttp
from datetime import datetime
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from priceapi import PriceAPI
from tabs.home import HomeTab
from tabs.top import TopTab
from tabs.bumpkin import BumpkinTab
from tabs.ranking import RankingTab
# if TYPE_CHECKING:
#     from pandas import Series
favicon: Any = Image.open("favicon.png")
st.set_page_config(
    page_title="SFL Plus",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"Get Help": None, "Report a bug": None, "About": None},
)
# st.write(
#     '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/
# bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1a
# oWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm"
# crossorigin="anonymous">',
#     unsafe_allow_html=True,
# )
def local_css(file_name) -> None:
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
class Main:
    def __init__(self) -> None:
        self.version = "v3.2"
        self.priceAPI: PriceAPI = PriceAPI()
        local_css("style.css")
        self.eth_price: float = self.priceAPI.retrieve_eth_price()
        self.matic_price: float = self.priceAPI.retrieve_matic_price()
        self.sfl_price: float = self.priceAPI.retrieve_sfl_price()
        self.sfl_supply: int | None = self.priceAPI.get_token_supply()
        # self.API_KEY_DUNE = st.secrets["api_dune"]
        # self.queries_owners: list[Any] = [100, None, None]
        # self.queries: list[str] = ["2649121", "2649118", "2427499"]  #
        # self.queries_name: list[str] = [
        #     "Emerald Turtle",
        #     "Tin Turtle",
        #     "Purple Trail",
        # ]  #
        # self.queries_quantity: list[str] = [
        #     "100 (SOLD OUT)",
        #     "3000",
        #     "10000",
        # ]  #
        # self.queries_emoji: list[str] = ["🐢", "🥫", "🐌"]  #
        # queries_ticket = ["3200", "1200", "500"]
        app_state_temp: dict[
            str, list[str]
        ] = st.experimental_get_query_params()
        # fetch the first item in each query string as we don't have multiple
        # values for each query string key in this example
        self.app_state: dict[str, str] = {
            k: v[0] if isinstance(v, list) else v
            for k, v in app_state_temp.items()
        }
        with open("data/skill_descriptions.json", "r", encoding="utf-8") as f:
            self.skills_description: dict[str, str] = json.load(f)
        with open("data/xp_data.json", "r", encoding="utf-8") as f:
            self.xp_dict: dict[int, dict[str, int | None]] = {
                int(k): v for k, v in json.load(f).items()
            }
        with open("data/wearables_sfl.json", "r", encoding="utf-8") as f:
            self.wearables_sfl: dict[str, int] = json.load(f)
        with open("data/inventory_items.json", "r", encoding="utf-8") as f:
            self.inventory_items: list[str] = json.load(f)
        with open("data/emojis.json", "r", encoding="utf-8") as f:
            self.emojis: dict[str, str] = json.load(f)
        with open("data/limits.json", "r", encoding="utf-8") as f:
            self.limits: dict[str, int] = json.load(f)
        self.fruits: list[str] = ["Apple", "Orange", "Blueberry"]
        self.fruits_price: dict[str, float] = {
            "Apple": 0.15625,
            "Orange": 0.1125,
            "Blueberry": 0.075,
        }
        self.fruit_emojis: dict[str, str] = {
            "Apple": " 🍎 ",
            "Orange": " 🍊 ",
            "Blueberry": " 🍇 ",
        }
        TopTab(self)
        tab1: DeltaGenerator
        tab2: DeltaGenerator
        tab3: DeltaGenerator
        tab1, tab2, tab3 = st.tabs(
            ["💾HOME", "🏆RANKING", "👥BUMPKIN"]
        )  # "📜NFT LIST", "👨‍🔬CALCULATOR", "💸TRADER"
        # Define default farm ID
        hometab = HomeTab(self, tab1)
        self.farm_id: str = hometab.get_farm_id()
        farm_tab_cons: dict[str, DeltaGenerator] = hometab.get_containers()
        ranktab = RankingTab(self, tab2)
        self.rank_tab_cons: dict[str, DeltaGenerator] = ranktab.get_containers()
        bumpkintab = BumpkinTab(self, tab3)
url_rank1 = "http://168.138.141.170:8080/api/v1/DawnBreakerTicket/ranking"

async def fetch(url, session: aiohttp.ClientSession) -> dict:
    async with session.get(url, timeout=5) as response:
        return await response.json()

async def main() -> None:
    main_app = Main()
    try:
        async with aiohttp.ClientSession() as session:
            try:
                data1 = await fetch(url_rank1, session)
            except Exception as e:
                main_app.rank_tab_cons["live_update"].error(
                    "The ranking is currently not working, will be fixed soon™"
                )
                return
            # data2 = await fetch(url_rank2, session)

        df1 = pd.DataFrame(
            {
                "Farm": [farm["FarmID"] for farm in data1["farms"]],
                "Bumpkin XP": [
                    farm["B_XP"]
                    if "B_XP" in farm
                    and farm["B_XP"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Expansion": [
                    farm["Land"]
                    if "Land" in farm
                    and farm["Land"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "SFL Earn": [
                    farm["B_EA"]
                    if "B_EA" in farm
                    and farm["B_EA"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "SFL Spent": [
                    farm["B_SP"]
                    if "B_SP" in farm
                    and farm["B_SP"] != ""
                    else None
                    for farm in data1["farms"]
                ],                
            }
        )

        df2 = pd.DataFrame(
            {
                "Farm": [farm["FarmID"] for farm in data1["farms"]],
                "Sunflowers": [
                    farm["B_SU"]
                    if "B_SU" in farm
                    and farm["B_SU"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Trees": [
                    farm["B_WO"]
                    if "B_WO" in farm
                    and farm["B_WO"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Stone": [
                    farm["B_ST"]
                    if "B_ST" in farm
                    and farm["B_ST"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Iron": [
                    farm["B_IR"]
                    if "B_IR" in farm
                    and farm["B_IR"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Gold": [
                    farm["B_GO"]
                    if "B_GO" in farm
                    and farm["B_GO"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Shovels": [
                    farm["B_SH"]
                    if "B_SH" in farm
                    and farm["B_SH"] != ""
                    else None
                    for farm in data1["farms"]
                ],
                "Drills": [
                    farm["B_DR"]
                    if "B_DR" in farm
                    and farm["B_DR"] != ""
                    else None
                    for farm in data1["farms"]
                ],                    
            }
        )

        # df3 = pd.DataFrame(
        #     {
        #         "Farm": [farm["FarmID"] for farm in data1["farms"]],
        #         "Bottles": [
        #             farm["OldBottle"]
        #             if "OldBottle" in farm and farm["OldBottle"] != ""
        #             else 0
        #             for farm in data1["farms"]
        #         ],
        #         "Seaweed": [
        #             farm["Seaweed"]
        #             if "Seaweed" in farm and farm["Seaweed"] != ""
        #             else 0
        #             for farm in data1["farms"]
        #         ],
        #         "Iron C.": [
        #             farm["IronCompass"]
        #             if "IronCompass" in farm and farm["IronCompass"] != ""
        #             else 0
        #             for farm in data1["farms"]
        #         ]
                # 'Davy Jones': ['YES' if int(farm.get('DavyJones', 0)) >= 1
                # else 'NO' for farm in data1['farms']]
        #     }
        # )

        # Remove rows with missing ticket counts
        df1: DataFrame = df1.dropna(subset=["Bumpkin XP"])
        # df3 = df3.dropna(subset=['Wild Mushroom'])

        # Convert Total Ticket column to numeric values
        df1["Bumpkin XP"] = pd.to_numeric(df1["Bumpkin XP"])
        df1['Bumpkin XP'] = df1['Bumpkin XP'].round(2)
        df1["Expansion"] = pd.to_numeric(df1["Expansion"])
        df1["SFL Earn"] = pd.to_numeric(df1["SFL Earn"])
        df1['SFL Earn'] = df1['SFL Earn'].round(2)
        df1["SFL Spent"] = pd.to_numeric(df1["SFL Spent"])
        df1['SFL Spent'] = df1['SFL Spent'].round(2)

        
        # Create a new column "Level" in the DataFrame
        df1["Level"] = None  # Initialize the "Level" column with None
        
        # Iterate through the DataFrame rows and determine the level based on "Bumpkin XP"
        for index, row in df1.iterrows():
            bump_xp = row["Bumpkin XP"]
            current_lvl = None
            
            for level, info in main_app.xp_dict.items():
                if bump_xp >= info["Total XP"]:
                    current_lvl = level
        
            if current_lvl is None:
                current_lvl = max(main_app.xp_dict.keys())
            
            df1.at[index, "Level"] = current_lvl
        
        #reorder columns
        df1 = df1[["Farm", "Level", "Bumpkin XP", "Expansion", "SFL Earn", "SFL Spent"]]

        
        # df2["Week 8"] = pd.to_numeric(df2["Week 8"])
        # df3["Bottles"] = pd.to_numeric(df3["Bottles"])
        # df3["Seaweed"] = pd.to_numeric(df3["Seaweed"])
        # df3["Iron C."] = pd.to_numeric(df3["Iron C."])

        # df3["Points"] = (
        #     df3["Bottles"].clip(upper=50) * 1.2
        #     + df3["Seaweed"].clip(upper=25) * 0.4
        #     + df3["Iron C."].clip(upper=15) * 2
        # )

        # Reorder the columns
        # df3 = df3.reindex(columns=['Farm', 'Points', 'Old Bottle',
        # 'Seaweed', 'Iron Compass'])
        # Format the Points column
        # df3["Points"] = df3["Points"].round(2)
        # df3['Points'] = df3['Points'].apply(lambda x: f'{x:.2f}')

        # Sort by Total Ticket in descending order
        df1 = df1.sort_values(by="Bumpkin XP", ascending=False)
        df2 = df2.sort_values(by="Sunflowers", ascending=False)
        # df3: DataFrame = df3.sort_values(by="Points", ascending=False)
        # ['Bottles', 'Iron C.', 'Seaweed'],
        # ascending=[False, False, False], kind='mergesort')

        df1 = df1.rename(columns={"Bumpkin XP": "Bumpkin XP 🔻"})
        df2 = df2.rename(columns={"Sunflowers": "Sunflowers 🔻"})

        # Reset index and set the "Ranking" column as the new index
        df1 = df1.reset_index(drop=True)
        df2 = df2.reset_index(drop=True)
        # df3 = df3.reset_index(drop=True)

        df1.index = df1.index + 1
        df2.index = df2.index + 1
        # df3.index = df3.index + 1

        # Rename the index to "Ranking"
        df1.index.name = "Rank"
        df2.index.name = "Rank"
        # df3.index.name = "Rank"

        # Convert index to integer values
        df1.index = df1.index.astype(int)
        df2.index = df2.index.astype(int)
        # df3.index = df3.index.astype(int)

        if df1.empty:
            main_app.rank_tab_cons["live_update"].error(
                " The ranking is currently not working, it will be fixed soon™ "
            )
        else:
            in_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
            out_fmt = "%Y-%m-%d %H:%M"
            update: str = datetime.strptime(
                data1["updatedAt"], in_fmt
            ).strftime(out_fmt)
            main_app.rank_tab_cons["live_update"].success(
                f"🕘Updated at: **{update} UTC**"
            )
          
            main_app.rank_tab_cons["live_xp"].write(df1)
            main_app.rank_tab_cons["live_resources"].write(df2)
        pass
    except Exception as e:
        main_app.rank_tab_cons["live_update"].error(
            f" 3 The ranking is currently not working, it will be fixed soon™, "
            + f"Error: {str(e)}"
        )
if __name__ == "__main__":
    asyncio.run(main())
    
# with tab8:
#     col_nft, buff11 = st.columns([2,2])
#     with col_nft:
#         st.error(f"The NFT List is momentarely disable,
# it will be enable back soon™")
