class Bike:
    def __init__(self, serial, station, needs_repair):
        self.serial = serial
        self.station = station
        self.needs_repair = needs_repair

    def is_rentable(self):
        return not self.needs_repair


class ClassicBike(Bike):
    pass


class ElectricBike(Bike):
    def __init__(self, serial, station, needs_repair, battery_range):
        super().__init__(serial, station, needs_repair)
        self.battery_range = battery_range


class CargoBike(Bike):
    def __init__(self, serial, station, needs_repair, crate_litres):
        super().__init__(serial, station, needs_repair)
        self.crate_litres = crate_litres


def late_fee(bike, hours):
    if isinstance(bike, ElectricBike):
        per_hour = 4.50
    elif isinstance(bike, CargoBike):
        per_hour = 2.50
    elif isinstance(bike, ClassicBike):
        per_hour = 1.50
    else:
        per_hour = 0.00
    return per_hour * hours


class Station:
    def __init__(self, name):
        self.name = name
        self.bikes = []

    def dock(self, bike):
        self.bikes.append(bike)

    def rentable(self):
        found = []
        for bike in self.bikes:
            if bike.is_rentable():
                found.append(bike)
        return found

    def repair_list(self):
        found = []
        for bike in self.bikes:
            if bike.needs_repair:
                found.append(bike)
        return found

    def at_station(self, name):
        found = []
        for bike in self.bikes:
            if bike.station == name:
                found.append(bike)
        return found

    def bikes_where(self, test):
        """Replace the three methods above with this one."""
        pass


def discounted_price(price, discount):
    return round(price * (1 - discount), 2)


def make_discounter(discount):
    """Replace discounted_price with this."""
    pass


# Build these two from make_discounter once it works.
member_price = None
staff_price = None
