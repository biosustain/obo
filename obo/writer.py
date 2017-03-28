
from operator import attrgetter

from obo import BUILT_IN_TYPEDEFS, Definition, XRef
from obo.stanzas import Relationship

ESCAPE_TRANSLATION_TABLE = str.maketrans({
    '\\': r'\\\\',
    '\n': '\\n',
    '\t': '\\t',
    ' ': '\\W',
    '"': '\\"',
    '(': '\\(',
    ')': '\\)',
    '[': '\\[',
    ']': '\\]',
    '{': '\\{',
    '}': '\\}'
})

ESCAPE_XREF_TRANSLATION_TABLE = str.maketrans({
    '\\': r'\\\\',
    '\n': '\\n',
    '\t': '\\t',
    ':': '\\:',
    ' ': '\\W',
    '"': '\\"',
    # '[': '\\[',
    ']': '\\]',
})

class OBOWriter(object):

    def _escape(self, s):
        return s.translate(ESCAPE_TRANSLATION_TABLE)

    def _escape_xref(self, s):
        return s.translate(ESCAPE_XREF_TRANSLATION_TABLE)

    def _format_tag_value(self, ontology, name, value):
        if isinstance(value, Relationship):
            try:
                target_term = ontology.terms[value.target_term]
                return '{} {} ! {}'.format(self._escape(value.type),
                                           self._escape(value.target_term),
                                           self._escape(target_term.name))
            except KeyError:
                return '{} {} ! {}'.format(self._escape(value.type),
                                           self._escape(value.target_term),
                                           self._escape(value.target_term))
        elif name in ('is_a', 'intersection_of', 'union_of', 'disjoint_from'):
            try:
                target_term = ontology.terms[value]
                return '{} ! {}'.format(self._escape(target_term.id), self._escape(target_term.name))
            except KeyError:
                return '{} ! {}'.format(self._escape(value), self._escape(value))
        elif value is True:
            return 'true'
        elif value is False:
            return 'false'
        elif isinstance(value, Definition):
            return '"{}" [{}]'.format(value.description, ', '.join(
                '{}:{}'.format(self._escape_xref(xref.database), self._escape_xref(str(xref.identifier)))
                for xref in value.xrefs))
        elif isinstance(value, XRef):
            if value.description:
                return '{}:{} "{}"'.format(self._escape_xref(value.database),
                                           self._escape_xref(str(value.identifier)),
                                           value.description)
            else:
                return '{}:{}'.format(self._escape_xref(value.database), self._escape_xref(str(value.identifier)))
        return str(value)

    def _write_tag_group(self, ontology, fp, name, values):
        """
        Formats tag name and values and writes them to fp.

        If the same tag appears multiple times in a stanza, the tags should be ordered alphabetically on the tag value.
        """
        # formatted_values = sorted(self._format_tag_value(ontology, name, value) for value in values)
        # for formatted_value in formatted_values:
        #     fp.write('{}: {}\n'.format(name, formatted_value))
        for value in values:
            fp.write('{}: {}\n'.format(name, self._format_tag_value(ontology, name, value)))

    def _write_object(self, ontology, fp, obj):
        for name in obj._tag_order:
            if name in obj.tags:
                self._write_tag_group(ontology, fp, name, obj.tags[name])
        for name in sorted(obj.tags):
            if name not in obj._tag_order:
                self._write_tag_group(ontology, fp, name, obj.tags[name])
        fp.write('\n')

    def _write_stanza(self, ontology, fp, stanza):
        fp.write('[{}]\n'.format(stanza._stanza_name))
        self._write_object(ontology, fp, stanza)

    def write(self, ontology, fp, saved_by=None):
        # auto-generated-by: Python-OBO 0.0.0

        self._write_object(ontology, fp, ontology)

        stanzas = (ontology.typedefs - set(BUILT_IN_TYPEDEFS)) | ontology.terms | ontology.instances

        for stanza in sorted(stanzas, key=attrgetter('id')):
            self._write_stanza(ontology, fp, stanza)