# coding=utf-8
import os
from glob import iglob


class File(object):
    def __init__(self, _file):
        self.__file = _file
        self.__mode = 'r'
        self.__buffering = -1
        self.__opened = None

    def __enter__(self):
        if self.__opened is None:
            self.__opened = open(self.__file, self.__mode, self.__buffering)

        return self.__opened

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__opened.close()
        self.__opened = None

    def buffering(self, buffering=-1):
        self.__buffering = buffering

    def mode(self, mode='r'):
        self.__mode = mode

        return self


class Path(object):
    def __init__(self, path=None):
        self.__drive = u''
        self.__file = None
        self.__path = []

        self.set(path)

    def __add__(self, other):
        if type(other) is Path:
            if (unicode(other).startswith('/') or
                    unicode(other).startswith('\\')):
                other = os.path.join(*other[1:])
            obj = Path(os.path.join(unicode(self), unicode(other)))
        else:
            obj = unicode(self) + other

        return obj

    def __call__(self, *args, **kwargs):
        return unicode(self)

    def __contains__(self, item):
        try:
            iglob(os.path.join(str(self), item)).next()
        except StopIteration:
            return False

        return True

    def __div__(self, other):
        path = self.__add_path(other)

        return Path(self.__build_path(path))

    def __eq__(self, other):
        return self.__get_path == unicode(other)

    def __getitem__(self, item):
        return self.__path_parts[item]

    def __iter__(self):
        return iter(Walker(self))

    def __len__(self):
        return len(unicode(self))

    def __mul__(self, other):
        if self.__file is None:
            raise AttributeError('No file associated with path.')

        if other[0] != '.':
            other = '.' + other

        return Path('{}{}'.format(
                os.path.splitext(unicode(self))[0], other))

    def __repr__(self):
        return repr(self.__get_path)

    def __unicode__(self):
        return unicode(self.__get_path)

    @staticmethod
    def __build_path(path):
        return os.path.normpath(os.path.join(*path))

    def __add_path(self, directory):
        path = self.__path[:]

        path.append(directory)
        return path

    def __set_path(self, path):
        head, tail = os.path.split(path)

        if tail:
            self.__path.insert(0, tail)
        elif head == os.sep:
            self.__path.insert(0, head)

        if head and tail:
            self.__set_path(head)

    def depth(self, depth=None):
        return Walker(self).depth(depth)

    def follow_links(self, follow=False):
        return Walker(self).follow_links(follow)

    def on_error(self, on_error=None):
        return Walker(self).on_error(on_error)

    def set(self, path, file_name=None):
        if isinstance(path, Path):
            path = unicode(path)

        if isinstance(path, (str, unicode)):
            path = os.path.expanduser(os.path.expandvars(path))
            path = os.path.normpath(path)

            if os.path.isfile(path):
                path, self.__file = os.path.split(path)

            self.__drive, path = os.path.splitdrive(path)
            self.__path = []
            self.__set_path(path)

        if file_name is not None:
            self.file = file_name

        return self

    def top_down(self, top_down=True):
        return Walker(self).top_down(top_down)

    def up(self, count=1):
        path = self.__path[:]

        while count:
            if len(path) > 1:
                path.pop()

            count -= 1

        drive = self.__drive if self.__drive else ''
        path = os.path.join(drive, *path)

        return Path(path)

    def files(self, file_filter='*'):
        for f in iglob(os.path.join(unicode(self), file_filter)):
            if os.path.isfile(f):
                yield Path(f)

    def dirs(self, dir_filter='*'):
        for d in iglob(os.path.join(unicode(self), dir_filter)):
            if os.path.isdir(d):
                yield Path(d)

    def existing_path(self):
        path = Path(unicode(self))

        while not path.exists() and unicode(path):
            path = path.up()

        if not unicode(path):
            raise IOError('Invalid path, no valid parent directories.')

        return path

    @property
    def __get_path(self):
        path = ''

        if len(self.__path):
            path = self.__build_path(self.__path)

        if self.__file is not None:
            path = os.path.join(path, self.__file)

        return unicode(self.__drive + path)

    @property
    def __path_parts(self):
        path_parts = []

        path_parts += self.__path[:]

        if self.__drive and path_parts[0] == os.sep:
            path_parts[0] = self.__drive + path_parts[0]

        if self.__file is not None:
            path_parts.append(self.__file)

        return path_parts

    @property
    def exists(self):
        return os.path.exists(unicode(self))

    @property
    def file(self):
        return self.__file

    @file.setter
    def file(self, file_name):
        if isinstance(file_name, (str, unicode)):
            self.__file = file_name

    @property
    def file_extension(self):
        return self.file_split[1]

    @property
    def file_split(self):
        return os.path.splitext(self.file)

    @property
    def full_path(self):
        return unicode(self)

    @property
    def is_dir(self):
        return os.path.isdir(unicode(self))

    @property
    def is_file(self):
        return os.path.isfile(unicode(self))

    @property
    def open(self):
        if self.file is None:
            raise IOError('The file property is not set.')

        return File(self.full_path)


class Walker(object):
    def __init__(self, path=None):
        self.__depth = None
        self.__follow_links = False
        self.__on_error = None
        self.__top_down = True

        self.__path = Path(path)

    def __iter__(self):
        return self.__walk()

    @staticmethod
    def __dir_path(dirs):
        for d in dirs:
            yield Path(d)

    @staticmethod
    def __file_path(files):
        for f in files:
            path = Path()
            path.file = f
            yield path

    def __walk(self):
        if not self.__path.exists:
            raise StopIteration

        walker = os.walk(unicode(self.__path),
                         self.__top_down,
                         self.__on_error,
                         self.__follow_links)

        for path, dirs, files in walker:
            children = path.replace(unicode(self.__path), '').split(os.sep)

            if self.__depth is not None and len(children) > self.__depth:
                del dirs[:]

            yield Path(path), self.__dir_path(dirs), self.__file_path(files)

    def depth(self, depth=None):
        if not isinstance(depth, int):
            depth = None

        self.__depth = depth

        return self

    def follow_links(self, follow=False):
        self.__follow_links = follow and True

        return self

    def on_error(self, on_error=None):
        self.__on_error = on_error

        return self

    def top_down(self, top_down=True):
        self.__top_down = top_down and True

        return self

