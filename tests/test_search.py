from unittest import TestCase

from obo import Ontology, Term


class SearchTestCase(TestCase):

    def test_is_a_search(self):
        vehicle = Term('T:001', 'vehicle')
        car = Term('T:002', 'car', is_a=[vehicle])
        four_wheeled_vehicle = Term('T:003', 'four_wheeled_vehicle', is_a=[vehicle])
        car.is_a.add(four_wheeled_vehicle)

        ontology = Ontology()
        ontology.terms.update({vehicle, car, four_wheeled_vehicle})

        #vehicle.search_incoming('is_a')
        #car.search_outgoing('is_a')

        car.is_a.remove(vehicle)

        # search again.