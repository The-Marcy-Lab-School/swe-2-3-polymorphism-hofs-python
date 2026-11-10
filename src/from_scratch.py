from abc import ABC, abstractmethod


class Bike:
    """Already written for you. Do not change it."""

    def __init__(self, serial, station, needs_repair):
        self.serial = serial
        self.station = station
        self.needs_repair = needs_repair

    def is_rentable(self):
        return not self.needs_repair

    def hourly_rate(self):
        """The base rate, in dollars, that every kind of bike starts from."""
        return 3.00

    def __repr__(self):
        return f"{type(self).__name__}({self.serial!r})"


class ClassicBike(Bike):
    """Already written for you. Do not change it."""

    def hourly_rate(self):
        return super().hourly_rate() + 1.00


class ElectricBike(Bike):
    """Already written for you. Do not change it."""

    def __init__(self, serial, station, needs_repair, battery_range):
        super().__init__(serial, station, needs_repair)
        self.battery_range = battery_range

    def hourly_rate(self):
        return super().hourly_rate() + 4.50


class CargoBike(Bike):
    """Already written for you. Do not change it."""

    def __init__(self, serial, station, needs_repair, crate_litres):
        super().__init__(serial, station, needs_repair)
        self.crate_litres = crate_litres

    def hourly_rate(self):
        return super().hourly_rate() + 2.50


def fleet_revenue(bikes, hours):
    pass


class Scooter:
    pass


class Rentable:
    pass


class Helmet:
    pass


def rate_of(bike):
    pass


def cheapest_first(bikes):
    pass


def cheapest_first_lambda(bikes):
    pass
