import argparse 

parser = argparse.ArgumentParser(description='Calculate optimal trader strategy')
parser.add_argument('-f', '--file', type=str, help="File with source data")


class TraderException(Exception):
    # Все ошибки логики
    pass

def parse_input_line(line):
    parts = line.split()

    if not parts == 3:
        raise TraderException("Incorrect format '{}'".format(line))

    try:
        data = dict(
            day=int(parts[0]),
            name=parts[1],
            price=float(parts[2]),
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
            days, lot_count, balance = file.readline().split()
            for c in range(0, int(lot_count)):
                line_num += 1
                try:
                    line_parts = file.readline().split()
                    lot_data = dict(
                        day=int(line_parts[0]),
                        name=line_parts[1],
                        price=float(line_parts[2]),
                        quantity=int(line_parts[3]),
                        )
                except TraderException as e:
                    print("Error in input data, line {} ".format(line_data, e.message))

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
    print()

