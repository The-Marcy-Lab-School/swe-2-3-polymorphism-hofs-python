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


from modify import Bike, CargoBike, ClassicBike, ElectricBike, late_fee


TEST_SUITE_NAME = "Modify Tests"


def test_the_fees_did_not_change():
    """late_fee - a refactor, so every answer is the same as before"""
    assert late_fee(ClassicBike("A1", "Grand Army", needs_repair=False), hours=2) == 3.00
    assert late_fee(ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24), hours=2) == 9.00
    assert late_fee(CargoBike("C3", "Grand Army", needs_repair=False, crate_litres=90), hours=2) == 5.00


def test_late_fee_no_longer_checks_the_class():
    """late_fee - no isinstance and no type left in the function"""
    source = code_of(late_fee)

    assert "isinstance" not in source, "Call the bike's late_fee_per_hour() instead of checking its class."
    assert "type(" not in source, "Call the bike's late_fee_per_hour() instead of checking its class."


def test_each_kind_of_bike_defines_its_own_fee():
    """late_fee - each subclass has a late_fee_per_hour() method"""
    assert ClassicBike("A1", "Grand Army", needs_repair=False).late_fee_per_hour() == 1.50
    assert ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24).late_fee_per_hour() == 4.50
    assert CargoBike("C3", "Grand Army", needs_repair=False, crate_litres=90).late_fee_per_hour() == 2.50


def test_a_plain_bike_charges_no_late_fee():
    """late_fee - Bike's own late_fee_per_hour() returns what the else branch did"""
    assert Bike("B0", "Grand Army", needs_repair=False).late_fee_per_hour() == 0.00
    assert late_fee(Bike("B0", "Grand Army", needs_repair=False), hours=5) == 0.00


def test_a_new_kind_of_bike_needs_no_change_to_late_fee():
    """late_fee - a new subclass works without editing late_fee"""
    class FoldingBike(Bike):
        def late_fee_per_hour(self):
            return 2.00

    assert late_fee(FoldingBike("F1", "Grand Army", needs_repair=False), hours=3) == 6.00, \
        "late_fee should work for a kind of bike that did not exist when it was written."
