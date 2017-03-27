import pprint
import re
from collections import defaultdict

from obo import Ontology, TermSubset, SynonymType, SynonymScope, Definition, XRef
from obo.stanzas import Term, Instance, Stanza, Typedef, Relationship


class ParseException(Exception):
    def __init__(self, message, value=None):
        super().__init__(': '.join([message, value]) if value else message)


RE_STANZA = re.compile(r'^\[(?P<stanza>.+)\]$')
RE_NAME_DESCRIPTION = re.compile(r'^(?P<name>.+) "(?P<description>(?:[^"\\]|\\.)*)"$')
RE_XREF_DEFINITION = re.compile(r'^(?P<name>.+)( "(?P<description>(?:[^"\\]|\\.)*)")?$')
RE_NAME_DESCRIPTION_MORE = re.compile(r'^(.+) "((?:[^"\\]|\\.)*)" (.+)"$')
RE_NAME_DESCRIPTION_XREFS = re.compile(r'^(.+) "((?:[^"\\]|\\.)*)" \[(.+)\]"$')
RE_DESCRIPTION_XREFS = re.compile(r'^"(?P<description>(?:[^"\\]|\\.)*)" \[(?P<xrefs>.+)\]$')
RE_XREF_DEFINITION_ITEM = re.compile(r'^(?P<name>.+)( "(?P<description>(?:[^"\\]|\\.)*)")?')
RE_XREF_DEFINITION_DIVIDER = re.compile(r'^,\s+')
RE_RELATIONSHIP = re.compile('^(?P<type>.+) (?P<target_term>.+)$')

RE_SYNONYM_TYPEDEF = re.compile(r'^(?P<name>.+) '
                                r'"(?P<description>(?:[^"\\]|\\.)*)"'
                                r'( (?P<scope>(EXACT|BROAD|NARROW|RELATED)))?$')

BOOLEAN_TAG_NAMES = (
    'is_anonymous',
    'is_obsolete',
    # TODO more tag names
)


class OBOReader(object):
    def _unescape(self, s):
        out, escape = '', False
        for char in s:
            if escape:
                if char in 'ntW':
                    out += {
                        'n': '\n',
                        't': '\t',
                        'W': ' '
                    }[char]
                else:
                    out += char
                escape = False
            elif char == '\\':
                escape = True
            else:
                out += char
        return out

    def read(self, fp):
        stanza = None
        header = None
        stanzas = []
        tag_value_pairs = []

        lines = iter(fp)

        while True:
            try:
                line = next(lines).strip()
            except StopIteration:
                break

            if line.startswith('['):
                # stanza
                match = RE_STANZA.match(line)
                if not match:
                    raise ValueError("Bad stanza tag format")

                if stanza is not None:
                    stanzas.append((stanza, tag_value_pairs))
                else:
                    header = tag_value_pairs

                stanza = match.group('stanza')
                tag_value_pairs = []
            elif line.startswith('!'):
                # skip comments
                pass
            elif not line:
                # empty line. ignore
                pass
            else:
                # tag-value pair

                # 1. strip unescaped '!'s.
                # 2. if line ends with '\', read next line, then continue with #1
                # 3. split at first unescaped ':' and ignore everything from first unescaped '{' or '!'

                tag, value = None, None
                part = ''
                escape, quote = False, False

                while True:
                    for char in line:
                        if escape:
                            # if char in 'ntW':
                            #     part += {
                            #         'n': '\n',
                            #         't': '\t',
                            #         'W': ' '
                            #     }[char]
                            # else:
                            #     part += char
                            escape = False
                        elif char == '\\':
                            escape = True
                        elif not tag and char == ':':
                            tag = part
                            part = ''
                        elif char == '!':  # and not quote? OBO Spec is not very specific on all of this.
                            break  # comment
                        elif char == '{' and not quote:
                            break  # trailing modifier
                        else:
                            if char == '"':
                                quote = not quote
                            part += char
                    if escape:
                        try:
                            line = next(lines).strip()
                        except StopIteration:
                            raise ParseException("Unterminated tag-value pair at end of file.", line)
                    else:
                        break

                #if quote:
                #    raise ParseException("Unterminated quote in tag-value pair", line, tag, value)

                if tag is not None:
                    value = part.strip()
                else:
                    raise ParseException('Tag without value', line)

                if tag in BOOLEAN_TAG_NAMES:
                    if value not in ('true', 'false'):
                        raise ParseException('Tag must be one of "true", "false"', line)
                    value = value == 'true'
                elif tag == 'relationship':
                    match = RE_RELATIONSHIP.match(value)

                    if match:
                        value = Relationship(self._unescape(match.group('type')),
                                             self._unescape(match.group('target_term')))
                    else:
                        raise ParseException("Malformatted 'relationship'", value)
                elif tag == 'xref':
                    match = RE_XREF_DEFINITION.match(value)

                    if match:
                        value = XRef(self._unescape(match.group('name')),
                                     self._unescape(match.group('description') or '') or None)
                    else:
                        raise ParseException("Malformatted 'xref'", value)
                elif tag == 'def':
                    match = RE_DESCRIPTION_XREFS.match(value)

                    if match:
                        description = match.group('description')
                        xrefs_value = match.group('xrefs')
                        xrefs = []

                        xref_match = RE_XREF_DEFINITION_ITEM.match(xrefs_value)
                        while xref_match:
                            pos = xref_match.endpos
                            xrefs.append(XRef(self._unescape(xref_match.group('name')),
                                              self._unescape(xref_match.group('description') or '') or None))

                            if pos == len(xrefs_value):
                                break

                            comma_match = RE_XREF_DEFINITION_DIVIDER.match(xrefs_value, pos)
                            if not comma_match:
                                raise ParseException("Malformatted 'def'", value)

                            pos = comma_match.endpos
                            xref_match = RE_XREF_DEFINITION_ITEM.match(xrefs_value, pos)

                        value = Definition(description, *xrefs)

                    else:
                        raise ParseException("Malformatted 'def'", value)

                tag_value_pairs.append((tag, value))

        if stanza is not None:
            stanzas.append((stanza, tag_value_pairs))
        else:
            header = tag_value_pairs

        ontology = Ontology()

        for name, value in header:
            if name == 'subsetdef':
                match = RE_NAME_DESCRIPTION.match(value)

                if match:
                    value = TermSubset(self._unescape(match.group('name')), self._unescape(match.group('description')))
                else:
                    raise ParseException("Malformatted 'subsetdef'", value)
            elif name == 'synonymtypedef':

                match = RE_SYNONYM_TYPEDEF.match(value)

                if match:
                    scope = match.group('scope')
                    value = SynonymType(self._unescape(match.group('name')),
                                        self._unescape(match.group('description')),
                                        scope=SynonymScope[scope] if scope else None)
                else:
                    raise ParseException("Malformatted 'synonymtypedef'", value)

            ontology.add_tag(name, value)

        for stanza, tags in stanzas:
            tags_dict = defaultdict(list)
            for name, value in tags:
                tags_dict[name].append(value)

            if stanza == 'Term':
                ontology.terms.add(Term(**tags_dict))

                # TODO attach subset.
            elif stanza == 'Typedef':
                ontology.typedefs.add(Typedef(**tags_dict))
            elif stanza == 'Instance':
                ontology.instances.add(Instance(**tags_dict))
            else:
                # Parsers/serializers round-trip (successfully load and save) unrecognized stanzas.
                self.unrecognized_stanzas.append(Stanza(stanza, **tags_dict))

        return ontology
