from __future__ import annotations

import bs4
import enum
import logging
import re

from typing import Any, List, Literal, Tuple

logger = logging.getLogger(__name__)


TRANSLATION_TABLE = {
    "zh-CN": {
        "课程名": "course_name",
        "课程类别": "course_type",
        "学分": "credit",
        "周学时": "course_periods",
        "教师": "teacher",
        "班号": "class_no",
        "开课单位": "faculty",
        "教室信息": "info",
        "选课结果": "result",
        "IP地址": "ip",
        "操作时间": "operation_time",
    }
}
BUILDINGS = {
    "理教": "理科教学楼",
    "地学": "地学",
    "二教": "第二教学楼",
    "三教": "第三教学楼",
}


def translate(src: dict, from_lang: str) -> dict:
    """
    Translate a dict from one language to English
    Keys not in the translation table will be ignored
    Key name is all given in camel case
    """
    res = {}
    if from_lang not in TRANSLATION_TABLE:
        raise ValueError("Invalid language")
    translation = TRANSLATION_TABLE[from_lang]
    for key, value in src.items():
        translated_key = translation.get(key)
        if translated_key is not None:
            res[translated_key] = value
        else:
            logger.warning(f"Key {key} not found in translation table")
            res[key] = value
    return res


class CourseType(enum.StrEnum):
    """
    课程类别
    """

    MAJOR_REQUIRED = enum.auto()
    """专业必修"""
    ALL_REQUIRED = enum.auto()
    """全校必修"""
    MAJOR_LIMITED = enum.auto()
    """限选"""
    ANY = enum.auto()
    """任选"""
    PUBLIC_I = enum.auto()
    """通识课(通选课I)"""
    PUBLIC_II = enum.auto()
    """通识课(通选课II)"""
    PUBLIC_III = enum.auto()
    """通识课(通选课III)"""
    PUBLIC_IV = enum.auto()
    """通识课(通选课IV)"""
    PUBLIC_V = enum.auto()
    """通识课(通选课V)"""
    PUBLIC_CORE_I = enum.auto()
    """通识课(通识核心课I)"""
    PUBLIC_CORE_II = enum.auto()
    """通识课(通识核心课II)"""
    PUBLIC_CORE_III = enum.auto()
    """通识课(通识核心课III)"""
    PUBLIC_CORE_IV = enum.auto()
    """通识课(通识核心课IV)"""
    PUBLIC_CORE_V = enum.auto()
    """通识课(通识核心课V)"""
    UNKNOWN = enum.auto()

    @classmethod
    def _missing_(cls, value: str) -> CourseType:
        TRANSLATION_TABLE = {
            "专业必修": "MAJOR_REQUIRED",
            "全校必修": "ALL_REQUIRED",
            "限选": "MAJOR_LIMITED",
            "任选": "ANY",
            "通识课(通选课I)": "PUBLIC_I",
            "通识课(通选课II)": "PUBLIC_II",
            "通识课(通选课III)": "PUBLIC_III",
            "通识课(通选课IV)": "PUBLIC_IV",
            "通识课(通选课V)": "PUBLIC_V",
            "通识课(通识核心课I)": "PUBLIC_CORE_I",
            "通识课(通识核心课II)": "PUBLIC_CORE_II",
            "通识课(通识核心课III)": "PUBLIC_CORE_III",
            "通识课(通识核心课IV)": "PUBLIC_CORE_IV",
            "通识课(通识核心课V)": "PUBLIC_CORE_V",
        }
        res = TRANSLATION_TABLE.get(value)
        if res is not None:
            return cls(res)
        else:
            return cls.UNKNOWN


class PKUCourse:
    """同一个课程可能有多个班级，但是 课程名, 课程类别, 学分, 周学时, 开课单位 相同"""

    def __init__(
            self,
            name: str | None = None,
            course_type: CourseType | str | None = None,
            credit: int | float | None = None,
            course_periods: int | float | None = None,
            faculty: str | None = None,
            course_id: int | None = None,
            *args: Any,
            **kwargs: Any,
    ) -> None:

        self.name: str | None = kwargs.get("course_name", name)
        """课程名"""

        if isinstance(course_type, str):
            course_type = CourseType(course_type)
        self.course_type: CourseType | None = course_type
        """课程类别"""

        self.credit: float | None = None if (credit is None) else float(credit)
        """学分"""

        self.course_periods: float | None = None if (
            course_periods is None) else float(course_periods)
        """周学时"""

        self.faculty: str | None = faculty
        """开课单位"""

        self.course_id: int | None = None if (
            course_id is None) else int(course_id)
        """课程ID"""


class PKUClass:
    """班级 包含课程信息"""

    def __init__(
        self,
        course: PKUCourse,
        teachers: List[str] | None = None,
        location: str | None = None,
        classes: List[Schedule] | None = None,
        info: str | None = None,
        result: str | None = None,
        remarks: str = "",
        *args: Any,
        **kwargs: Any
    ) -> None:

        self.course: PKUCourse = course
        """课程信息"""

        self.teachers: List[str] | None = teachers
        """教师"""

        self.location: str | None = location
        """上课地点"""

        self.classes: List[Schedule] | None = classes
        """上课时间"""

        self.info: str | None = info
        """备注级别的好几项信息"""

        self.result: str | None = result
        """选课结果"""

        self.remarks: str = remarks
        """备注"""

    def __str__(self) -> str:
        return f"PKUClass({self.name})"

    @property
    def name(self) -> str | None:
        return self.course.name

    @property
    def course_type(self) -> CourseType | None:
        return self.course.course_type

    @property
    def credit(self) -> float | None:
        return self.course.credit

    @property
    def course_periods(self) -> float | None:
        return self.course.course_periods

    @property
    def faculty(self) -> str | None:
        return self.course.faculty

    @classmethod
    def from_dict(cls, src: dict) -> PKUClass:
        course = PKUCourse(**src)
        return cls(course=course, **src)

    @classmethod
    def from_html(cls, html: str) -> List[PKUClass]:
        soup = bs4.BeautifulSoup(html, 'html.parser')
        class_list = []

        fields = [
            field.text.strip()
            for field in soup.select('tr.datagrid-header th')
        ]
        for row in soup.select('tr.datagrid-all, tr.datagrid-odd, tr.datagrid-even'):
            course_dict = {}
            for field, value in zip(fields, row.select('td.datagrid')):
                # Process <br> or similar tags
                text: str = '\n'.join(
                    [text.strip() for text in value.stripped_strings]
                )
                course_dict[field] = text
            translated = translate(course_dict, "zh-CN")
            class_list.append(cls.from_dict(translated))

        return class_list

    def parse_info(info: str) -> dict:
        """
        最抽象的一集

        要把 上课时间, 上课地点, 考试时间, 考试类型, 备注 这些东西从同一个字符串中解析出来
        """

        # Multiline string
        lines = info.splitlines()

        res = {}

        for line in lines:

            # # 上课时间:
            # 1. 最基础的类型:
            # Example:
            # 1~16周 每周周五10~11节

            res.update({})  # TODO

            # # 上课地点:
            # 1. 常见类型:
            # Example:
            # 理教101

            pattern = fr"(?P<building>{'|'.join(BUILDINGS.keys())})(?P<room>\d+)"
            re_res = re.search(pattern, line)
            if re_res is not None:
                location = {
                    "building": BUILDINGS[re_res.group("building")],
                    "room": re_res.group("room")
                }
                loc_str = f"{location['building']} {location['room']}"
                res.update({
                    "location": loc_str
                })

            # # 考试相关信息:
            # 1. 套话:
            # Example:
            # 考试方式：堂考、论文、或统一时间考试
            if re.match(r"考试方式：堂考、论文、或统一时间考试$", line) is not None:
                res.update({
                    "exam_info": "堂考、论文、或统一时间考试"
                })

            # 2. 有时间的:
            # Example:
            # 考试时间：20240105下午；
            re_res = re.match(r"考试时间：(?P<exam_time>[^;；]*)[;；]?$", line)
            if re_res is not None:
                res.update({
                    "exam_info": {
                        "time": re_res.group("exam_time")
                    }
                })

        return res


class Schedule:
    def __init__(self: Schedule, cal: int, time: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
        self.cal: int = cal
        self.start_time: Tuple[int, int] = time[0]
        self.stop_time: Tuple[int, int] = time[1]
