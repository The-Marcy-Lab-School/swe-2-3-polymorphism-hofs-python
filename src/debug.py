class Scooter:
    def __init__(self, serial, charge, needs_repair):
        self.serial = serial
        self.charge = charge
        self.needs_repair = needs_repair


def needs_charging(scooter):
    return scooter.charge < 20


def scooters_where(scooters, matches):
    """Already correct. Do not change it."""
    return [scooter for scooter in scooters if matches(scooter)]


def charging_list(scooters):
    return scooters_where(scooters, needs_charging())
