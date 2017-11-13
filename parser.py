"""
parser.py
"""

import re

DF = 'df'


class Parser(object):

    def __init__(self, *args):
        self._patterns = []
        for pattern in args:
            self.add_pattern(pattern)

    def add_pattern(self, pattern):
        assert isinstance(pattern, Pattern)
        #self._match_str, parserpatterns.append(pattern)
        self._patterns.append(pattern)

    def add_rule(self, rule):
        assert isinstance(rule, Rule)
        self._stack.append(rule)

    def parse(self, sql_str):
        self._sql_str = sql_str
        self._cursor = 0
        self._stack = [ NextPatternRule(self) ]

        while self._stack:
            print("At position: {}".format(self._cursor))
            print("Stack contents: {}".format(self._stack))
            self._rule = self._stack.pop()
            self._rule()


class Rule(object):

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class NextPatternRule(Rule):

    def __init__(self, parser):
        self._parser = parser

    def _get_next_pattern(self):

        # Evaluate all patterns.
        next_pattern = None
        next_str = ""
        next_pattern_span = (1000, 1000)  # OBVIOUSLY FIX THIS!

        for pattern in self._parser._patterns:
            match = pattern.search(self._parser)
            if match is not None:
                if match.span()[0] < next_pattern_span[0]:
                    next_pattern = pattern
                    next_pattern_span = match.span()
                    next_str = match.group() 
                    continue
                elif match.span()[0] == next_pattern_span[0]:
                    next_pattern = pattern
                    next_pattern_span = match.span()
                    next_str = match.group() 
                    continue

        return next_pattern, next_str

    def __call__(self):

        next_pattern, match_str = self._get_next_pattern()
        if next_pattern is not None:
            next_pattern.rules_to_stack(match_str, self._parser)


class AdvanceCursorRule(Rule):

    def __init__(self, advance, parser):
        self._advance = advance
        self._parser = parser

    def __call__(self):
        self._parser._cursor += self._advance


class PrintTableColumnRule(Rule):

    def __init__(self, table_column):
        self._table_column = table_column

    def __call__(self, table_column):
        print( "".join(( DF, "['", self._table_column, "']")))


class PrintLiteralRule(Rule):

    def __init__(self, literal):
        self._literal = literal

    def __call__(self):
        print(self._literal)


class PrintDecimalRule(Rule):

    def __init__(self, decimal):
        self._decimal = decimal

    def __call__(self):
        print(self._decimal)


class Pattern(object):

    regex = None

    def __call__(self):
        raise NotImplementedError

    def search(self, parser):
        print("Pattern {} is searching in {} (cursor {})".format(self, parser._sql_str[parser._cursor:], parser._cursor))
        return self.regex.search(parser._sql_str[parser._cursor:])

    def rules_to_stack(self, match_str, parser):
        rules = self(match_str, parser)
        for rule in rules[::-1]:
            parser.add_rule(rule)


class LiteralPattern(Pattern):

    regex = re.compile("\d+")

    def __call__(self, match_str, parser):

        rules = [PrintLiteralRule(literal=match_str),
                 AdvanceCursorRule(advance=len(match_str), parser=parser),
                 NextPatternRule(parser)]

        return rules


class DecimalPattern(Pattern):

    regex = re.compile("\d+\.\d+")

    def __call__(self, match_str, parser):

        rules = [ PrintDecimalRule(decimal=match_str),
                  AdvanceCursorRule(advance=len(match_str), parser=parser),
                  NextPatternRule(parser) ]

        return rules


class TableColumnPattern(Pattern):

    regex = re.compile("\$[^ ]*")

    def __call__(self, match_str, parser):
        rules = [ PrintTableColumnRule(table_column=match_str),
                  AdvanceCursorRule(advance=len(match_str), parser=parser),
                  NextPAtternRule(parser) ]

