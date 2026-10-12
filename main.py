from model import FinanceiroModel
from presenter import FinanceiroPresenter
from view import FinanceiroView


def main():
    model = FinanceiroModel()
    presenter = FinanceiroPresenter(model)
    FinanceiroView(presenter)


if __name__ == '__main__':
    main()
