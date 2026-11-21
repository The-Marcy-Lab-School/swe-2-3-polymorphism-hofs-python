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
