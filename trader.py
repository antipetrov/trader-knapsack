import argparse 

LOT_NOMINAL = 1000 # номинал каждой облигации
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
            day=int(parts[0]),
            name=parts[1],
            price_percent=float(parts[2]),
            quantity=int(parts[3]),
        )
    except ValueError as e:
        raise TraderException("Unable to parse '{}'".format(line))

    # стоимость всего лота в деньгах
    data['lot_price'] = LOT_NOMINAL * \
                        data['price_percent']/100 * \
                        data['quantity']

    # выигрышь лота (в дегьшах) = купонный доход + сумма погашения
    data['lot_win'] = (LOT_NOMINAL +
                       LOT_DAYS*LOT_COUPON_DAYLY) * \
                      data['quantity']

    return data


def get_data_from_file(filename):

    lots = list()
    try:
        with open(filename, 'r') as file:
            line_num = 0
            days, lot_count, balance = file.readline().split()

            for c in range(0, int(lot_count)):
                line_num += 1
                try:
                    lot_data = parse_input_line(file.readline())
                except TraderException as e:
                    print("Error in input data, line {}: {}".format(line_num, e))

                lots.append(lot_data)
    except Exception as e:
        raise e

    return days, lots, balance

def get_data_from_input():
    return None,None,None


def calculate_optimal_lots(days, lots, balance):
    total_win = 0
    lot_purchased = []
    return total_win, lot_purchased


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculate optimal trader strategy')
    parser.add_argument('-f', '--file', type=str, help="File with source data")

    args = parser.parse_args()
    
    filename = args.file


    try:
        if filename:
            days, lots, balance = get_data_from_file(filename)
        else:
            days, lots, balance = get_data_from_input()
    except Exception as e:
        exit("Input error: {}".format(e))

    print(lots, days, balance)


    total_win, lot_purchased = calculate_optimal_lots(days, lots, balance)
    # /print()

