from modify import Bike, CargoBike, ClassicBike, Dock, ElectricBike, Station, busiest_first, late_fee


TEST_SUITE_NAME = "Modify Tests"


import inspect



def test_the_fees_did_not_move():
    """late_fee - a refactor, so every answer is what it was before"""
    assert late_fee(ClassicBike("A1", "Grand Army", False), 2) == 3.00
    assert late_fee(ElectricBike("E9", "Borough Hall", False, 24), 2) == 9.00
    assert late_fee(CargoBike("C3", "Grand Army", False, 90), 2) == 5.00


def test_late_fee_no_longer_asks_what_kind_of_bike():
    """late_fee - no isinstance and no type left in the function"""
    source = inspect.getsource(late_fee)

    assert "isinstance" not in source, "Ask the bike for its fee instead."
    assert "type(" not in source, "Ask the bike for its fee instead."


def test_each_class_reports_its_own_fee():
    """late_fee - the fee is now a fact about each kind of bike"""
    assert ClassicBike("A1", "Grand Army", False).late_fee_per_hour() == 1.50
    assert ElectricBike("E9", "Borough Hall", False, 24).late_fee_per_hour() == 4.50
    assert CargoBike("C3", "Grand Army", False, 90).late_fee_per_hour() == 2.50


def test_a_plain_bike_still_answers():
    """late_fee - the superclass keeps the fallback the else branch had"""
    assert Bike("B0", "Grand Army", False).late_fee_per_hour() == 0.00
    assert late_fee(Bike("B0", "Grand Army", False), 5) == 0.00


def test_a_new_kind_of_bike_needs_no_change_to_late_fee():
    """late_fee - this is what the refactor bought"""
    class FoldingBike(Bike):
        def late_fee_per_hour(self):
            return 2.00

    assert late_fee(FoldingBike("F1", "Grand Army", False), 3) == 6.00, \
        "late_fee should work for a kind of bike it was never told about."


import modify



def station():
    stop = Station("Grand Army")
    stop.dock(Bike("A1", "Grand Army", False))
    stop.dock(Bike("A2", "Grand Army", True))
    stop.dock(Bike("B7", "Borough Hall", False))
    return stop


def test_bikes_where_takes_a_lambda():
    """Station.bikes_where - the condition arrives as an argument"""
    found = station().bikes_where(lambda bike: bike.is_rentable())

    assert [bike.serial for bike in found] == ["A1", "B7"]


def test_bikes_where_takes_a_named_function():
    """Station.bikes_where - any function of one bike works"""
    def needs_work(bike):
        return bike.needs_repair

    assert [bike.serial for bike in station().bikes_where(needs_work)] == ["A2"]


def test_bikes_where_answers_a_condition_it_was_never_written_for():
    """Station.bikes_where - this is what taking a function bought"""
    found = station().bikes_where(lambda bike: bike.station == "Borough Hall")

    assert [bike.serial for bike in found] == ["B7"]


def test_bikes_where_can_match_nothing():
    """Station.bikes_where - an empty result is a new empty list"""
    stop = station()

    assert stop.bikes_where(lambda bike: False) == []
    assert len(stop.bikes) == 3, "Filtering must not empty the station."


def test_the_three_old_methods_are_gone():
    """Station.bikes_where - rentable, repair_list and at_station were deleted"""
    for name in ("rentable", "repair_list", "at_station"):
        assert not hasattr(modify.Station, name), \
            f"Delete {name}. bikes_where replaces it."


import inspect



def test_busiest_first_orders_by_rides_started():
    """busiest_first - most rides first"""
    docks = [Dock("Grand Army", 14), Dock("Borough Hall", 31), Dock("Prospect", 22)]

    assert [dock.name for dock in busiest_first(docks)] == \
        ["Borough Hall", "Prospect", "Grand Army"]


def test_busiest_first_leaves_the_original_alone():
    """busiest_first - sorted returns a new list"""
    docks = [Dock("Grand Army", 14), Dock("Borough Hall", 31)]
    busiest_first(docks)

    assert docks[0].name == "Grand Army"


def test_busiest_first_handles_a_tie():
    """busiest_first - two docks with the same count must not be compared to each other"""
    docks = [Dock("Grand Army", 20), Dock("Borough Hall", 20), Dock("Prospect", 5)]

    names = [dock.name for dock in busiest_first(docks)]

    assert names[2] == "Prospect"
    assert set(names[:2]) == {"Grand Army", "Borough Hall"}


def test_busiest_first_uses_sorted_with_a_key():
    """busiest_first - the hand-rolled version is gone"""
    source = inspect.getsource(busiest_first)

    assert "sorted(" in source, "Use sorted() with a key."
    assert "key=" in source, "Tell sorted what to sort by with key=."
    assert ".reverse()" not in source, "sorted takes reverse=True."
    assert "append" not in source, "sorted returns the list, so nothing needs appending."
