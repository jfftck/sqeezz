# coding=utf-8


class StringConcat(object):
    def __init__(self, value=None):
        self.__buffer = []

        if value is not None and isinstance(value, basestring):
            self.__buffer.append(value)

    def __add__(self, other):
        if not isinstance(other, basestring):
            other = unicode(other)

        self.__buffer.extend(other)

        return self

    def __repr__(self):
        return repr(''.join(self.__buffer))

    def __sub__(self, other):
        try:
            self.__buffer.remove(other)
        except ValueError as e:
            if e.message != 'list.remove(x): x not in list':
                raise

        return self

    def __unicode__(self):
        return unicode(''.join(self.__buffer))

    def clear(self):
        self.__buffer = []

        return self
