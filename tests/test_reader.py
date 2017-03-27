from unittest import TestCase

from obo import Ontology, Definition
from obo.reader import OBOReader
from obo.stanzas import Relationship


class OBOReaderTestCase(TestCase):
    pass


class GeneOntologyTestCase(TestCase):

    def test_read_gene_ontology(self):
        reader = OBOReader()
        with open('files/go.obo', 'r') as fp:
            ontology = reader.read(fp)

        self.assertIsInstance(ontology, Ontology)
        self.assertEqual(len(ontology.terms), 44492)


class SequenceOntologyTestCase(TestCase):

    def test_read_sequence_ontology(self):

        reader = OBOReader()
        with open('files/so-xp.obo', 'r') as fp:
            ontology = reader.read(fp)

        self.assertIsInstance(ontology, Ontology)
        self.assertEqual(len(ontology.subsetdefs), 3)
        self.assertEqual(len(ontology.synonymtypedefs), 9)
        self.assertEqual(len(ontology.terms), 2311)
        self.assertEqual(len(ontology.typedefs), 50 + 6)
        self.assertEqual(len(ontology.instances), 0)
        self.assertEqual(len(ontology.unrecognized_stanzas), 0)

        for term in ontology.terms:
            if term.definition:
                self.assertIsInstance(term.definition, Definition)

            if term.relationships:
                for relationship in term.relationships:
                    self.assertIsInstance(relationship, Relationship)

    def test_read_sequence_ontology_shortcut(self):
        with open('files/so-xp.obo', 'r') as fp:
            ontology = Ontology.read(fp)

        self.assertIsInstance(ontology, Ontology)