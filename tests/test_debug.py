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


from debug import Rental, Screening, Station, Tandem, fleet_total, message_if, restock_message


TEST_SUITE_NAME = "Debug Tests"


def test_restock_message_warns_a_low_station():
    """restock_message - it no longer raises, and it warns when bikes are low"""
    assert restock_message(Station("Grand Army", 1)) == "Grand Army: send bikes"


def test_restock_message_says_ok_when_there_are_enough():
    """restock_message - a station with enough bikes needs no warning"""
    assert restock_message(Station("Borough Hall", 9)) == "Borough Hall: ok"


def test_restock_message_passes_the_function_not_its_result():
    """restock_message - is_low is handed over uncalled"""
    source = code_of(restock_message)

    assert "is_low()" not in source, \
        "Pass station.is_low, with no parentheses. message_if calls it itself."
    assert "is_low" in source, "message_if still needs to be given the check."


def test_message_if_was_left_alone():
    """restock_message - message_if was never the bug"""
    source = code_of(message_if)

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
