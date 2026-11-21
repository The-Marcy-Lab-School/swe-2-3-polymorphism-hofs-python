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


from debug import Scooter, charging_list, needs_charging, scooters_where


TEST_SUITE_NAME = "Debug Tests"


def scooters():
    return [Scooter("S1", charge=80, needs_repair=False),
            Scooter("S2", charge=10, needs_repair=False),
            Scooter("S3", charge=5, needs_repair=True)]


def test_charging_list_finds_the_low_scooters():
    """charging_list - it no longer raises, and it returns the scooters below 20% charge"""
    assert [scooter.serial for scooter in charging_list(scooters())] == ["S2", "S3"]


def test_charging_list_of_full_scooters_is_empty():
    """charging_list - no scooter needs charging, so the list is empty"""
    assert charging_list([Scooter("S1", charge=80, needs_repair=False)]) == []


def test_charging_list_passes_the_function_not_its_result():
    """charging_list - needs_charging is passed with no parentheses"""
    source = code_of(charging_list)

    assert "needs_charging(" not in source, \
        "Pass needs_charging with no parentheses. scooters_where calls it itself."
    assert "needs_charging" in source, "scooters_where still needs to be given needs_charging."


def test_the_other_functions_were_left_alone():
    """charging_list - needs_charging and scooters_where were never the bug"""
    assert needs_charging(Scooter("S2", charge=10, needs_repair=False)) is True
    assert "matches(scooter)" in code_of(scooters_where), \
        "scooters_where calls the function it is given. That part was already right."
