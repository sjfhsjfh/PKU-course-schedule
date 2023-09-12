import logging
import os
import unittest

import PKULogin

from PKUCourse import logger


logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

logger.addHandler(console_handler)


class Test(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.username = os.environ["PKU_STUDENT_ID"]
        self.password = os.environ["PKU_PASSWORD"]

    def test_html(self):
        logger.info("Test Login & get course html")
        login = PKULogin.SyllabusLogin(self.username, self.password)
        login.login()

        res = login.session.get(
            'https://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/electiveWork/showResults.do'
        )

        self.assertEqual(res.status_code, 200)
        self.assertIn("<title>选课结果</title>", res.text)

        self.html = res.text

    def test_parse(self):
        logger.info("Test parse course html")
        from PKUCourse import PKUClass

        self.test_html()

        classes = PKUClass.from_html(self.html)

        self.assertGreater(len(classes), 0)

        for pku_class in classes:
            logger.info(pku_class.info)
            pku_class.parse_info()
            for schedule in pku_class.classes:
                logger.info(schedule)
