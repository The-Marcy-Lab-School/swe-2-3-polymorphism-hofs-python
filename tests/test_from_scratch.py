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


from from_scratch import Bike, CargoBike, ClassicBike, ElectricBike, Helmet, Rentable, Scooter, cheapest_first, cheapest_first_lambda, fleet_revenue, rate_of


TEST_SUITE_NAME = "From Scratch Tests"


def test_fleet_revenue_adds_up_one_kind():
    """fleet_revenue - a list of one kind of bike"""
    fleet = [ClassicBike("A1", "Grand Army", False),
             ClassicBike("A2", "Grand Army", False)]

    assert fleet_revenue(fleet, 1) == 8.00


def test_fleet_revenue_adds_up_a_mixed_fleet():
    """fleet_revenue - each kind contributes its own rate"""
    fleet = [ClassicBike("A1", "Grand Army", False),
             ElectricBike("E9", "Borough Hall", False, 24),
             CargoBike("C3", "Grand Army", False, 90)]

    assert fleet_revenue(fleet, 2) == 34.00


def test_fleet_revenue_of_an_empty_fleet_is_zero():
    """fleet_revenue - a for loop may run over an empty list"""
    assert fleet_revenue([], 8) == 0


def test_fleet_revenue_never_asks_what_kind_of_bike():
    """fleet_revenue - the right answer, reached without asking what kind"""
    assert fleet_revenue([ClassicBike("A1", "Grand Army", False)], 1) == 4.00

    source = code_of(fleet_revenue)

    for banned in ("isinstance", "type(", "__class__", "__name__"):
        assert banned not in source, \
            f"Remove {banned} — every bike already knows its own rate, so just ask it."


def test_scooter_answers_the_contract():
    """Scooter - it has both method names the callers use"""
    scooter = Scooter("S1", 80, False)

    assert scooter.hourly_rate() == 5.00
    assert scooter.is_rentable() is True


def test_scooter_has_its_own_rule_for_being_rentable():
    """Scooter - charge and repair both matter, by the scooter's own rule"""
    assert Scooter("S2", 10, False).is_rentable() is False, \
        "A scooter below 20% charge cannot be rented."
    assert Scooter("S3", 95, True).is_rentable() is False, \
        "A scooter needing repair cannot be rented."
    assert Scooter("S4", 20, False).is_rentable() is True, \
        "Exactly 20% is enough."


def test_scooter_does_not_inherit_from_bike():
    """Scooter - it satisfies the contract without being a Bike"""
    assert Scooter("S1", 80, False).hourly_rate() == 5.00

    assert not issubclass(Scooter, Bike), \
        "A scooter is not a kind of bike. Answer the contract instead of inheriting."


def test_one_loop_covers_scooters_and_bikes():
    """Scooter - a caller that only uses the contract works on both"""
    mixed = [Scooter("S1", 80, False), ClassicBike("A1", "Grand Army", False)]

    assert sum(item.hourly_rate() for item in mixed) == 9.00
    assert all(item.is_rentable() for item in mixed)


import pytest



def test_rentable_cannot_be_instantiated():
    """Rentable - an abstract base class refuses to be made"""
    with pytest.raises(TypeError):
        Rentable()


def test_rentable_names_both_methods_as_abstract():
    """Rentable - both is_rentable and hourly_rate are abstract"""
    assert getattr(Rentable, "__abstractmethods__", frozenset()) == \
        {"is_rentable", "hourly_rate"}, \
        "Decorate both methods with @abstractmethod, and inherit from ABC."


def test_an_incomplete_subclass_cannot_be_instantiated():
    """Rentable - a subclass missing hourly_rate raises TypeError when made"""
    class Towel(Rentable):
        def is_rentable(self):
            return True

    with pytest.raises(TypeError):
        Towel()


def test_helmet_is_a_complete_subclass():
    """Helmet - it implements both methods, so it can be made"""
    helmet = Helmet("H1", False)

    assert isinstance(helmet, Rentable)
    assert helmet.hourly_rate() == 1.00
    assert helmet.is_rentable() is True


def test_helmet_refuses_when_it_needs_cleaning():
    """Helmet - its own rule decides whether it can be rented"""
    assert Helmet("H2", True).is_rentable() is False


import inspect



def fleet():
    return [ElectricBike("E9", "Borough Hall", False, 24),
            ClassicBike("A1", "Grand Army", False),
            CargoBike("C3", "Grand Army", False, 90)]


def test_rate_of_reports_one_bikes_rate():
    """rate_of - a plain function, so it can be handed to sorted as a key"""
    assert rate_of(ClassicBike("A1", "Grand Army", False)) == 4.00
    assert rate_of(ElectricBike("E9", "Borough Hall", False, 24)) == 7.50


def test_cheapest_first_sorts_by_rate():
    """cheapest_first - cheapest to dearest, using the named key function"""
    assert [bike.serial for bike in cheapest_first(fleet())] == ["A1", "C3", "E9"]


def test_cheapest_first_leaves_the_original_alone():
    """cheapest_first - sorted returns a new list"""
    original = fleet()
    ordered = cheapest_first(original)

    assert [bike.serial for bike in ordered] == ["A1", "C3", "E9"]
    assert original[0].serial == "E9", "sorted() does not reorder what you passed it."


def test_the_lambda_version_gives_the_same_answer():
    """cheapest_first_lambda - the same sort, written inline"""
    assert [bike.serial for bike in cheapest_first_lambda(fleet())] == \
        ["A1", "C3", "E9"]


def test_each_version_uses_the_form_it_asks_for():
    """cheapest_first - one passes a named function, the other a lambda"""
    named = inspect.getsource(cheapest_first)
    inline = inspect.getsource(cheapest_first_lambda)

    assert "lambda" not in named, \
        "cheapest_first should pass the named function rate_of as its key."
    assert "rate_of" in named, "Pass rate_of to sorted as key=rate_of."
    assert "lambda" in inline, "cheapest_first_lambda should use a lambda as its key."
