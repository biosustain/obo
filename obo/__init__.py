from collections import defaultdict
from enum import Enum

from obo.stanzas import Term, Typedef, Object, TagValueProperty, TagValueSetProperty
from obo.util import StanzaSet

__version__ = (1, 0, 0)

TYPE = 'OBO:TYPE'
TERM_OR_TYPE = 'OBO:TERM_OR_TYPE'
TERM = 'OBO:TERM'
INSTANCE = 'OBO:INSTANCE'


class XRef(object):
    """

    This class makes no assumptions about the format of `name`. This is because not all ontologies use the common
    "name:value" format for DB-xrefs, but may use URLs or other names instead.

    """
    __slots__ = ('name', 'description')

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        # NOTE trailing modifiers are ignored by this implementation.
        # https://oboformat.googlecode.com/svn/trunk/doc/GO.format.obo-1_2.html#S.1.4
        # Parser implementations may choose to decode and/or round-trip these trailing modifiers.
        # However, this is not required. A parser may choose to ignore or strip away trailing modifiers.

    @property
    def database(self):
        return self.name.split(':', 1)[0]

    @property
    def identifier(self):
        if ':' not in self.name:
            return None
        return self.name.split(':', 1)[1]

    def __repr__(self):
        return '{}({}, description={})'.format(self.__class__.__name__, repr(self.name), repr(self.description))

    def __str__(self):
        if self.description:
            return '{} "{}"'.format(self.name, self.description)
        return self.name


class Definition(object):
    __slots__ = ('description', 'xrefs')

    def __init__(self, description, *xrefs):
        self.description = description
        self.xrefs = xrefs

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, repr(self.description), repr(self.xrefs))

    def __str__(self):
        return '"{}" [{}]'.format(self.description, ', '.join(str(xref) for xref in self.xrefs))


BUILT_IN_TYPEDEFS = (
    Typedef('ia_a',
            name='is_a',
            range=TERM_OR_TYPE,
            domain=TERM_OR_TYPE,
            definition=Definition("The basic subclassing relationship", XRef('OBO:defs'))),
    Typedef('disjoint_from',
            name='disjoint_from',
            range=TERM,
            domain=TERM,
            definition=Definition("Indicates that two classes are disjoint", XRef('OBO:defs'))),
    Typedef('instance_of',
            name='instance_of',
            range=TERM,
            domain=INSTANCE,
            definition=Definition("Indicates the type of an instance", XRef('OBO:defs'))),
    Typedef('inverse_of',
            name='inverse_of',
            range=TYPE,
            domain=TYPE,
            definition=Definition("Indicates that one relationship type is the inverse of another", XRef('OBO:defs'))),
    Typedef('union_of',
            name='union_of',
            range=TERM,
            domain=TERM,
            definition=Definition("Indicates that a term is the union of several others", XRef('OBO:defs'))),
    Typedef('intersection_of',
            name='intersection_of',
            range=TERM,
            domain=TERM,
            definition=Definition("Indicates that a term is the intersection of several others [OBO:defs]",
                                  XRef('OBO:defs'))),
)


class TermSubset(object):
    __slots__ = ('name', 'description')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, repr(self.name), repr(self.description))

    def __str__(self):
        return '{} "{}"'.format(self.name, self.description)


class SynonymScope(Enum):
    EXACT = 'EXACT'
    BROAD = 'BROAD'
    NARROW = 'NARROW'
    RELATED = 'RELATED'


class SynonymType(object):
    __slots__ = ('name', 'description', 'scope')

    def __init__(self, name, description, scope=None):
        self.name = name
        self.description = description
        self.scope = scope

    def __repr__(self):
        return '{}({}, {}, scope={})'.format(self.__class__.__name__,
                                             repr(self.name),
                                             repr(self.description),
                                             repr(self.scope))

    def __str__(self):
        if self.scope:
            return '{} "{}" {}'.format(self.name, self.description, self.scope.name)
        return '{} "{}"'.format(self.name, self.description)


class Ontology(Object):
    _tag_order = (
        'format-version',
        'data-version',
        'date',
        'saved-by',
        'auto-generated-by',
        'import',
        'subsetdef',
        'synonymtypedef',
        'default-namespace',
        'remark',
    )

    format_version = TagValueProperty('format_version')

    data_version = TagValueProperty('data_version')
    ontology = TagValueProperty('ontology')
    date = TagValueProperty('date')
    saved_by = TagValueProperty('saved-by')
    auto_generated_by = TagValueProperty('auto-generated-by')

    id_spaces = TagValueSetProperty('idspace')
    default_relationship_id_prefix = TagValueProperty('default-relationship-id-prefix')
    id_mappings = TagValueSetProperty('id-mapping')

    remark = TagValueProperty('remark')

    # TODO OBO 1.4 tags

    subsetdefs = TagValueSetProperty('subsetdef')
    synonymtypedefs = TagValueSetProperty('synonymtypedef')

    def __init__(self, **kwargs):
        super(Ontology, self).__init__(**kwargs)
        self.typedefs = StanzaSet(BUILT_IN_TYPEDEFS)
        self.terms = StanzaSet()
        self.instances = StanzaSet()
        self.unrecognized_stanzas = []

    @classmethod
    def read(cls, fp, format='obo'):
        if format == 'obo':
            from obo.reader import OBOReader
            return OBOReader().read(fp)
        else:
            raise NotImplementedError('Only the "obo" format is supported.')

    # TODO replace terms with a better data structure for O(1) lookup
    # deprecated
    def term_by_id(self, id_):
        return self.terms[id_]

    # TODO replace terms with a better data structure for O(1) lookup
    def term_by_name(self, name):
        try:
            return next(term for term in self.terms if term.name == name)
        except StopIteration:
            raise KeyError('No term with name: {}'.format(name))
