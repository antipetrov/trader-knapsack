import argparse
import sys
from collections import deque


PAPER_NOMINAL = 1000 # номинал каждой облигации
LOT_DAYS = 30 # дней до погашения
LOT_COUPON_DAYLY = 1 # купонный доход в день


class TraderException(Exception):
    # Все ошибки логики
    pass


def parse_input_line(line):
    """
    Разбирает строку входных данных и считает выигрыш
    :param line:
    :return:
    """

    parts = line.split()

    if not len(parts) == 4:
        raise TraderException("Incorrect format '{}'".format(line))

    try:
        data = dict(
            raw_line=line.strip(),
            day=int(parts[0]),
            name=parts[1],
            price_percent=float(parts[2]),
            quantity=int(parts[3]),
        )
    except ValueError as e:
        raise TraderException("Unable to parse '{}'".format(line))


    return data


def get_data_from_file(filename):

    lots = list()
    try:
        with open(filename, 'r') as file:
            line_num = 0
            header_parts = file.readline().split()

            try:
                days = int(header_parts[0])
                lot_count = int(header_parts[1])
                balance = float(header_parts[2])
            except ValueError as e:
                sys.stderr.write("Error in first line: {}\n".format(e))

            for line in file:
                line_num += 1
                try:
                    lot_data = parse_input_line(line)
                except TraderException as e:
                    sys.stdout.write("Error in input data, line {}: {}\n".format(line_num, e))
                lots.append(lot_data)

    except Exception as e:
        raise e

    return days, lots, balance


def get_data_from_input():
    return None,None,None


class Node(object):
    """
    'Узел' дерева рещений задачи (0-1 Рюкзак)
    Каждый узел содержит
    - суммарный доход (win)
    - стоимость (price)
    - список купленных лотов (items)

    Проходя по списку лотов будем создавать по два узла на каждый лот:
    - для варианта когда лот куплен
    - для варианта когда лот не куплен

    Для каждого узла, вычислим
    """

    count = 0

    def __init__(self, win, price, level, items=[]):
        self.win = win
        self.price = price
        self.level = level
        self.items = items

        self.count = Node.count
        Node.count += 1

    def upperbound(self, lots_all, balance):
        """
        Проверяем, какой максимальный выигрыш мы можем получить,
        если начиная с текущего узла будем покупать все оставшиеся лоты,
        пока деньги не кончатся

        :param lots_all: список всех лотов
        :param balance: общий баланс
        :return:
        """

        if self.price > balance:
            return 0

        sum_value = self.win
        sum_price = self.price

        l = self.level+1
        max_level = len(lots_all)

        while l < max_level and sum_price + lots_all[l].price <= balance:

            sum_value += lots_all[l].win
            sum_price += lots_all[l].price
            l += 1

        # Делаем вид что последний лот можно поделить (branch and bound)
        # чтобы получить верхнюю оценку
        if l < max_level:
            sum_value += int((balance - sum_price) * \
                         lots_all[l].win / lots_all[l].price)

        return sum_value

    def __repr__(self):
        return "<Node{} level{} items:[{}]>".format(self.count, self.level, ",".join([str(i) for i in self.items]))


class Lot(object):

    count = 0

    def __init__(self, index, name, win, price):
        self.index = index
        self.name = name
        self.win = win
        self.price = price

        self.count = self.__class__.count
        self.__class__.count += 1

    def __repr__(self):
        return "<Lot {} win:{} price:{}>".format(self.count, self.win, self.price)


def convert_to_lots(lot_list):
    """
    Преобразуем исходные данные в список объектов типа Lot
    Список сразу сортируем по убыванию win/price (доход на стоимость)
    win и price хранятся в int - то есть
    номинируются в копейках (умножаются на 100)
    Это нужно чтобы не возиться с округлением по ходу вычислений

    :param lot_list: список dict-ов
    :return:
    """

    items = list()
    for idx, data in enumerate(lot_list):

        # стоимость всего лота в деньгах (="вес" в задаче о рюкзаке)
        lot_price = int(100 * PAPER_NOMINAL * data['price_percent']/100 * data['quantity'])

        # выигрыш лота (в деньгах) = купонный доход + сумма погашения
        # (="ценность\цена" в задаче о рюкзаке)
        lot_win = int(100 * (PAPER_NOMINAL + LOT_DAYS * LOT_COUPON_DAYLY) * \
                  data['quantity'])

        items.append(Lot(idx, data['name'], lot_win, lot_price))

    items.sort(key=lambda x: x.win/x.price, reverse=True)

    return items


def calculate_optimal_lots(lot_list, days, balance, is_debug=False):

    lots = convert_to_lots(lot_list)
    nodes = deque()
    balance100 = balance*100

    # создаем фиктивный узел дерева чтобы с него начать
    root_node = Node(0, 0, -1, [])
    nodes.append(root_node)
    max_win_node = root_node

    while len(nodes) > 0:

        current_node = nodes.popleft()
        level = current_node.level + 1

        if is_debug:
            sys.stdout.write('current node: {}\n'.format(current_node))

        if level + 1 > len(lots):
            continue

        # вариант 1: что если купить следующий лот по списку
        new_left = Node(current_node.win + lots[level].win,
                        current_node.price + lots[level].price,
                        level,
                        current_node.items + [lots[level]])

        if is_debug:
            sys.stdout.write('\tleft node: {}'.format(new_left))

        if new_left.price <= balance100:

            if max_win_node.win < new_left.win:
                max_win_node = new_left
                if is_debug:
                    sys.stdout.write(' [set new max: {}]'.
                                     format(max_win_node.win))

            bound = new_left.upperbound(lots, balance100)
            if bound > max_win_node.win:
                nodes.append(new_left)

            if is_debug:
                sys.stdout.write(' upperbound: {}\n'.format(bound))

        # вариант 2: а что если не покупать следующий лот по списку
        new_right = Node(current_node.win,
                         current_node.price,
                         level,
                         current_node.items)

        if is_debug:
            sys.stdout.write('\tright node: {}'.format(new_right))

        bound = new_right.upperbound(lots, balance100)
        if bound > max_win_node.win:
            nodes.append(new_right)

        if is_debug:
            sys.stdout.write(' upperbound: {}\n'.format(bound))


    return max_win_node.win/100, (lot.index for lot in max_win_node.items)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculate optimal trader strategy (0-1 knapsack)')
    parser.add_argument('-f', '--file', type=str, help="Data-file")
    parser.add_argument('--verbose', action='store_true', default=False, help="Verbose output")
    args = parser.parse_args()

    filename = args.file
    is_debug = args.verbose

    try:
        days, lots, balance = get_data_from_file(filename)
    except Exception as e:
        sys.stderr.write("Input error: {}\n".format(e))
        exit()

    try:
        total_win, lot_indexes = calculate_optimal_lots(lots, days, balance, is_debug)
    except Exception as e:
        sys.stderr.write("Unknown error: {}\n".format(e))
        exit()


    sys.stdout.write(str(total_win))
    sys.stdout.write("\n")
    for idx in lot_indexes:
        sys.stdout.write(lots[idx]['raw_line'])
        sys.stdout.write("\n")