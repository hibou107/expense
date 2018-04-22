
import math


def revenu(net_imposable, part):
    by_part = net_imposable / part
    tranches = [(0, 9807, 0),
                (9807, 27086, 0.14),
                (27086, 72617, 0.3),
                (72617, 158783, 0.41),
                (153783, 100000000, 0.45)]
    result = 0.0
    for (min, max, taux) in tranches:
        if min <= by_part <= max:
            result = result + (by_part - min) * taux
            return math.floor(result * part)
        elif by_part > max:
            result = result + (max - min) * taux
    return math.floor(result * part)


def plot():
    import matplotlib.pyplot as plt
    net_imposables = range(10000, 100000, 100)
    impots = [revenu(x, 2.5) for x in net_imposables]
    plt.plot(net_imposables, impots)
    plt.ylabel('some numbers')
    plt.show()


def compute_mensualite(total, taux, months):
    temp1 = total * taux / 12
    temp2 = math.pow(1 + taux / 12, - months)
    return temp1 / (1 - temp2)


def compute_monthly_rate(year_rate):
    return math.pow(1 + year_rate, 1 / 12) - 1


def compute_monthly_investment(monthly_saving, monthly_rate, nb_months, tax_monthly):
    result = 0.0
    for i in range(nb_months):
        result = result * (1 + monthly_rate) + monthly_saving - tax_monthly
    return result


def simulate_buy():
    monthly_saving = 3000
    total_saving = 80000
    apport = 30000
    current_saving = total_saving - apport
    apartment_price = 270000
    notaire_fee = apartment_price * 0.08
    nb_months = 12 * 15
    nb_year = nb_months / 12
    market_yield = 0.05
    taux_teg = 0.02
    inflation = 0.01
    taxe_fonciere = 3000
    taxe_fonciere_monthly = taxe_fonciere / 12
    charge_coproprietaire = 4000
    charge_coproprietaire_monthly = charge_coproprietaire / 12
    frais_agence = 0.05

    mensualite = compute_mensualite(apartment_price + notaire_fee - apport, taux_teg, nb_months)

    investir_par_mois = monthly_saving - mensualite
    monthly_market_yield = compute_monthly_rate(market_yield)
    all_monthly_investment = compute_monthly_investment(investir_par_mois, monthly_market_yield, nb_months,
                                                        taxe_fonciere_monthly + charge_coproprietaire_monthly)

    from_original_investment = current_saving * math.pow(1 + market_yield, nb_year)
    all_investment = all_monthly_investment + from_original_investment
    assets = apartment_price * math.pow(1 + inflation, nb_year) * (1 - frais_agence)
    return assets + all_investment


def simulate_rent():
    monthly_saving = 3000
    rent = 1200
    total_saving = 80000
    nb_months = 12 * 15
    nb_year = nb_months / 12
    market_yield = 0.05
    monthly_market_yield = compute_monthly_rate(market_yield)
    all_monthly_investment = compute_monthly_investment(monthly_saving - rent, monthly_market_yield, nb_months, 0.0)
    from_original_investment = total_saving * math.pow(1 + market_yield, nb_year)
    return all_monthly_investment + from_original_investment


def simulate_scpi():
    monthly_saving = 3000
    rent = 1150
    total_saving = 80000
    scpi_total = 100000
    apport = 10000
    nb_months = 12 * 15
    nb_year = nb_months / 12
    taux_teg = 0.028
    mensualite = compute_mensualite(scpi_total - apport, taux_teg, nb_months)
    market_yield = 0.05
    frais_revente = 0.12
    scpi_yield_annual = 0.06
    rent_monthly = scpi_total * scpi_yield_annual / 12
    monthly_market_yield = compute_monthly_rate(market_yield)
    all_monthly_investment = compute_monthly_investment(monthly_saving - rent - mensualite + rent_monthly,
                                                        monthly_market_yield, nb_months, 0.0)
    inflation = 0.01
    asset = scpi_total * math.pow(1 + inflation, nb_year) * (1 - frais_revente)

    from_original_investment = (total_saving - apport) * math.pow(1 + market_yield, nb_year)

    return all_monthly_investment + asset + from_original_investment


if __name__ == "__main__":
    print(compute_mensualite(100000, 0.028, 15*12))
    print(simulate_buy())
    print(simulate_rent())
    print(simulate_scpi())
    # print(revenu(45609, 2.5))
    # plot()

