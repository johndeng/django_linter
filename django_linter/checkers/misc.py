from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import Name


class MiscChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'misc'
    msgs = {
        'W5201': ('Print is used (consider using logger instead)',
                  'print-used',
                  'Used when there is print statement or function'),
    }

    def visit_callfunc(self, node):
        if isinstance(node.func, Name) and node.func.name == 'print':
            self.add_message('W5201', node=node)

    def visit_print(self, node):
        self.add_message('W5201', node=node)
