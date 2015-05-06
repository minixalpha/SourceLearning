# -*- coding: utf-8 -*-

from jinja import lexer

def test_get_tokens(source):
    assert lexer.get_tokens(source) == []


if __name__ == '__main__':
    source = """<html>
    Hello {{ user }}
</html>
    """
    test_get_tokens(source)


