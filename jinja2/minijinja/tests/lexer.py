# -*- coding: utf-8 -*-

from jinja import lexer


def test_get_tokens():
    tsource = """<html>
    hi {{ user }}
</html>"""
    expected_tokens = [
        ('<html>\n    hi ', 'data'),
        ('{{', 'expression_start'),
        (' user ', 'expression'),
        ('}}', 'expression_end'),
        ('\n</html>', 'data')
    ]
    assert lexer.get_tokens(tsource) == expected_tokens

