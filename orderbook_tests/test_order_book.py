from order_book import Order
import pytest


asks = [
    {'price': 2.9895869718570243, 'quantity': 2, 'id': 19295},
    {'price': 4.731063050251845, 'quantity': 8, 'id': 17634},
    {'price': 3.1369574384273693, 'quantity': 2, 'id': 19831}
]

bids = [
    {'price': 8.142864134725002, 'quantity': 8, 'id': 18367},
    {'price': 4.649052595182558, 'quantity': 5, 'id': 16772},
    {'price': 3.966239602633006, 'quantity': 10, 'id': 20185}
]


@pytest.fixture(scope="module")
def test_order():
    return Order(asks, bids)


def test_values(test_order):
    assert test_order.value["asks"]
    assert test_order.value["bids"]

def test_len_values(test_order):
    assert len(test_order.value["asks"]) == 3
    assert len(test_order.value["bids"]) == 3


def test_keys_asks(test_order):
    assert test_order.value["asks"][0]["id"]
    assert test_order.value["asks"][0]["price"]
    assert test_order.value["asks"][0]["quantity"]


def test_keys_bids(test_order):
    assert test_order.value["bids"][0]["id"]
    assert test_order.value["bids"][0]["price"]
    assert test_order.value["bids"][0]["quantity"]


def test_sort_asks(test_order):
    data_now = test_order.value["asks"][0]
    test_order.sort()
    data_after_sort = test_order.value["asks"][0]
    assert data_now != data_after_sort


def test_sort_bids(test_order):
    data_now = test_order.value["bids"][0]
    test_order.sort()
    data_after_sort = test_order.value["bids"][0]
    assert data_now != data_after_sort


def test_add_asks(test_order):
    data = {"id": 231223, "price": "2.1213122", "quantity": "3"}
    test_order.add_ask(data)
    assert len(Order.value["asks"]) == 4


def test_add_bids(test_order):
    data = {"id": 23123, "price": "2.123312", "quantity": "2"}
    test_order.add_bids(data)
    assert len(Order.value["bids"]) == 4


def test_delete_asks(test_order):
    count_asks = len(test_order.value["asks"])
    data = 19295
    test_order.delete(data)
    count_asks_after_delete = len(test_order.value["asks"])
    assert count_asks != count_asks_after_delete


def test_delete_bids(test_order):
    count_asks = len(test_order.value["bids"])
    data = 20185
    test_order.delete(data)
    count_asks_after_delete = len(test_order.value["bids"])
    assert count_asks != count_asks_after_delete
