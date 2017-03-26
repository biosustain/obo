from collections import defaultdict


class TagValueSetProperty(object):
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __get__(self, stanza, owner):
        return stanza._tags[self.name]

    def __set__(self, stanza, value):
        if isinstance(value, set):
            stanza._tags[self.name] = value
        else:
            stanza._tags[self.name] = set(value)


class TagValueProperty(object):
    __slots__ = ('name', 'default')

    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def __get__(self, stanza, owner):
        try:
            return stanza._tags[self.name][0]
        except (KeyError, IndexError):
            return self.default

    def __set__(self, stanza, value):
        stanza._tags[self.name] = [value]


class ForbiddenTagProperty(object):
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def _raise_attribute_error(self, stanza):
        raise AttributeError("'{}' is a forbidden attribute in {}".format(self.name,
                                                                          stanza._stanza_name or stanza.__class__.__name__))

    def __get__(self, stanza, owner):
        self._raise_attribute_error(stanza)

    def __set__(self, stanza, value):
        self._raise_attribute_error(stanza)


class Object(object):
    __slots__ = ('_tags',)
    _tag_order = ()

    def __init__(self, **kwargs):
        self._tags = tags = defaultdict(list)
        for name, value in kwargs.items():
            if isinstance(value, (list, tuple, set)):
                tags[name] = value
            else:
                tags[name].append(value)

    def add_tag(self, name, value):
        if isinstance(self._tags[name], set):
            self._tags[name].add(value)
        else:
            self._tags[name].append(value)

    @staticmethod
    def _format_tag_group(name, values):
        s = ''
        for item in values:
            s += '{}: {}\n'.format(name, str(item))
        return s

    def __str__(self):
        known_tags = ''
        unknown_tags = ''
        for name in self._tag_order:
            if name in self._tags:
                known_tags += self._format_tag_group(name, self._tags[name])
            else:
                unknown_tags += self._format_tag_group(name, self._tags[name])
        return known_tags + unknown_tags


class Stanza(Object):
    __slots__ = ('_stanza_name',)

    id = TagValueProperty('id')
    name = TagValueProperty('name')

    is_anonymous = TagValueProperty('is_anonymous')
    alt_ids = TagValueSetProperty('alt_id')
    definition = TagValueProperty('def')  # 'def' is a reserved keyword in Python
    comment = TagValueProperty('comment')
    subset = TagValueProperty('subset')
    synonyms = TagValueSetProperty('synonym')
    xrefs = TagValueSetProperty('xref')
    is_a = TagValueSetProperty('is_a')
    intersection_of = TagValueSetProperty('intersection_of')
    union_of = TagValueSetProperty('union_of')
    disjoint_from = TagValueSetProperty('disjoint_from')
    relationship = TagValueSetProperty('relationship')
    is_obsolete = TagValueProperty('is_obsolete', default=False)
    replaced_by = TagValueProperty('replaced_by')
    consider = TagValueProperty('consider')
    created_by = TagValueProperty('created_by')
    creation_date = TagValueProperty('creation_date')

    def __init__(self, stanza_name, id=None, **kwargs):
        super(Stanza, self).__init__(id=id, **kwargs)
        self._stanza_name = stanza_name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.id == other.id

    def __str__(self):
        if self._stanza_name is None:
            s = ''
        else:
            s = '[{}]\n'.format(self._stanza_name)
        s += Object.__str__(self)
        return s


class Term(Stanza):
    _tag_order = (
        'id',
        'is_anonymous',
        'name',
        'namespace',
        'alt_id',
        'def',
        'comment',
        'subset',
        'synonym',
        'xref',
        'is_a',
        'intersection_of',
        'union_of',
        'disjoint_from',
        'relationship',
        'is_obsolete',
        'replaced_by',
        'consider',
        'created_by',
        'creation_date',
    )

    def __init__(self, id=None, **kwargs):
        super(Term, self).__init__('Term', id, **kwargs)


class Typedef(Stanza):
    _tag_order = (
        'id',
        'is_anonymous',
        'name',
        'namespace',
        'alt_id',
        'def',
        'comment',
        'subset',
        'synonym',
        'xref',
        'domain',
        'range',
        'is_anti_symmetric',
        'is_cyclic',
        'is_reflexive',
        'is_symmetric',
        'is_transitive',
        'is_a',
        'inverse_of',
        'transitive_over',
        'relationship',
        'is_obsolete',
        'replaced_by',
        'consider',
    )

    union_of = ForbiddenTagProperty('union_of')
    intersection_of = ForbiddenTagProperty('intersection_of')
    disjoint_from = ForbiddenTagProperty('disjoint_from')

    domain = TagValueProperty('domain')
    range = TagValueProperty('range')

    inverse_of = TagValueProperty('inverse_of')
    transitive_over = TagValueSetProperty('transitive_over')

    is_cyclic = TagValueProperty('is_cyclic', default=False)
    is_reflexive = TagValueProperty('is_reflexive', default=False)
    is_symmetric = TagValueProperty('is_symmetric', default=False)
    is_anti_symmetric = TagValueProperty('is_anti_symmetric', default=False)
    is_transitive = TagValueProperty('is_transitive', default=False)

    is_metadata_tag = TagValueSetProperty('is_metadata_tag')

    def __init__(self, id=None, **kwargs):
        super(Typedef, self).__init__('Typedef', id, **kwargs)


class PropertyValue(object):
    def __init__(self, name, value, datatype=None):
        self.name = name
        self.value = value
        self.datatype = datatype


class Instance(Stanza):
    _tag_order = (
        'id',
        'is_anonymous',
        'name',
        'namespace',
        'alt_id',
        'comment',
        'synonym',
        'xref',
        'instance_of',
        'property_value',
        'is_obsolete',
        'replaced_by',
        'consider',
    )

    property_values = TagValueSetProperty('property_value')

    def __init__(self, id=None, **kwargs):
        super(Instance, self).__init__('Instance', id, **kwargs)


