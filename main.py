from __future__ import print_function

import click

from ExpenseService import ExpenseService

expense_instance = None


def get_instance():
    global expense_instance
    if expense_instance:
        return expense_instance
    else:
        expense_instance = ExpenseService()
        return expense_instance


@click.group()
def main():
    pass


@main.command()
def set_tags():
    get_instance().set_tags()


@main.command()
def set_school_expense():
    get_instance().school_service.compute_all()


if __name__ == '__main__':
    main()