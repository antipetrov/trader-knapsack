from unittest import TestCase
from trader import *

class MainTestCase(TestCase):

    def test_test(self):
        self.assertEqual(True, True)

    def test_data_convert(self):

        input_list = [
            {'raw_line': '1 alfa-05 100.2 2\n', 'day': 2, 'name': 'alfa-05',
             'price_percent': 200.0, 'quantity': 2},
            {'raw_line': '2 alfa-05 101.5 5\n', 'day': 2, 'name': 'alfa-05',
             'price_percent': 100.0, 'quantity': 2},
        ]
        converted = convert_to_lots(input_list)

        self.assertEqual(type(converted), list)
        self.assertEqual(type(converted[0]), Lot)

        # первым в списке должен идти второй лот (idx=1)
        # потому что у него лучше win/price
        self.assertEqual(converted[0].index, 1)

    def test_upperbound(self):
        lots = [
            Lot(0, 'test0', 100, 200),
            Lot(1, 'test1', 150, 200),
        ]

        # с первого лота
        node = Node(lots[0].win, lots[0].price, 0, items=lots)
        bound = node.upperbound(lots, 1000)
        self.assertEqual(bound, 250)

        # со второго лота
        node = Node(
            lots[0].win + lots[1].win,
            lots[0].price + lots[1].price,
            1,
            items=lots)

        bound = node.upperbound(lots, 1000)
        self.assertEqual(bound, 250)

        # со второго лота но упершись в ограничение бюджета
        node = Node(
            lots[0].win + lots[1].win,
            lots[0].price + lots[1].price,
            1,
            items=lots)

        bound = node.upperbound(lots, 300)
        self.assertEqual(bound, 0)

        # когда только часть второго лота влезает в бюджет,
        # оценка должна быть больше выиграша первого лота
        node = Node(lots[0].win, lots[0].price, 0, items=lots)
        bound = node.upperbound(lots, 300)
        self.assertTrue(bound > lots[0].win)
