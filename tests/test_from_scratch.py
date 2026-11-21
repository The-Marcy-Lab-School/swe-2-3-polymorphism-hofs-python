import ast
import inspect
import textwrap


def attributes_set_on(instance):
    """The attribute names stored on this instance rather than on its class.

    An attribute written in the class body is shared by every instance, so it
    does not appear here. One assigned to self in __init__ does.
    """
    return set(vars(instance))


def assigns_in_class_body(cls):
    """The names assigned directly in a class body, read with the ast module.

    The source is parsed rather than searched as text, so a name mentioned in a
    comment or a docstring never counts.
    """
    source = textwrap.dedent(inspect.getsource(cls))
    body = ast.parse(source).body[0].body
    names = set()
    for node in body:
        if isinstance(node, ast.Assign):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names

def code_of(func):
    """A function's source with its comments and docstring removed.

    A test that bans a substring has to look at code only. Reading raw source
    fails a fellow who mentions the banned thing in a comment -- "no isinstance
    here" would fail a check for "isinstance" -- which is a correct answer
    rejected for its prose.
    """
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                node.body = body[1:] or [ast.Pass()]
    return ast.unparse(ast.fix_missing_locations(tree))

def as_written(module, name, cls=None):
    """One function's body as it appears in the file, with decorators ignored.

    Reading a decorated function at runtime gives you the wrapper, so its own
    body is out of reach. Parsing the file instead shows what the fellow wrote,
    and works whatever shape their decorator took -- a closure, a class with
    __call__, or functools.wraps on top of either.
    """
    tree = ast.parse(inspect.getsource(module))
    scope = tree.body
    if cls is not None:
        scope = next(n.body for n in tree.body
                     if isinstance(n, ast.ClassDef) and n.name == cls)
    found = next((n for n in scope
                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                  and n.name == name), None)
    assert found is not None, f"Keep a function named {name}."
    return "\n".join(ast.unparse(stmt) for stmt in found.body)


import importlib.util
from abc import ABC, abstractmethod
from pathlib import Path

import pytest

from from_scratch import (Bike, CargoBike, ClassicBike, ElectricBike, Fleet, Helmet, Rentable, Scooter,
                          fleet_revenue, is_cheap, rate_of, costs_less_than)


TEST_SUITE_NAME = "From Scratch Tests"


def a_fleet():
    """One of each kind of item, added in an order that is not sorted by rate."""
    fleet = Fleet()
    fleet.add(ClassicBike("A1", "Grand Army", needs_repair=False))                     # 4.00
    fleet.add(ElectricBike("E9", "Borough Hall", needs_repair=True, battery_range=24))  # 7.50
    fleet.add(Scooter("S1", charge=80, needs_repair=False))                             # 5.00
    fleet.add(Helmet("H1", needs_cleaning=False))                                       # 1.00
    return fleet


def serials(items):
    return [item.serial for item in items]


# ---------- Question 1: fleet_revenue ----------

def test_fleet_revenue_adds_up_one_kind():
    """fleet_revenue - a list of one kind of bike"""
    items = [ClassicBike("A1", "Grand Army", needs_repair=False),
             ClassicBike("A2", "Grand Army", needs_repair=False)]

    assert fleet_revenue(items, hours=1) == 8.00


def test_fleet_revenue_adds_up_a_mixed_fleet():
    """fleet_revenue - each kind of bike contributes its own rate"""
    items = [ClassicBike("A1", "Grand Army", needs_repair=False),
             ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24),
             CargoBike("C3", "Grand Army", needs_repair=False, crate_litres=90)]

    assert fleet_revenue(items, hours=2) == 34.00


def test_fleet_revenue_of_an_empty_list_is_zero():
    """fleet_revenue - an empty list earns nothing"""
    assert fleet_revenue([], hours=8) == 0


def test_fleet_revenue_never_checks_the_class():
    """fleet_revenue - the right answer, reached without checking any item's class"""
    assert fleet_revenue([ClassicBike("A1", "Grand Army", needs_repair=False)], hours=1) == 4.00

    source = code_of(fleet_revenue)
    for banned in ("isinstance", "type(", "__class__", "__name__"):
        assert banned not in source, \
            f"Remove {banned}. Call hourly_rate() on each item instead of checking its class."


# ---------- Question 2: Scooter ----------

def test_scooter_stores_its_own_data():
    """Scooter - __init__ stores the serial, charge and repair flag"""
    scooter = Scooter("S1", charge=80, needs_repair=False)

    assert scooter.serial == "S1"
    assert scooter.charge == 80
    assert scooter.needs_repair is False


def test_scooter_charges_five_dollars_an_hour():
    """Scooter - hourly_rate() returns 5.00"""
    assert Scooter("S1", charge=80, needs_repair=False).hourly_rate() == 5.00


def test_scooter_rentable_rule():
    """Scooter - rentable only with no repair needed and at least 20% charge"""
    assert Scooter("S1", charge=80, needs_repair=False).is_rentable() is True
    assert Scooter("S2", charge=10, needs_repair=False).is_rentable() is False, \
        "A scooter below 20% charge cannot be rented."
    assert Scooter("S3", charge=95, needs_repair=True).is_rentable() is False, \
        "A scooter that needs repair cannot be rented."
    assert Scooter("S4", charge=20, needs_repair=False).is_rentable() is True, \
        "Exactly 20% charge is enough."


def test_scooter_does_not_inherit_from_bike():
    """Scooter - it is not a Bike, and it does not inherit from one"""
    assert Scooter("S1", charge=80, needs_repair=False).hourly_rate() == 5.00
    assert not issubclass(Scooter, Bike), \
        "A scooter is not a kind of bike. Define the two methods yourself instead of inheriting them."


def test_fleet_revenue_works_on_scooters_too():
    """Scooter - fleet_revenue works on a list that mixes scooters and bikes"""
    items = [Scooter("S1", charge=80, needs_repair=False),
             ClassicBike("A1", "Grand Army", needs_repair=False)]

    assert fleet_revenue(items, hours=2) == 18.00


# ---------- Question 3: Rentable and Helmet ----------

def test_rentable_cannot_be_created():
    """Rentable - an abstract base class cannot be created itself"""
    with pytest.raises(TypeError):
        Rentable()


def test_rentable_marks_both_methods_abstract():
    """Rentable - is_rentable and hourly_rate are both abstract methods"""
    assert getattr(Rentable, "__abstractmethods__", frozenset()) == {"is_rentable", "hourly_rate"}, \
        "Inherit from ABC, and put @abstractmethod above both methods."


def test_a_rentable_missing_a_method_cannot_be_created():
    """Rentable - a subclass missing hourly_rate raises TypeError when created"""
    class Towel(Rentable):
        def is_rentable(self):
            return True

    with pytest.raises(TypeError):
        Towel()


def test_helmet_stores_its_own_data():
    """Helmet - __init__ stores the serial and the cleaning flag"""
    helmet = Helmet("H1", needs_cleaning=False)

    assert helmet.serial == "H1"
    assert helmet.needs_cleaning is False


def test_helmet_is_a_complete_rentable():
    """Helmet - it inherits from Rentable and defines both methods"""
    helmet = Helmet("H1", needs_cleaning=False)

    assert isinstance(helmet, Rentable), "Helmet should inherit from Rentable."
    assert helmet.hourly_rate() == 1.00
    assert helmet.is_rentable() is True


def test_helmet_that_needs_cleaning_is_not_rentable():
    """Helmet - a helmet that needs cleaning cannot be rented"""
    assert Helmet("H2", needs_cleaning=True).is_rentable() is False


# ---------- Question 4: testing Rentable ----------

YOUR_TESTS = Path(__file__).parent.parent / "my_tests" / "test_rentable.py"


class WorkingRentable(ABC):
    @abstractmethod
    def is_rentable(self):
        pass

    @abstractmethod
    def hourly_rate(self):
        pass


class RentableWithoutTheHourlyRateRule(ABC):
    @abstractmethod
    def is_rentable(self):
        pass

    def hourly_rate(self):
        pass


class RentableThatRefusesEverything(WorkingRentable):
    @abstractmethod
    def inspection_date(self):
        pass


def your_test(name, rentable_class, monkeypatch):
    """One of the fellow's tests, set to run against the given Rentable.

    Their file imports Rentable from from_scratch, and their subclasses are
    defined inside each test, so they look the name up when the test runs.
    Replacing the name in the loaded file grades the test itself, whatever
    state their own Rentable is in.
    """
    spec = importlib.util.spec_from_file_location("your_rentable_tests", YOUR_TESTS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "Rentable", rentable_class)
    test = getattr(module, name, None)
    assert test is not None, f"Keep the name {name} for your test in {YOUR_TESTS.name}."
    return test


def test_your_missing_method_test_catches_a_rentable_without_the_rule(monkeypatch):
    """Your tests - the missing-method test passes on a working Rentable and fails when hourly_rate is not abstract"""
    name = "test_a_rentable_missing_hourly_rate_cannot_be_created"

    your_test(name, WorkingRentable, monkeypatch)()

    broken_test = your_test(name, RentableWithoutTheHourlyRateRule, monkeypatch)
    # pytest.raises reports a missing error with its own exception, not AssertionError.
    try:
        broken_test()
    except (AssertionError, pytest.fail.Exception):
        return
    pytest.fail("Your test passed against a Rentable whose hourly_rate is not abstract, "
                "so it would not catch a subclass that leaves hourly_rate out.")


def test_your_complete_rentable_test_catches_a_rentable_that_refuses_everything(monkeypatch):
    """Your tests - the complete-subclass test passes on a working Rentable and fails when every subclass is refused"""
    name = "test_a_complete_rentable_can_be_created"

    your_test(name, WorkingRentable, monkeypatch)()

    broken_test = your_test(name, RentableThatRefusesEverything, monkeypatch)
    try:
        broken_test()
    except (AssertionError, TypeError, pytest.fail.Exception):
        return
    pytest.fail("Your test passed against a Rentable that refuses even a subclass defining both methods, "
                "so it would not catch an abstract base class that refuses everything.")


# ---------- Question 5: Fleet ----------

def test_a_new_fleet_is_empty():
    """Fleet - a new fleet starts with an empty list of items"""
    assert Fleet().items == []


def test_fleet_add_keeps_the_order_items_were_added():
    """Fleet - add() puts each item at the end of items"""
    assert serials(a_fleet().items) == ["A1", "E9", "S1", "H1"]


def test_find_with_a_named_function():
    """Fleet - find() keeps the items its callback returns True for"""
    assert serials(a_fleet().find(is_cheap)) == ["A1", "H1"]


def test_find_with_a_lambda():
    """Fleet - find() works with any callback, including a lambda"""
    fleet = a_fleet()

    assert serials(fleet.find(lambda item: item.is_rentable())) == ["A1", "S1", "H1"]
    assert serials(fleet.find(lambda item: item.serial.startswith("S"))) == ["S1"]
    assert fleet.find(lambda item: False) == []


def test_find_returns_a_new_list():
    """Fleet - find() leaves the fleet's own list unchanged"""
    fleet = a_fleet()
    found = fleet.find(lambda item: True)
    found.clear()

    assert serials(fleet.items) == ["A1", "E9", "S1", "H1"], \
        "Build a new list in find() rather than returning self.items."


def test_find_calls_its_callback_once_per_item():
    """Fleet - find() calls the callback itself, once for each item"""
    seen = []

    def remember(item):
        seen.append(item.serial)
        return True

    a_fleet().find(remember)

    assert seen == ["A1", "E9", "S1", "H1"]


# ---------- Question 6: sorting the fleet ----------

def test_cheapest_first_sorts_by_rate():
    """Fleet - cheapest_first() returns the items from lowest rate to highest"""
    assert serials(a_fleet().cheapest_first()) == ["H1", "A1", "S1", "E9"]


def test_cheapest_first_leaves_the_fleet_alone():
    """Fleet - cheapest_first() returns a new list and leaves items in the order they were added"""
    fleet = a_fleet()
    fleet.cheapest_first()

    assert serials(fleet.items) == ["A1", "E9", "S1", "H1"], \
        "Use sorted(), which returns a new list, rather than .sort(), which reorders the list itself."


def test_cheapest_first_passes_rate_of_as_its_key():
    """Fleet - cheapest_first() hands rate_of to sorted() as the key"""
    source = code_of(Fleet.cheapest_first)

    assert "key=rate_of" in source.replace(" ", ""), "Pass rate_of to sorted() as key=rate_of."
    assert "lambda" not in source, "cheapest_first() should use the named function rate_of."


def test_priciest_returns_the_most_expensive_item():
    """Fleet - priciest() returns the one item with the highest rate"""
    assert a_fleet().priciest().serial == "E9"


def test_priciest_uses_a_lambda_as_its_key():
    """Fleet - priciest() writes its key inline with a lambda"""
    source = code_of(Fleet.priciest)

    assert "lambda" in source, "Write priciest()'s key as a lambda."
    assert "max(" in source, "max() with a key returns the item whose key is largest."


# ---------- Question 7: costs_less_than ----------

def test_costs_less_than_returns_a_function():
    """costs_less_than - it returns a function, not True or False"""
    assert callable(costs_less_than(5.00)), \
        "Return the inner function itself, with no parentheses after its name."


def test_costs_less_than_builds_a_working_test():
    """costs_less_than - the returned function is True when an item costs less than the limit"""
    under_five = costs_less_than(5.00)

    assert under_five(Helmet("H1", needs_cleaning=False)) is True
    assert under_five(Scooter("S1", charge=80, needs_repair=False)) is False


def test_costs_less_than_works_with_find():
    """costs_less_than - its result can be passed straight to Fleet.find()"""
    fleet = a_fleet()

    assert serials(fleet.find(costs_less_than(5.00))) == ["A1", "H1"]
    assert serials(fleet.find(costs_less_than(2.00))) == ["H1"]
    assert serials(fleet.find(costs_less_than(8.00))) == ["A1", "E9", "S1", "H1"]


def test_each_function_from_costs_less_than_keeps_its_own_limit():
    """costs_less_than - two functions built from it each keep their own limit"""
    under_two = costs_less_than(2.00)
    under_eight = costs_less_than(8.00)
    classic = ClassicBike("A1", "Grand Army", needs_repair=False)

    assert under_two(classic) is False
    assert under_eight(classic) is True
    assert under_two(classic) is False, "Building under_eight should not change under_two."
