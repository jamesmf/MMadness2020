import pandas as pd  # type: ignore
import numpy as np  # type: ignore
import os
from collections import defaultdict
from typing import List, Dict, Union, Any
import typing


class GameDF:
    team1: int = 0
    team2: int = 0
    team1_ord: int = 0
    team2_ord: int = 0
    score: int = 0
    t1_wins: int = 0


MAX_ORD = 355


class DataHolder:
    def __init__(self, path: str):
        """
        path: path to folder
        """
        if path.find("women") > -1:
            self.comp = "womens"
        else:
            self.comp = "mens"
        self.tourney_results = pd.read_csv(
            os.path.join(path, "MNCAATourneyCompactResults.csv")
        )
        self.season_results = pd.read_csv(
            os.path.join(path, "MNCAATourneyCompactResults.csv")
        )
        massey = pd.read_csv(os.path.join(path, "MMasseyOrdinals.csv"))

        # we care about the POM ratings for now
        massey = massey[massey.SystemName == "POM"]
        # short term, we'll use the max POM < 129
        masseymax = np.max([i for i in massey.RankingDayNum.values if i < 129])
        massey = massey[massey.RankingDayNum == masseymax]
        massey_dict: Dict[int, Dict[int, int]] = defaultdict(
            lambda: defaultdict(lambda: MAX_ORD)
        )
        for season, team, ord in massey[["Season", "TeamID", "OrdinalRank"]].values:
            massey_dict[season][team] = ord
        self.massey = massey_dict

    def create_game_df(self) -> GameDF:
        df = self.season_results.copy()
        df["team1_ord"] = df[["Season", "WTeamID"]].apply(
            lambda x: self.massey[x["Season"]][x["WTeamID"]], axis=1
        )
        df["team2_ord"] = df[["Season", "LTeamID"]].apply(
            lambda x: self.massey[x["Season"]][x["LTeamID"]], axis=1
        )
        df["score"] = df["WScore"] - df["LScore"]
        df["t1_wins"] = (df["score"] > 0) * 1

        return typing.cast(GameDF, df)
