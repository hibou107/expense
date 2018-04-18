
import math


def revenu(net_imposable, part):
    by_part = net_imposable / part
    tranches = [(0, 9807, 0), (9807, 27086, 0.14), (17806, 72617, 0.3),
                (72617, 158783, 0.41), (153783, 100000000, 0.45)]
    result = 0.0
    for (min, max, taux) in tranches:
        if min < by_part < max:
            result = result + (by_part - min) * taux
            return math.floor(result * part)
        else:
            result = result + (max - min) * taux
    return math.floor(result * part)


def mensualite(K, t, y):
    temp1 = K * t / 12
    temp2 = math.pow(1 + t / 12, -(12 * y))
    return temp1 / (1 - temp2)


if __name__ == "__main__":

    print(revenu(45640.0, 2.5))
    print(mensualite(100000, 0.04, 20))
