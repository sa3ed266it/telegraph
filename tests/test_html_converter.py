from unittest import TestCase

from telegraph.exceptions import NotAllowedTag, InvalidHTML
from telegraph.utils import html_to_nodes, nodes_to_html

HTML_TEST_STR = """
<p>Hello, world!<br/></p>
<p><a href="https://graph.org/">Test link&lt;/a&gt;</a></p>
<figure>
<img src="/file/6c2ecfdfd6881d37913fa.png"/>
<figcaption></figcaption>
</figure>
""".replace(
    "\n", ""
)

NODES_TEST_LIST = [
    {"tag": "p", "children": ["Hello, world!", {"tag": "br"}]},
    {
        "tag": "p",
        "children": [
            {
                "tag": "a",
                "attrs": {"href": "https://graph.org/"},
                "children": ["Test link</a>"],
            }
        ],
    },
    {
        "tag": "figure",
        "children": [
            {"tag": "img", "attrs": {"src": "/file/6c2ecfdfd6881d37913fa.png"}},
            {"tag": "figcaption"},
        ],
    },
]

HTML_MULTI_LINES = """
<p>
    <b>
        Hello,

    </b>
    world!
</p>
"""

HTML_MULTI_LINES1 = """<p><b>Hello, </b>world! </p>"""

HTML_MULTI_LINES_NODES_LIST = [
    {"tag": "p", "children": [{"tag": "b", "children": ["Hello, "]}, "world! "]},
]

HTML_NO_STARTTAG = "</a><h1></h1>"


class TestHTMLConverter(TestCase):
    def test_html_to_nodes(self):
        self.assertEqual(html_to_nodes(HTML_TEST_STR), NODES_TEST_LIST)

    def test_nodes_to_html(self):
        self.assertEqual(nodes_to_html(NODES_TEST_LIST), HTML_TEST_STR)

    def test_html_to_nodes_multi_line(self):
        self.assertEqual(html_to_nodes(HTML_MULTI_LINES), HTML_MULTI_LINES_NODES_LIST)
        self.assertEqual(html_to_nodes(HTML_MULTI_LINES1), HTML_MULTI_LINES_NODES_LIST)

    def test_uppercase_tags(self):
        self.assertEqual(
            html_to_nodes("<P>Hello</P>"), [{"tag": "p", "children": ["Hello"]}]
        )

    def test_html_to_nodes_invalid_html(self):
        with self.assertRaises(InvalidHTML):
            html_to_nodes("<p><b></p></b>")

    def test_html_to_nodes_not_allowed_tag(self):
        with self.assertRaises(NotAllowedTag):
            html_to_nodes('<script src="localhost"></script>')

    def test_nodes_to_html_nested(self):
        self.assertEqual(
            nodes_to_html(
                [
                    {
                        "tag": "a",
                        "children": [
                            {
                                "tag": "b",
                                "children": [
                                    {
                                        "tag": "c",
                                        "children": [{"tag": "d", "children": []}],
                                    }
                                ],
                            }
                        ],
                    }
                ]
            ),
            "<a><b><c><d></d></c></b></a>",
        )

    def test_nodes_to_html_blank(self):
        self.assertEqual(nodes_to_html([]), "")

    def test_clear_whitespace(self):
        i = (
            "\n<p><i>A</i><b> </b><b>B <i>C</i><i><b></b></i>"
            " D </b> E </p><p> F </p>\n"
        )
        expected = [
            {
                "tag": "p",
                "children": [
                    {"tag": "i", "children": ["A"]},
                    {"tag": "b", "children": [" "]},
                    {
                        "tag": "b",
                        "children": [
                            "B ",
                            {"tag": "i", "children": ["C"]},
                            {"tag": "i", "children": [{"tag": "b"}]},
                            " D ",
                        ],
                    },
                    "E ",
                ],
            },
            {"tag": "p", "children": ["F "]},
        ]

        self.assertEqual(html_to_nodes(i), expected)

    def test_clear_whitespace_1(self):
        x = "\n<p><i>A</i><b> </b><b>B <i>C</i><i><b></b></i> D </b> E </p><p> F </p>\n"
        y = "<p><i>A</i><b> </b><b>B <i>C</i><i><b></b></i> D </b>E </p><p>F </p>"
        self.assertEqual(nodes_to_html(html_to_nodes(x)), y)

    def test_pre_whitespace_preserved(self):
        self.assertEqual(
            html_to_nodes("<pre>\nhello\nworld</pre>"),
            [{"tag": "pre", "children": ["\nhello\nworld"]}],
        )

    def test_no_starttag_node(self):
        with self.assertRaises(InvalidHTML):
            html_to_nodes(HTML_NO_STARTTAG)
