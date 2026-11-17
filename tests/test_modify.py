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


from modify import Bike, CargoBike, ClassicBike, ElectricBike, Station, late_fee, make_discounter, member_price, staff_price


TEST_SUITE_NAME = "Modify Tests"


def test_the_fees_did_not_move():
    """late_fee - a refactor, so every answer is what it was before"""
    assert late_fee(ClassicBike("A1", "Grand Army", False), 2) == 3.00
    assert late_fee(ElectricBike("E9", "Borough Hall", False, 24), 2) == 9.00
    assert late_fee(CargoBike("C3", "Grand Army", False, 90), 2) == 5.00


def test_late_fee_no_longer_asks_what_kind_of_bike():
    """late_fee - no isinstance and no type left in the function"""
    source = code_of(late_fee)

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


import modify



def test_make_discounter_returns_a_function():
    """make_discounter - it hands back a function, it does not discount anything itself"""
    assert callable(make_discounter(0.10)), \
        "Return the inner function, with no parentheses."


def test_the_returned_function_uses_its_own_discount():
    """make_discounter - the closure remembers the discount it was built with"""
    assert make_discounter(0.10)(20.00) == 18.00
    assert make_discounter(0.25)(20.00) == 15.00


def test_two_discounters_do_not_share_a_discount():
    """make_discounter - each call builds a new closure"""
    member = make_discounter(0.10)
    staff = make_discounter(0.25)

    assert member(20.00) == 18.00
    assert staff(20.00) == 15.00
    assert member(20.00) == 18.00, "Building the second one must not change the first."


def test_the_two_built_functions_work():
    """make_discounter - member_price and staff_price are built from it"""
    assert callable(member_price), "Build member_price from make_discounter(0.10)."
    assert member_price(20.00) == 18.00
    assert staff_price(20.00) == 15.00


def test_the_old_function_is_gone():
    """make_discounter - discounted_price was deleted"""
    assert not hasattr(modify, "discounted_price"), \
        "Delete discounted_price. make_discounter replaces it."
