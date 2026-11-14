"""
Everything else a demo holds lands somewhere: the players' whole state, every
other event, teammates' hits, the chat, grenade flights, the game's state,
the players' profiles - on the hand-built demo with those added.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from heat3d_cs2.match import build_match
from heat3d_cs2.output import table
from heat3d_cs2.stats import summary

from .fixtures import hurt, player_columns, two_rounds


def everything():
    raw = two_rounds()
    s = raw.samples
    n = len(s)
    s["flash_duration"] = np.where(s["tick"] == 1240, 2.5, 0.0)
    s["has_helmet"] = True
    s["inventory"] = [["Glock-18", "AK-47"]] * n
    s["approximate_spotted_by"] = [[]] * n
    s["aim_punch_angle"] = [[1.5, -0.5, 0.0]] * n
    s["kills_total"] = (s["tick"] >= 1280).astype(int)
    s["crosshair_code"] = "CSGO-test"
    s["is_bomb_planted"] = s["tick"] >= 4000
    ev = raw.events
    ev["chat_message"] = pd.DataFrame(
        [{"tick": 1100, **player_columns("user", "3", 1100), "chat_message": "gl hf", "is_warmup_period": False}]
    )
    ev["item_pickup"] = pd.DataFrame(
        [{"tick": 700, **player_columns("user", "1", 700), "item": "ak47", "defindex": 7, "silent": False, "is_warmup_period": False}]
    )
    ev["server_message"] = pd.DataFrame([{"tick": 650, "server_message": "Live!", "is_warmup_period": False}])
    ev["fire_bullets"] = pd.DataFrame(
        [{"tick": 1270, **player_columns("user", "1", 1270), "inaccuracy": 0.004, "recoil_index": 0.0, "player": 7}]
    )
    # A teammate's hit: in the table, not in the statistics.
    ev["player_hurt"] = pd.concat([ev["player_hurt"], pd.DataFrame([hurt(1250, "2", "1", 12, 88, weapon="hegrenade")])])
    ticks = np.arange(1200, 1291)
    raw.grenades = pd.DataFrame(
        {
            "grenade_type": ["CSmokeGrenadeProjectile"] * len(ticks) + ["CSmokeGrenade"],
            "grenade_entity_id": [501] * (len(ticks) + 1),
            "x": list(np.linspace(120.0, 50.0, len(ticks))) + [np.nan],
            "y": list(np.linspace(10.0, 60.0, len(ticks))) + [np.nan],
            "z": [-150.0] * (len(ticks) + 1),
            "tick": list(ticks) + [1190],
            "steamid": ["2"] * (len(ticks) + 1),
            "name": ["ash"] * (len(ticks) + 1),
        }
    )
    ev["smokegrenade_detonate"]["entityid"] = 501
    return build_match([raw], "alpha-vs-bravo-m1-test")


@pytest.fixture(scope="module")
def match():
    return everything()


def test_the_players_state_on_every_sample(match):
    pos = match.rows[match.rows["event"] == "position"]
    assert set(pos["helmet"]) == {1.0} and set(pos["inventory"]) == {"Glock-18|AK-47"}
    assert pos["punchPitch"].iloc[0] == 1.5 and pos["punchYaw"].iloc[0] == -0.5
    assert pos.loc[pos["time"] == pos["time"].max(), "killsTotal"].max() == 1



def test_events_carry_the_players_state_and_rounds_their_pay(match):
    rows = match.rows
    named = rows[(rows["steamid"] != "") & (rows["event"] != "position")]
    held = named[named["state_helmet"].notna()]
    assert len(held) and set(held["state_helmet"]) == {1.0} and set(held["state_utility"]) == {0.0}
    assert set(held["inventory"]) == {"Glock-18|AK-47"}
    ends = rows[rows["event"] == "round_end"]
    assert len(ends) and set(ends["won"]) <= {0.0, 1.0} and (ends["earn_round_cs2"] >= 0).all()


def test_other_events_are_rows_where_the_player_was(match):
    rows = match.rows
    (chat,) = rows[rows["event"] == "chat"].itertuples()
    assert (chat.player, chat.text, chat.side) == ("bob", "gl hf", "CT")
    (pick,) = rows[rows["event"] == "item_pickup"].itertuples()
    assert pick.weapon == "AK-47" and json.loads(pick.detail) == {"defindex": 7, "item": "ak47", "silent": False}
    assert pick.phase == "live"


def test_a_shot_carries_the_games_account_of_its_bullets(match):
    shot = match.rows[match.rows["event"] == "shot"].iloc[0]
    assert json.loads(shot["detail"])["inaccuracy"] == 0.004
    assert set(match.rows.loc[match.rows["event"] == "slash", "weapon"]) == {"Knife"}


def test_a_teammates_hit_is_a_row_but_not_a_statistic(match):
    hurt_rows = match.rows[match.rows["event"] == "hurt"]
    team = hurt_rows[(hurt_rows["player"] == "ace") & (hurt_rows["other"] == "ash")]
    assert len(team) == 1 and team["damage"].iloc[0] == 12 and team["health"].iloc[0] == 88
    assert not ((match.damage["victim"] == "ace") & (match.damage["attacker"] == "ash")).any()


def test_a_grenades_flight_ends_where_it_went_off(match):
    flight = match.rows[match.rows["event"] == "grenade"].sort_values("time")
    assert set(flight["entity"]) == {501} and set(flight["weapon"]) == {"Smoke Grenade"}
    assert (flight["x"].iloc[-1], flight["y"].iloc[-1]) == pytest.approx((50.0, 60.0))
    smoke = match.rows[match.rows["event"] == "smoke"].iloc[0]
    assert smoke["entity"] == 501


def test_the_summary_keeps_the_rest(match):
    doc = summary(match)
    assert doc["chat"] == [{"time": doc["chat"][0]["time"], "round": 1, "player": "bob", "side": "CT", "text": "gl hf"}]
    (message,) = [e for e in doc["events"] if e["event"] == "server_message"]
    assert message["server_message"] == "Live!" and message["time"] == pytest.approx(650 / 64, abs=0.001)
    assert {"field": "is_bomb_planted", "value": True} in [{k: v for k, v in e.items() if k != "time"} for e in doc["state"]]
    assert doc["profiles"]["1"]["crosshair_code"] == "CSGO-test"
    json.dumps(doc)


def test_the_table_writes(match):
    t = table(match)
    assert {"detail", "text", "entity", "inventory", "helmet", "killsTotal"} <= set(t.column_names)
