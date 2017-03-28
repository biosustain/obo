from unittest import SkipTest
from unittest import TestCase

import io

from obo import Ontology
from obo.writer import OBOWriter


class WriterTestCase(TestCase):
    def test_read_write_sequence_ontology(self):
        obo_file_path = 'files/so-xp.obo'
        with open(obo_file_path, 'r') as fp:
            ontology = Ontology.read(fp)

        with open(obo_file_path, 'r') as fp:
            file = fp.read()

        output = io.StringIO()

        writer = OBOWriter()
        writer.write(ontology, output)

        self.maxDiff = 2000
        self.assertEqual(file, output.getvalue())

    @SkipTest
    def test_read_write_genome_ontology(self):
        obo_file_path = 'files/go.obo'
        with open(obo_file_path, 'r') as fp:
            ontology = Ontology.read(fp)

        with open(obo_file_path, 'r') as fp:
            file = fp.read()

        output = io.StringIO()

        writer = OBOWriter()
        writer.write(ontology, output)

        self.maxDiff = 2000
        self.assertEqual(file, output.getvalue())

    def test_read_write_taxrank_ontology(self):
        obo_file_path = 'files/taxrank.obo'
        with open(obo_file_path, 'r') as fp:
            ontology = Ontology.read(fp)

        with open(obo_file_path, 'r') as fp:
            file = fp.read()

        output = io.StringIO()

        writer = OBOWriter()
        writer.write(ontology, output)

        self.maxDiff = 2000
        self.assertEqual(file, output.getvalue())
