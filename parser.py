import sys
from typing import List
from enum import Enum


class State(Enum):
    """Enumerates the possible states the Parser can be in"""
    INITIAL = 0
    DEFAULT = 1
    HEADING = 2
    PARAGRAPH = 3
    UNORDERED_LIST = 4
    ORDERED_LIST = 5


class Transition(Enum):
    """Enumerates the possible transitions that can occur"""
    POUND_SIGN = 1
    ASTERISK = 2
    OTHER_CHARACTER = 3
    LIST_NUMBER = 4
    EMPTY_LINE = 5
    NONE = 6


class Parser:
    def __init__(self):
        self.is_previous_line_newline = False
        self.is_paragraph = False
        self.is_unordered_list = False
        self.state = State.INITIAL
        self.output = ""
        self.tokens = []

    def transition(self):
        """Execute the transition based on the current state and perform the associated actions, if any"""
        if len(self.tokens) == 0:
            transition = Transition.EMPTY_LINE
        elif self.tokens[0][0] == "#":
            transition = Transition.POUND_SIGN
        elif self.tokens[0][0] == "*":
            transition = Transition.ASTERISK
        elif self.tokens[0][0].isdigit() and len(self.tokens) > 1 and self.tokens[0][1] == ".":
            transition = Transition.LIST_NUMBER
        else:
            transition = Transition.OTHER_CHARACTER

        transitions = {
            (State.INITIAL, Transition.POUND_SIGN): (State.DEFAULT, [self.create_heading]),
            (State.INITIAL, Transition.ASTERISK): (State.UNORDERED_LIST, None),
            (State.INITIAL, Transition.OTHER_CHARACTER): (State.PARAGRAPH, None),
            (State.INITIAL, Transition.LIST_NUMBER):
                (State.ORDERED_LIST, [self.create_ordered_list_start, self.create_list_item_start]),

            (State.DEFAULT, Transition.POUND_SIGN): (State.DEFAULT, [self.create_heading]),
            (State.DEFAULT, Transition.ASTERISK): (
                State.UNORDERED_LIST, [self.create_unordered_list_start]),
            (State.DEFAULT, Transition.OTHER_CHARACTER): (State.PARAGRAPH, [self.create_paragraph_start]),
            (State.DEFAULT, Transition.LIST_NUMBER):
                (State.ORDERED_LIST, [self.create_ordered_list_start, self.create_list_item_start]),

            (State.PARAGRAPH, Transition.EMPTY_LINE): (State.DEFAULT, [self.create_paragraph_end]),
            (State.PARAGRAPH, Transition.ASTERISK):
                (State.UNORDERED_LIST,
                 [self.create_paragraph_end, self.create_unordered_list_start,
                  self.create_list_item_start]),
            (State.PARAGRAPH, Transition.LIST_NUMBER):
                (State.ORDERED_LIST,
                 [self.create_paragraph_end, self.create_ordered_list_start,
                  self.create_list_item_start]),
            (State.PARAGRAPH, Transition.POUND_SIGN): (State.DEFAULT, [self.create_paragraph_end, self.create_heading]),

            (State.UNORDERED_LIST, Transition.EMPTY_LINE): (
                State.DEFAULT, [self.create_list_item_end, self.create_unordered_list_end]),
            (State.UNORDERED_LIST, Transition.ASTERISK): (
                State.UNORDERED_LIST, [self.create_list_item_end, self.create_list_item_start]),
            (State.UNORDERED_LIST, Transition.LIST_NUMBER): (State.ORDERED_LIST,
                                                             [self.create_list_item_end,
                                                              self.create_unordered_list_end,
                                                              self.create_ordered_list_start,
                                                              self.create_list_item_start]),

            (State.ORDERED_LIST, Transition.LIST_NUMBER): (
                State.ORDERED_LIST, [self.create_list_item_end, self.create_list_item_start]),
            (State.ORDERED_LIST, Transition.EMPTY_LINE): (
                State.DEFAULT, [self.create_list_item_end, self.create_ordered_list_end]),
            (State.ORDERED_LIST, Transition.ASTERISK): (State.UNORDERED_LIST, [self.create_list_item_end,
                                                                               self.create_ordered_list_end,
                                                                               self.create_unordered_list_start,
                                                                               self.create_list_item_start]),
        }

        try:
            (self.state, transition_actions) = transitions[(self.state, transition)]
        except KeyError:
            self.output = " ".join(self.tokens)
            self.output += "\n"
            return

        if transition_actions:
            for action in transition_actions:
                action()
                self.output += "\n"
        else:
            self.output = " ".join(self.tokens)
            self.output += "\n"

    def create_heading(self):
        """Append the heading start tag, the heading content, and the heading end tag to the output"""
        pound_sign_count = 0
        for character in self.tokens[0]:
            if character == "#" and pound_sign_count < 6:
                pound_sign_count += 1
            else:
                break

        self.output += "<h{}>\n".format(pound_sign_count)
        self.output += " ".join([self.tokens[0][pound_sign_count:]] + self.tokens[1:])
        self.output += "\n"
        self.output += "</h{}>".format(pound_sign_count)

    def create_paragraph_start(self):
        """Append the paragraph start tag and first line of paragraph content to the output"""
        self.output += "<p>\n"
        self.output += " ".join(self.tokens)

    def create_paragraph_end(self):
        """Append the paragraph end tag to the output"""
        self.output += "</p>"

    def create_unordered_list_start(self):
        """Append the unordered list start tag to the output"""
        self.output += "<ul>"

    def create_unordered_list_end(self):
        """Append the unordered list end tag to the output"""
        self.output += "</ul>"

    def create_list_item_start(self):
        """Append the list item start tag to the output"""
        self.output += "<li>\n"
        self.output += " ".join(self.tokens[1:])

    def create_list_item_end(self):
        """Append the list item end tag to the output"""
        self.output += "</li>"

    def create_ordered_list_start(self):
        """Append the ordered list start tag to the output"""
        self.output += "<ol>"

    def create_ordered_list_end(self):
        """Append the ordered list end tag to the output"""
        self.output += "</ol>"

    def parse_line(self, line: str):
        self.output = ""
        self.tokens = line.split()
        self.transition()

        return self.output


def parse_to_html(path_to_file: str):
    with open(path_to_file, "r") as markdown_file:
        parser = Parser()
        for line in markdown_file:
            print(parser.parse_line(line), end="")


parse_to_html(sys.argv[1])
