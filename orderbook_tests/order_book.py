

class Order():
    """Exchange glass

    Returns:
        class
    """

    value = {
        "asks": None,
        "bids": None
        }
    def __init__(self, asks, bids):
        self.value["asks"] = asks
        self.value["bids"] = bids


    def sort(self, *args):
        """Sort method 
        if none arguments sort self values
        if have arguments sort arguments

        Returns:
            obj.values = {"asks": ["price": value, "id": value, "quantity": value, ....],
                   "bids": ["price": value, "id": value, "quantity": value, ....]}
        """
        shema = {
                "asks": None,
                "bids": None
            }
        if args:
            print(args[0])
            print(args[1])
            asks = self.sort_asks(args[0])
            bids = self.sort_bids(args[1])
            shema["asks"], shema["bids"] = asks, bids
            return self.value
        else:
            if "asks" and "bids" in self.value:
                asks = self.sort_asks(self.value["asks"])
                bids = self.sort_bids(self.value["bids"])
                shema["asks"], shema["bids"] = asks, bids


    def add_bids(self, add_bids):
        """Add bids to values 

        Args:
            add_bids (dict): "{'id'}: value, {'price'}: value, {'quantity'}: value"
        """

        if "id" and "price" and "quantity" in add_bids:
            self.value["bids"].append(add_bids)
        else:
            print("Wrong data...", "{'id'}: value, {'price'}: value, {'quantity'}: value")


    def add_ask(self, add_asks):
        """add asks to values

        Args:
            add_asks (dict): "{'id'}: value, {'price'}: value, {'quantity'}: value"
        """

        if "id" and "price" and "quantity" in add_asks:
            self.value["asks"].append(add_asks)
        else:
            print("Wrong data...", "{'id'}: value, {'price'}: value, {'quantity'}: value")


    def delete(self, data_id):
        """delete one values by "id"

        Args:
            data_id (int): *****
        """

        if "asks" in self.value:
            count = 0
            for item  in self.value["asks"]:
                if item["id"] == data_id:
                    del self.value["asks"][count]
                count += 1
        if "bids" in self.value:
            count = 0
            for item  in self.value["bids"]:
                if item["id"] == data_id:
                    del self.value["bids"][count]
                count += 1
                

    @staticmethod
    def sort_asks(asks):
        size = lambda asks: asks["price"]
        asks.sort(key=size, reverse=True)
        return asks

    @staticmethod
    def sort_bids(bids):
        prise = lambda bids: bids["price"]
        bids.sort(key=prise, reverse=False)
        return bids


if __name__ == "__main__":
        """ Тест класса без использования pytest
        """
    import random
    import uuid


    def get_data():
        """Generate datasets
        Returns:
            list: [{"price":"int", "quantity":"int"},{"",""}.....]
        """
        result = []
        shema = {
            "price": None,
            "quantity": None,
            "id" : None
        }
        for i in range(10):
            shema["price"] = random.triangular(1, 10)
            shema["quantity"] = random.randint(1, 10)
            shema["id"] = uuid.uuid4().fields[2]
            result.append(shema)
            shema = {
            "price": None,
            "quantity": None
            }
            
        return result

    
    asks = get_data() # дата сет запросов
    bids = get_data() # дата сет ставок

    order = Order(asks, bids) #Создаем экземпляр класса и инициализируем данные
    print("Исходные данные: ")
    if "asks" in order.value:
        for i in order.value["asks"]:
            print(i)

    print(50*"=")
    if "bids" in order.value:
        for i in order.value["bids"]:
            print(i)

    print("Сортированные данные:")
    order.sort() # Сортируем данные как в биржевом стакане
    if "asks" in order.value:
        for i in order.value["asks"]:
            print(i)

    print(50*"=")
    if "bids" in order.value:
        for i in order.value["bids"]:
            print(i)

