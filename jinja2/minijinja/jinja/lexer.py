# -*- coding: utf-8 -*-
"""
    jinja.lexer
    ~~~~~~~~~~~

    lexer of jinja html template
"""

token_type = {'data',
              'expression_start', 'expression_end', 'expression',
              'statement_start', 'statement_end', 'statement',
              'comment_start', 'comment_end', 'comment',
              'line_statment_start', 'line_statment_end', 'line_statment'
}

token_type_map = {
    '{{': 'expression_start',
    '}}': 'expression_end',
    '{%': 'statement_start',
    '%}': 'statement_end',
    '{#': 'comment_start',
    '#}': 'comment_end',
    '#': 'line_statement_start',
    '##': 'line_statement_end'
}


state = {'data', 'expression', 'statement', 'comment', 'line_statement', 'bad'}

state_machine = {
    'data': {
        '{{': 'expression',
        '{%': 'statement',
        '{#': 'comment',
        'eof': 'end'
    },

    'expression': {
        '}}': 'data',
        'eof': 'bad'
    },

    'statement': {
        '%}': 'data',
        'eof': 'bad'
    },

    'comment': {
        '#}': 'data',
        'eof': 'bad'
    },

    'bad': {
        'any': 'bad'
    },

    'end': {
        'any': 'bad'
    }
}


def get_tokens(source):
    """
    get tokens from html template

    :param source: source of template
    :return: tokens
    """
    tokens = []
    token = []
    state = 'data'
    while source is not '':
        step = source[:2]

        # get next state according to step
        # default state is state itself
        next_state = state_machine[state].get(step, state)
        if next_state == state:
            token.append(step[0])
            source = source[1:]
        else:
            tokens.append((''.join(token), state))
            tokens.append((step, token_type_map.get(step, '')))
            token = []
            source = source[2:]
            state = next_state
    if token is not []:
        tokens.append((''.join(token), state))
    if state_machine[state].get('eof') is 'bad':
        print('bad template: %s is not match'.format(state))

    return tokens


if __name__ == '__main__':
    tsource = """<html>
    hi {{ user }}
</html>"""
    tokens = get_tokens(tsource)
    print(tokens)