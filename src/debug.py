from abc import ABC, abstractmethod


class Station:
    def __init__(self, name, bikes_available):
        self.name = name
        self.bikes_available = bikes_available

    def is_low(self):
        return self.bikes_available < 3


def message_if(station, check, message):
    """Already correct. Do not change it."""
    if check():
        return f"{station.name}: {message}"
    return f"{station.name}: ok"


def restock_message(station):
    return message_if(station, station.is_low(), "send bikes")


class Rental(ABC):
    @abstractmethod
    def is_rentable(self):
        pass

    @abstractmethod
    def hourly_rate(self):
        pass


class Tandem(Rental):
    def __init__(self, serial, needs_repair):
        self.serial = serial
        self.needs_repair = needs_repair

    def is_rentable(self):
        return not self.needs_repair

    def hourly_rate(self):
        return 6.50


class Screening(Rental):
    def __init__(self, serial, seats_left):
        self.serial = serial
        self.seats_left = seats_left

    def is_rentable(self):
        return self.seats_left > 0


def fleet_total(rentals, hours):
    return sum(rental.hourly_rate() * hours for rental in rentals)
