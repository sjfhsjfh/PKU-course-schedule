from __future__ import annotations

import re
import time

from typing import List, Tuple


DEFAULT_SCHEDULE: List[Tuple[Tuple[int, int], Tuple[int, int]]] = [
    ((8, 0), (8, 50)),
    ((9, 0), (9, 50)),
    ((10, 10), (11, 0)),
    ((11, 10), (12, 0)),
    ((13, 0), (13, 50)),
    ((14, 0), (14, 50)),
    ((15, 10), (16, 0)),
    ((16, 10), (17, 0)),
    ((17, 10), (18, 0)),
    ((18, 40), (19, 30)),
    ((19, 40), (20, 30)),
]

WEEKDAYS = {
    "一": 0,
    "Mon": 0,
    "二": 1,
    "Tue": 1,
    "三": 2,
    "Wed": 2,
    "四": 3,
    "Thu": 3,
    "五": 4,
    "Fri": 4,
    "六": 5,
    "Sat": 5,
    "日": 6,
    "Sun": 6,
}
"""
星期几的映射, 从 0 开始!!!!!
Example:
    "一": 0,
    "Mon": 0
"""

WEEKTYPE = {
    "每": 0,
    "单": 1,
    "双": 2,
}


class Schedule:

    class_schedule: List[
        Tuple[Tuple[int, int], Tuple[int, int]]
    ] = DEFAULT_SCHEDULE

    def __init__(
            self,
            weekday: int,
            duration: Tuple[int, int],
            type: int = 0,
    ) -> None:
        """
        weekday: 星期几, 从 0 开始!!!!!
        duration: 第几节到第几节课, 从 0 开始!!!!!
        type: 0: 每周, 1: 单周, 2: 双周
        """

        self.duration: Tuple[int, int] = duration
        """第几节到第几节课, 从 0 开始!!!!!"""

        self.weekday: int = weekday
        """星期几, 从 0 开始!!!!!"""

        self.type: int = type
        """0: 每周, 1: 单周, 2: 双周"""

    def __str__(self) -> str:
        return f"星期{'一二三四五六日'[self.weekday]} 第 {self.duration[0] + 1}-{self.duration[1] + 1} 节"

    @property
    def start_time(self) -> Tuple[int, int]:
        return self.class_schedule[self.duration[0]][0]

    @property
    def end_time(self) -> Tuple[int, int]:
        return self.class_schedule[self.duration[1]][1]

    @property
    def is_today(self) -> bool:
        """是否是今天"""

        return self.weekday == time.localtime().tm_wday

    @staticmethod
    def from_str(s: str) -> Schedule | None:
        """从单行字符串解析出 Schedule"""

        s = s.strip()

        # 至尊无敌正则表达式
        re_res = re.search(
            fr"(?P<week_type>[单双每])周周(?P<weekday>{'|'.join(WEEKDAYS.keys())})(?P<duration_from>\d+)~(?P<duration_to>\d+)节",
            s
        )
        if re_res is None:
            return None

        week_type = WEEKTYPE.get(re_res.group("week_type"))
        weekday = WEEKDAYS.get(re_res.group("weekday"))
        duration_from = int(re_res.group("duration_from")) - 1
        duration_to = int(re_res.group("duration_to")) - 1

        if week_type is None or weekday is None:
            return None

        return Schedule(
            weekday=weekday,
            duration=(duration_from, duration_to),
            type=week_type
        )
