from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import Name, CallFunc, AssName, Getattr, Tuple, Subscript


class ViewsChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = 'views'
    msgs = {
        'W5501': ('is_authenticated is not called',
                  'is-authenticated-not-called',
                  'Used when is_authenticated method is not called'),
        'W5502': ('objects.get is used without catching DoesNotExist',
                  'objects-get-without-doesnotexist',
                  'Used when Model.objects.get is used without enclosing it '
                  'in try-except block to catch DoesNotExist exception.'),
        'W5503': ('Fetching model objects only for getting len',
                  'fetching-db-objects-len',
                  'Used when there is db query that fetches objects from '
                  'database only to check the number of returned objects.'),
        'W5504': ('Accessing raw GET or POST data, consider using forms',
                  'raw-get-post-access',
                  'Used when request.GET or request.POST dicts is accessed '
                  'directly, it is better to use forms.'),
    }

    _is_view_function = False
    _is_view_class = False
    _is_inside_try_except = False
    _try_except_node = None
    _is_len = True

    @staticmethod
    def _is_does_not_exist(node):
        if (isinstance(node, (Name, Getattr)) and
                'DoesNotExist' in node.as_string()):
            return True
        return False

    @staticmethod
    def _is_getattr_or_name(node, name):
        if ((isinstance(node, Name) and node.name == name) or
                (isinstance(node, Getattr) and node.attrname == name)):
            return True
        return False

    def visit_getattr(self, node):
        parent = node.parent
        expr = node.expr
        if self._is_getattr_or_name(expr, 'user'):
            if (node.attrname == 'is_authenticated' and
                    not isinstance(parent, CallFunc)):
                self.add_message('W5501', node=node)
        elif self._is_getattr_or_name(expr, 'request'):
            if node.attrname in ('GET', 'POST'):
                if (isinstance(parent, Subscript) or
                        isinstance(parent, Getattr) and
                        parent.attrname == 'get'):
                    self.add_message('W5504', node=node)

        elif node.attrname == 'objects':

            # Fixed the parent object didn't has attrname
            if hasattr(parent, 'attrname'):
                return

            if parent.attrname == 'get':
                if self._is_view_function or self._is_view_class:
                    if not self._is_inside_try_except:
                        self.add_message('W5502', node=node)
                    else:
                        for h in self._try_except_node.handlers:
                            if self._is_does_not_exist(h.type):
                                break
                            elif isinstance(h.type, Tuple):
                                _does_not_exist_found = False
                                for exc_cls in h.type.elts:
                                    if self._is_does_not_exist(exc_cls):
                                        _does_not_exist_found = True
                                        break
                                if _does_not_exist_found:
                                    break
                        else:
                            self.add_message('W5502', node=node)
            elif parent.attrname in ('all', 'filter', 'exclude'):
                if self._is_len:
                    self.add_message('W5503', node=node)

    def visit_function(self, node):
        if 'views' in node.root().file:
            args = node.args.args
            if (args and isinstance(args[0], AssName) and
                    args[0].name == 'request'):
                self._is_view_function = True

    def leave_function(self, node):
        self._is_view_function = False

    def visit_tryexcept(self, node):
        self._is_inside_try_except = True
        self._try_except_node = node

    def leave_tryexcept(self, node):
        self._is_inside_try_except = False
        self._try_except_node = None

    def visit_callfunc(self, node):
        if isinstance(node.func, Name) and node.func.name == 'len':
            self._is_len = True

    def leave_callfunc(self, node):
        self._is_len = False

    def visit_class(self, node):
        if node.is_subtype_of('django.views.generic.base.View'):
            self._is_view_class = True

    def leave_class(self, node):
        self._is_view_class = False
