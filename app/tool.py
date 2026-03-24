import json
import time
import random
import string
import requests
import importlib

from typing import Any
from pathlib import Path

from third_party.pcrdapi import pcrdapi


class Tool:
    def __init__(self) -> None:
        self.url = "https://api.pcrdfans.com/x/v1/search"
        self.pcr_map = load_pcr_map()

    def parse_def(self, message: str) -> list[int]:
        tag, *alias_list = message.split()
        if tag != "怎么拆":
            return []

        chara_list = [self.pcr_map.get(alias, None) for alias in alias_list]
        chara_list = [chara * 100 + 1 for chara in chara_list if chara]
        return chara_list

    def parse_akt(self, chara_list: list[int]) -> list[str]:
        chara_list = [chara - 1 for chara in chara_list]
        chara_list = [int(chara / 100) for chara in chara_list]
        messages: list[str] = [self.pcr_map[chara][0] for chara in chara_list]
        return messages

    def query(self, chara_list: list[int]) -> dict[str, Any]:
        data = {
            "def": chara_list,  # 角色ID列表
            "language": 0,  # 0:中文
            "nonce": get_nonce(),
            "page": 1,
            "region": 2,  # 2:国服 3:台服
            "sort": 1,  # 1:综合排序 2:按时间排序
            "ts": get_time(),
        }
        data_str = dump_to_str(data)
        data["_sign"] = pcrdapi.sign(data_str, data["nonce"])

        playload = dump_to_str(data).encode()
        resp = requests.post(self.url, headers=get_headers(), data=playload)
        return resp.json()


def load_pcr_map() -> dict[str | int, Any]:
    _pcr_data_path = Path("third_party/LandosolRoster/_pcr_data.py")
    pcr_data_path = Path(__file__).parent / "pcr_data.py"

    if not pcr_data_path.exists():
        if not _pcr_data_path.exists():
            return {}
        pcr_data_path.write_text(_pcr_data_path.read_text())

    from app import pcr_data  # type: ignore  # noqa: F811

    importlib.reload(pcr_data)

    pcr_map: dict[str | int, Any] = pcr_data.CHARA_NAME.copy()  # type: ignore
    pcr_map.update(
        {
            alias: chara
            for chara, alias_list in pcr_data.CHARA_NAME.items()
            for alias in alias_list
        }
    )

    return pcr_map


def dump_to_str(data: dict[str, str]) -> str:
    return json.dumps(data, ensure_ascii=False).replace(" ", "")


def get_headers() -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
        "Referer": "https://pcrdfans.com/",
        "Origin": "https://pcrdfans.com",
        "Accept": "*/*",
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "",
        "Host": "api.pcrdfans.com",
    }


def get_nonce() -> str:
    char = string.digits + string.ascii_lowercase
    return "".join(random.choices(char, k=16))


def get_time() -> int:
    return int(time.time())
