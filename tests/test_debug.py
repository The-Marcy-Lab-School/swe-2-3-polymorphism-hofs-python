from debug import Rental, Screening, Station, Tandem, fleet_total, message_if, restock_message


TEST_SUITE_NAME = "Debug Tests"


import inspect



def test_restock_message_warns_a_low_station():
    """restock_message - it no longer raises, and it warns when bikes are low"""
    assert restock_message(Station("Grand Army", 1)) == "Grand Army: send bikes"


def test_restock_message_says_ok_when_there_are_enough():
    """restock_message - a station with enough bikes needs no warning"""
    assert restock_message(Station("Borough Hall", 9)) == "Borough Hall: ok"


def test_restock_message_passes_the_function_not_its_result():
    """restock_message - is_low is handed over uncalled"""
    source = inspect.getsource(restock_message)

    assert "is_low()" not in source, \
        "Pass station.is_low, with no parentheses. message_if calls it itself."
    assert "is_low" in source, "message_if still needs to be given the check."


def test_message_if_was_left_alone():
    """restock_message - message_if was never the bug"""
    source = inspect.getsource(message_if)

    assert "check()" in source, \
        "message_if calls the function it is given. That part was already right."


import pytest



def test_screening_can_now_be_made():
    """Screening - it implements both abstract methods, so it is no longer abstract"""
    screening = Screening("SC1", 40)

    assert screening.hourly_rate() == 6.00
    assert isinstance(screening, Rental)


def test_screening_keeps_its_own_rule_for_being_rentable():
    """Screening - is_rentable was already correct and still is"""
    assert Screening("SC1", 40).is_rentable() is True
    assert Screening("SC2", 0).is_rentable() is False


def test_the_abstract_base_class_was_not_weakened():
    """Screening - Rental still refuses an incomplete subclass"""
    assert Rental.__abstractmethods__ == {"is_rentable", "hourly_rate"}, \
        "Keep both @abstractmethod decorators on Rental."

    class Trailer(Rental):
        def is_rentable(self):
            return True

    with pytest.raises(TypeError):
        Trailer()


def test_the_mixed_fleet_adds_up():
    """Screening - one loop over both kinds, each answering for itself"""
    assert fleet_total([Tandem("T1", False), Screening("SC1", 40)], 2) == 25.00
