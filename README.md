# Polymorphism and Functions as Values

Let each kind of object answer for itself, and start passing functions around as values.

**Practicing:** polymorphism, duck typing, abstract base classes, contracts, higher-order functions, `sorted(key=)`, `lambda`

- [AI Use on This Assignment](#ai-use-on-this-assignment)
- [Setup](#setup)
- [Before You Start](#before-you-start)
  - [Syntax to recognize](#syntax-to-recognize)
  - [Look these up yourself](#look-these-up-yourself)
- [From Scratch](#from-scratch)
  - [Question 1: `fleet_revenue`](#question-1-fleet_revenue)
  - [Question 2: `Scooter`](#question-2-scooter)
  - [Question 3: `Rentable` and `Helmet`](#question-3-rentable-and-helmet)
  - [Question 4: `cheapest_first`](#question-4-cheapest_first)
- [Modify](#modify)
  - [Question 5: `late_fee`](#question-5-late_fee)
  - [Question 6: `Station.bikes_where`](#question-6-stationbikes_where)
  - [Question 7: `busiest_first`](#question-7-busiest_first)
- [Debug](#debug)
  - [Question 8: `restock_message`](#question-8-restock_message)
  - [Question 9: `Screening`](#question-9-screening)
- [Submitting](#submitting)
- [Good luck!](#good-luck)

## AI Use on This Assignment

**Tutor mode, for this whole quarter.** The AI explains, questions, quizzes,
and critiques, and you write every line you submit. Quarter 1 is where you
build the habit of writing code by hand; asking an AI to write it for you
comes later, in Quarter 2, where the job becomes judging code rather than
producing it.

For this assignment that means asking it why a loop over a mixed list needs no
`isinstance()`, or having it quiz you on the difference between `is_full` and
`is_full()` until you can say which one a higher-order function wants. Ask it a
hundred questions — that is the whole point. What you do not do is ask it for
the answer. Paste this at the start of a chat and it will hold for the rest of
the conversation:

> You are acting as a tutor. Your job is to explain what this coding question
> is asking, clarify confusing wording, and highlight the relevant concepts I
> need to know — but do not provide the full solution or code that directly
> answers the question. Instead, rephrase the problem in simpler terms,
> identify what is being tested, and suggest what steps or thought processes
> might help. Ask me guiding questions to make sure I am thinking critically.
> Do not write the final function, algorithm, or code implementation.

You own every line you submit, and you will be asked to explain it.

## Setup

Clone your repository in `development/mod-2` and then `cd` into it. Set up
your virtual environment and make a draft branch before you start.

```sh
git clone [your_repo]
cd [your_repo]
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
git checkout -b draft
```

Run `pytest` to test the entire assignment. To run one question, pass part of
its name: `pytest -k Bike`. Every push runs the tests on GitHub and reports
which ones passed in the **Actions** tab.

Push before it is finished. Your instructor grades this against the rubric,
not against the test count, so treat submitting as a checkpoint rather than a
finish line and come back to improve it.

When you are done working on this assignment, turn off your virtual
environment by running:

```sh
deactivate
```

## Before You Start

Skim this section before you read the lessons, so you know what to look for in
them. Classes, inheritance, `super()` and properties are all assumed here. The
new material is **letting each object answer for itself**, and **passing
functions around as values**.

This assignment has three sections:

1. From Scratch
2. Modify
3. Debug

<details>
<summary><strong>Ideas to look for</strong> — the ideas behind the questions, if you want them up front</summary>

Each question depends on one or more of these ideas. Part of the work is
deciding which.

| Idea | Lesson |
| --- | --- |
| One loop can work on several kinds of object as long as every one of them answers the same method name. The loop asks; it does not check. That is polymorphism, and the benefit belongs to the caller, which got simpler. | 2.5 |
| An `isinstance` chain is the shape to watch for. It means a fact about one kind of object is living in a function instead of on that kind of object, so adding a new kind means editing the function. | 2.5 |
| **Duck typing** means an object qualifies by answering the names a caller uses, not by what it inherits. Two classes can answer the same question for completely different reasons. | 2.5 |
| The set of method names a group of classes must all answer is their **contract**. Writing it down is the first specification you record in this module. | 2.5 |
| An **abstract base class** writes the contract into code. A class inheriting `ABC` with an `@abstractmethod` cannot be instantiated, and nor can a subclass that leaves one out — Python raises `TypeError` at the line that tried to build it. | 2.5 |
| Enforcing a contract with an abstract base class and documenting a duck-typed one are both real choices. Each fails somewhere, and knowing where is the skill. | 2.5 |
| Functions are values. They can be stored in a variable, passed to another function, and returned from one, exactly like a number or a list. | 2.6 |
| A **higher-order function** takes a function as an argument or returns one. `sorted(items, key=...)` takes one. | 2.6 |
| `sorted()` needs a `key=` function when the items are not numbers, because it cannot guess what to sort objects by. It returns a new list and leaves the original alone. | 2.6 |
| A `lambda` writes a short function inline, where one is expected. It is worth using when the function is tiny and needed once. | 2.6 |
| `is_low` is a function. `is_low()` is the value calling it produced. A higher-order function wants the first, because it calls the function itself. Passing the second is the most common mistake here, and the error is `'bool' object is not callable`. | 2.6 |

</details>

### Syntax to recognize

```python
from abc import ABC, abstractmethod


class Rentable(ABC):                     # an abstract base class
    @abstractmethod
    def hourly_rate(self):               # named in the contract, no body
        pass


for bike in bikes:                       # one loop, several kinds
    total += bike.hourly_rate()          # ask, do not check the type

sorted(bikes, key=rate_of)               # pass the function
sorted(bikes, key=lambda b: b.rate)      # or write it inline
sorted(docks, key=..., reverse=True)     # largest first

def bikes_where(self, test):             # a method taking a function
    return [b for b in self.bikes if test(b)]

message_if(station, station.is_low)      # pass it
message_if(station, station.is_low())    # calls it first — a bool, not a function
```

### Look these up yourself

- `sorted()`. You need its `key=` and `reverse=` arguments, and no lesson walks
  through them. Read about it on
  [W3Schools](https://www.w3schools.com/python/ref_func_sorted.asp).
- `abc`. The module `ABC` and `abstractmethod` come from. Read the
  [`ABC`](https://docs.python.org/3/library/abc.html#abc.ABC) and
  [`abstractmethod`](https://docs.python.org/3/library/abc.html#abc.abstractmethod)
  entries in the Python docs and skip the rest of that page — the opening is
  about machinery you do not need yet.

## From Scratch

Write these functions and classes in `src/from_scratch.py`.

### Question 1: `fleet_revenue`

Boro Bikes needs a day's revenue across the whole fleet. The fleet holds three
kinds of bike, each charging a different hourly rate, and the finance team keeps
asking for the number.

**`Bike`, `ClassicBike`, `ElectricBike` and `CargoBike` are already written for
you** in `src/from_scratch.py`. Read their `hourly_rate()` methods before you
start.

Write `fleet_revenue(bikes, hours)`, which returns what the whole list would
earn if every bike in it were rented for `hours` hours.

```python
fleet = [
    ClassicBike("A1", "Grand Army", False),       # 4.00 an hour
    ElectricBike("E9", "Borough Hall", False, 24),  # 7.50 an hour
    CargoBike("C3", "Grand Army", False, 90),     # 5.50 an hour
]

fleet_revenue(fleet, 2)          # 34.0 — (4.00 + 7.50 + 5.50) * 2
fleet_revenue([], 8)             # 0 — an empty fleet earns nothing
```

**Your loop must not ask what kind of bike it is holding.** No `isinstance()`,
no `type()`, and no checking a class name. A test checks for this.

Each bike already knows its own rate, so the loop's job is only to ask. That is
the whole idea: the function works for a kind of bike that does not exist yet,
as long as that kind answers `hourly_rate()`.

### Question 2: `Scooter`

Boro Bikes is adding scooters. A scooter is not a bike — it does not dock at a
station, it has no frame size, and nothing about `Bike` describes it. But the
revenue report, the rental screen and the maintenance list all have to include
scooters tomorrow.

Those three places only ever ask a thing two questions: **can I rent it**, and
**what does it cost an hour**. That pair of method names is the **contract**.

Write a class `Scooter` that answers the contract **without inheriting from
`Bike`**.

`__init__` takes a serial, a charge level as a percentage, and a repair flag.

| Method | Does | Returns |
| --- | --- | --- |
| `is_rentable()` | A scooter needs no repair and at least 20% charge | `True` or `False` |
| `hourly_rate()` | Scooters are a flat `5.00` an hour | `5.00` |

```python
scooter = Scooter("S1", 80, False)
scooter.is_rentable()            # True
scooter.hourly_rate()            # 5.0

Scooter("S2", 10, False).is_rentable()   # False — not enough charge
Scooter("S3", 95, True).is_rentable()    # False — needs repair

isinstance(scooter, Bike)        # False — it is not a bike and never was

# the same loop works on a list holding both
sum(item.hourly_rate() for item in [scooter, ClassicBike("A1", "Grand Army", False)])
# 9.0
```

This is **duck typing**: the loop does not care what a thing is, only that it
answers the names the loop uses. `Scooter` passes because it answers them, not
because of what it inherits.

Notice that a scooter decides `is_rentable()` by its own rule, using charge,
which no bike has. Two classes can answer the same question for completely
different reasons. That is the point of asking rather than checking.

### Question 3: `Rentable` and `Helmet`

The contract in the last question — `is_rentable()` and `hourly_rate()` — is
written down nowhere. A new engineer added a class, forgot `hourly_rate()`, and
nothing complained until the revenue report crashed in front of the finance
team.

An **abstract base class** writes the contract down and refuses to let an
incomplete class be instantiated at all. The failure moves from the revenue
report to the line that made the object.

Write `Rentable`, an abstract base class with two abstract methods,
`is_rentable()` and `hourly_rate()`. Then write `Helmet`, a real subclass of it.

`Helmet.__init__` takes a serial and a `needs_cleaning` flag.

| Class | Member | Returns |
| --- | --- | --- |
| `Rentable` | `is_rentable()` | abstract — no body |
| `Rentable` | `hourly_rate()` | abstract — no body |
| `Helmet` | `is_rentable()` | `True` unless it needs cleaning |
| `Helmet` | `hourly_rate()` | `1.00` |

```python
helmet = Helmet("H1", False)
helmet.is_rentable()             # True
helmet.hourly_rate()             # 1.0
Helmet("H2", True).is_rentable() # False

Rentable()                       # TypeError — abstract, so it cannot be made

class Towel(Rentable):           # forgets hourly_rate
    def is_rentable(self):
        return True

Towel()                          # TypeError, and it names the missing method
```

`ABC` and `abstractmethod` both come from Python's `abc` module:

```python
from abc import ABC, abstractmethod
```

A class inheriting `ABC` with at least one `@abstractmethod` cannot be
instantiated, and neither can a subclass that leaves one unimplemented. You do
not write that error — Python raises it, and the message names what is missing.

Use `pass` for each abstract method's body. The method exists to be named in the
contract, not to do anything.

### Question 4: `cheapest_first`

The rental screen shows the fleet cheapest first. `sorted()` can do this, but
only if you tell it what to sort by, because a `Bike` is not a number and Python
will not guess.

`sorted(items, key=...)` takes a **function** as its `key`. It calls that
function on each item and sorts by what comes back. A function that takes
another function like this is a **higher-order function**.

Write the same sort twice, so you have both forms.

**`Bike` and its three subclasses are already written for you.**

| Write | Does |
| --- | --- |
| `rate_of(bike)` | Returns one bike's hourly rate. A plain named function |
| `cheapest_first(bikes)` | Returns a **new** list sorted by rate, passing `rate_of` as the key |
| `cheapest_first_lambda(bikes)` | The same thing, with a `lambda` written inline as the key |

```python
fleet = [
    ElectricBike("E9", "Borough Hall", False, 24),  # 7.50
    ClassicBike("A1", "Grand Army", False),         # 4.00
    CargoBike("C3", "Grand Army", False, 90),       # 5.50
]

[bike.serial for bike in cheapest_first(fleet)]
# ["A1", "C3", "E9"]

[bike.serial for bike in cheapest_first_lambda(fleet)]
# ["A1", "C3", "E9"] — same answer
fleet[0].serial                  # "E9" — sorted() left the original alone
```

Pass `rate_of`, do not call it. `key=rate_of` hands `sorted` the function.
`key=rate_of(bike)` calls it immediately and hands over a number, which is the
most common mistake with higher-order functions and the subject of a later
question.

The two versions behave identically. A `lambda` is worth using when the function
is this short and needed in exactly one place; a named function is worth it when
the name explains something or you need it twice.

## Modify

Change the code already in `src/modify.py`.

### Question 5: `late_fee`

`late_fee` charges a different amount per late hour depending on the kind of
bike, and it decides by asking what kind it is holding. Adding scooters next
week means editing this function, and every other function shaped like it.

Move each fee onto the class it belongs to, so `late_fee` does not have to ask.

The code is in `src/modify.py`. When you are done:

- Each of the three classes has a `late_fee_per_hour()` method returning its own
  fee.
- `late_fee(bike, hours)` has no `isinstance` and no `type` in it, and still
  returns the same numbers.

```python
late_fee(ClassicBike("A1", "Grand Army", False), 2)        # 3.0
late_fee(ElectricBike("E9", "Borough Hall", False, 24), 2) # 9.0
late_fee(CargoBike("C3", "Grand Army", False, 90), 2)      # 5.0
```

Same answers as now — this is a refactor, so the numbers must not move.

The fees are in the function today, so read them out of it rather than inventing
them.

Ask yourself where a fee belongs. A classic bike's late fee is a fact about
classic bikes, so it belongs on `ClassicBike`, not in a function that has to be
told about every kind of bike that will ever exist.

### Question 6: `Station.bikes_where`

`Station` has three methods that are the same loop three times. Each one walks
the station's bikes, keeps the ones matching a condition, and returns a new
list. Only the condition differs.

The next request will be "bikes under 5.00 an hour", and the answer should not
be a fourth copy of the loop.

Replace all three with **one method that takes the condition as an argument**.
The method is waiting in `src/modify.py`.

```python
station = Station("Grand Army")
station.dock(Bike("A1", "Grand Army", False))
station.dock(Bike("A2", "Grand Army", True))

[b.serial for b in station.bikes_where(lambda bike: bike.is_rentable())]
# ["A1"]

[b.serial for b in station.bikes_where(lambda bike: bike.needs_repair)]
# ["A2"]

def is_cheap(bike):
    return bike.hourly_rate() < 5.00

[b.serial for b in station.bikes_where(is_cheap)]
# ["A1", "A2"] — a condition the class was never written for

station.bikes_where(lambda bike: False)   # [] — nothing matches
```

**Delete `rentable`, `repair_list` and `at_station` when you are done.** A test
checks they are gone.

`bikes_where` takes a function and calls it on each bike, keeping the bike when
the call returns true. A method that takes a function like this is a
**higher-order function**, and it turns a class that answers three fixed
questions into one that answers any question of that shape.

Call the parameter something that says what it is for, such as `test` or
`matches`. It is a function, so you call it: `test(bike)`.

### Question 7: `busiest_first`

`busiest_first` sorts docks by how many rides started there, most first. It does
it by building a list of `(rides, dock)` pairs, sorting those, reversing, and
pulling the docks back out. It works, and it is eleven lines of code that
`sorted` does in one.

Rewrite it using `sorted()` with a `key=` function. The code is in
`src/modify.py`.

```python
docks = [Dock("Grand Army", 14), Dock("Borough Hall", 31), Dock("Prospect", 22)]

[dock.name for dock in busiest_first(docks)]
# ["Borough Hall", "Prospect", "Grand Army"]

docks[0].name                    # "Grand Army" — the original is untouched
```

Two things to find in the docs rather than work around:

- `sorted` takes `reverse=True`, so you do not need to sort and then reverse.
- `key=` takes a function of one item that returns the value to sort by.

The pair-building version has a bug you inherit if you keep it: two docks with
the same ride count get compared by their second element, the `Dock` object
itself, which Python cannot order. `sorted` with a `key` never compares the
objects, so the bug disappears rather than being fixed. A test covers it.

## Debug

Fix the code in `src/debug.py`.

### Question 8: `restock_message`

`restock_message` asks `message_if` to build a warning when a station is low on
bikes. It raises:

```python
restock_message(Station("Grand Army", 1))
# TypeError: 'bool' object is not callable
```

Read the message literally. Something is being called, and the thing being
called is a `bool`. `message_if` calls what it is handed. So what did it get
handed?

Fix `restock_message` in `src/debug.py`.

```python
restock_message(Station("Grand Army", 1))     # "Grand Army: send bikes"
restock_message(Station("Borough Hall", 9))   # "Borough Hall: ok"
```

`station.is_low` is the **function**. `station.is_low()` is the `True` or
`False` that calling it produced. `message_if` needs the first one, because it
decides for itself when to call it.

This is the most common mistake with higher-order functions, and Python cannot
warn you where you make it. Passing a value where a function was wanted is only
discovered later, when something tries to call that value — which is why the
traceback points at `message_if`, a function that is not wrong.

`message_if` and `Station` are both correct. Two characters are the whole bug.

### Question 9: `Screening`

`Rental` is an abstract base class naming the two methods every rentable thing
must answer. `Tandem` works. `Screening`, added last week, does not:

```python
Screening("SC1", 40)
# TypeError: Can't instantiate abstract class Screening without an
# implementation for abstract method 'hourly_rate'
```

This error is the abstract base class doing its job. The class is incomplete,
and Python refused to make one rather than letting a half-built object into the
fleet and crashing later in `fleet_total`.

Fix `Screening` in `src/debug.py`. A screening costs `6.00` an hour.

```python
screening = Screening("SC1", 40)
screening.hourly_rate()          # 6.0
screening.is_rentable()          # True — 40 seats left

Screening("SC2", 0).is_rentable()  # False — sold out

fleet_total([Tandem("T1", False), Screening("SC1", 40)], 2)   # 25.0
```

Read the error message rather than guessing. It names the class it could not
build and the exact method that is missing, which is more than most Python
errors tell you.

Do not fix this by removing `@abstractmethod` from `Rental`, and do not stop
`Screening` inheriting from it. Either one makes the error go away and puts the
crash back in `fleet_total`, which is what the abstract base class was added to
prevent.

## Submitting

```sh
git add -A
git commit -m "your message"
git push
```

Pushing runs the tests on GitHub. Check the **Actions** tab to see which
passed, then open a pull request to your instructor for feedback.

## Good luck!

Every system you build from here is made of classes, so this is the
assignment the rest of the module stands on. You got this!
