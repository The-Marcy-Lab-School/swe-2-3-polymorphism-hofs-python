# Polymorphism and Functions as Values

Practice writing classes that share the same methods, so that one loop works on all of them, and practice passing functions to other functions.

**Practicing:** polymorphism, duck typing, abstract base classes, testing an abstract base class, higher-order functions, callbacks, `lambda`, `sorted()`, `max()`, `key=`, closures

- [AI Use on This Assignment](#ai-use-on-this-assignment)
- [Setup](#setup)
- [Before You Start](#before-you-start)
  - [Syntax to recognize](#syntax-to-recognize)
- [From Scratch](#from-scratch)
  - [Question 1: `fleet_revenue`](#question-1-fleet_revenue)
  - [Question 2: `Scooter`](#question-2-scooter)
  - [Question 3: `Rentable` and `Helmet`](#question-3-rentable-and-helmet)
  - [Question 4: Testing `Rentable`](#question-4-testing-rentable)
  - [Question 5: `Fleet` and `is_cheap`](#question-5-fleet-and-is_cheap)
  - [Question 6: Sorting the Fleet](#question-6-sorting-the-fleet)
  - [Question 7: `rate_under`](#question-7-rate_under)
- [Modify](#modify)
  - [Question 8: `late_fee`](#question-8-late_fee)
- [Debug](#debug)
  - [Question 9: `charging_list`](#question-9-charging_list)
- [Submitting](#submitting)
- [Good luck!](#good-luck)

## AI Use on This Assignment

**Tutor mode, for this whole quarter.** The AI explains, questions, quizzes,
and critiques, and you write every line you submit. Quarter 1 is where you
build the habit of writing code by hand; asking an AI to write it for you
comes later, in Quarter 2, where the job becomes judging code rather than
producing it.

For this assignment that means asking it why a loop over a mixed list needs no
`isinstance()`, or having it quiz you on the difference between `is_cheap` and
`is_cheap()` until you can say which one a higher-order function wants. Ask it a
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
its name: `pytest -k scooter`. Every push runs the tests on GitHub and reports
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

Skim this section before you read the lessons, so you know what to look for in them. Classes, inheritance, `super()` and properties are all assumed here. The new material is **classes that share the same methods**, and **functions passed around as values**.

This assignment has three sections:

1. From Scratch
2. Modify
3. Debug

<details>
<summary><strong>Ideas to look for</strong> — the ideas behind the questions, if you want them up front</summary>

Each question depends on one or more of these ideas. Part of the work is deciding which.

| Idea                                                                                                                                                                                                                                | Lesson |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| A function that checks each object's class with `isinstance()` needs a new branch for every new kind of object, and a missed branch gives a wrong answer without an error.                                                          | 2.5    |
| **Polymorphism** is different types of object responding to the same method call in their own way. When every kind of bike defines `hourly_rate()`, one loop can call `item.hourly_rate()` on each item without checking its class. | 2.5    |
| **Duck typing** means code calls the method it needs without checking the object's class. Any object that has the method works, even one whose class inherits from nothing.                                                         | 2.5    |
| A **contract** is the set of method names every type in a group promises to define, so that code using the group can call them on any member.                                                                                       | 2.5    |
| An **abstract base class** inherits from `ABC` and marks methods with `@abstractmethod`. Creating the abstract base class itself, or a subclass that leaves out one of those methods, raises `TypeError`.                           | 2.5    |
| `with pytest.raises(TypeError):` around the line that creates an object passes only if creating it raises a `TypeError`. A subclass that exists only to be refused is defined inside the test.                                      | 2.5    |
| A function is a value: it can be stored in a variable and passed to another function, like a number or a list.                                                                                                                      | 2.6    |
| A function passed into another function is a **callback**. A function that takes a function as an argument, or returns one, is a **higher-order function**. A callback that returns `True` or `False` is a **predicate**.           | 2.6    |
| Pass a callback by writing its name with no parentheses. With parentheses, Python calls the function before the higher-order function starts.                                                                                       | 2.6    |
| A **`lambda`** writes a one-expression function where it is used: `lambda item: item.hourly_rate()`.                                                                                                                                | 2.6    |
| `sorted()`, `min()` and `max()` take a `key` callback and call it on each element to get the value to compare. `sorted()` returns a new list.                                                                                       | 2.6    |
| A function defined inside another function and returned from it keeps access to the outer function's variables. That inner function is a **closure**.                                                                               | 2.6    |

</details>

### Syntax to recognize

This code combines examples from lessons 2.5 and 2.6. It runs as written, and the comments show what it prints.

```python
from abc import ABC, abstractmethod
from datetime import date, timedelta


class Event(ABC):                              # an abstract base class: an Event itself cannot be created
    def __init__(self, name, date, capacity, base_price):
        self.name = name
        self.date = date
        self.capacity = capacity
        self.base_price = base_price

    @abstractmethod
    def ticket_price(self):                    # every subclass must define ticket_price()
        return self.base_price

    @abstractmethod
    def can_refund(self, today):               # and can_refund(today)
        pass


class Concert(Event):                          # a concrete class: it defines both abstract methods
    SERVICE_FEE = 5

    def __init__(self, name, date, capacity, base_price, performer):
        super().__init__(name, date, capacity, base_price)
        self.performer = performer

    def ticket_price(self):
        return super().ticket_price() + Concert.SERVICE_FEE

    def can_refund(self, today):
        return today <= self.date - timedelta(days=7)


class Screening(Event):
    def ticket_price(self):
        return super().ticket_price()

    def can_refund(self, today):
        return False


class MuseumTour:                              # inherits from nothing, but defines the same two methods
    def __init__(self, name, date, price):
        self.name = name
        self.date = date
        self.price = price

    def ticket_price(self):
        return self.price

    def can_refund(self, today):
        return today < self.date


class Venue:
    def __init__(self, name):
        self.name = name
        self.events = []

    def add_event(self, event):
        self.events.append(event)

    def find_events(self, matches):            # a higher-order function: it takes a function
        return [event for event in self.events if matches(event)]


def is_in_december(event):                     # a predicate: it returns True or False
    return event.date.month == 12


def matches_month(month):                      # a higher-order function: it returns a function
    def matches(event):                        # a closure: it keeps access to month
        return event.date.month == month
    return matches                             # no parentheses: return the function without calling it


hall = Venue('Riverside Community Hall')
hall.add_event(Concert('Friday Night Jazz', date(2026, 12, 5), capacity=40, base_price=25, performer='The Blue Notes'))
hall.add_event(Screening('Movie Night: Coco', date(2026, 11, 28), capacity=30, base_price=8))
hall.add_event(MuseumTour('Gallery After Dark', date(2026, 12, 11), price=12))

today = date(2026, 12, 1)
for event in hall.events:                      # polymorphism: one loop, and each kind of event works out its own answer
    marker = ' (refundable)' if event.can_refund(today) else ''
    print(f'{event.name}: ${event.ticket_price()}{marker}')
# Friday Night Jazz: $30
# Movie Night: Coco: $8
# Gallery After Dark: $12 (refundable)

december = hall.find_events(is_in_december)                         # pass the function: no parentheses
cheap = hall.find_events(lambda event: event.ticket_price() < 10)   # or write it inline with lambda
november = hall.find_events(matches_month(11))                      # call matches_month to build the test
print([event.name for event in december])   # ['Friday Night Jazz', 'Gallery After Dark']
print([event.name for event in cheap])      # ['Movie Night: Coco']
print([event.name for event in november])   # ['Movie Night: Coco']

by_date = sorted(hall.events, key=lambda event: event.date)         # sorted() calls the key on each event
print([event.name for event in by_date])    # ['Movie Night: Coco', 'Friday Night Jazz', 'Gallery After Dark']
```

## From Scratch

Write these functions and classes in `src/from_scratch.py`. The questions build one system, so do them in order: Questions 5 to 7 use your answers to Questions 2 and 3.

The examples pass every number and every `True` or `False` by keyword, as in `Scooter("S1", charge=80, needs_repair=False)`, so that each value says what it is. Give each `__init__` parameter the name the examples use, or those tests will not pass.

### Question 1: `fleet_revenue`

Boro Bikes rents three kinds of bike: classic bikes, electric bikes, and cargo bikes. Each kind charges its own hourly rate. **`Bike`, `ClassicBike`, `ElectricBike` and `CargoBike` are already written for you** in `src/from_scratch.py`, and each kind's `hourly_rate()` method returns its rate.

Write a function called `fleet_revenue` that answers the question "how much would these items earn if each one were rented for this many hours?"

| Write                         | Takes                                 | Does                                                               |
| ----------------------------- | ------------------------------------- | ------------------------------------------------------------------ |
| `fleet_revenue(items, hours)` | a list of items and a number of hours | Returns the total of each item's hourly rate multiplied by `hours` |

**Requirements:** Do not use `isinstance()` or `type()` to check which kind of bike an item is. A test checks for this.

```python
items = [
    ClassicBike("A1", "Grand Army", needs_repair=False),                         # 4.00 an hour
    ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24),    # 7.50 an hour
    CargoBike("C3", "Grand Army", needs_repair=False, crate_litres=90),          # 5.50 an hour
]

fleet_revenue(items, hours=2)    # Returns 34.0, which is (4.00 + 7.50 + 5.50) * 2
fleet_revenue([], hours=8)       # Returns 0, because an empty list earns nothing
```

### Question 2: `Scooter`

Boro Bikes also rents electric scooters. A scooter has a serial and a charge level, measured as a percentage, and it either needs a repair or does not. A scooter can be rented when it does not need a repair and its charge is at least 20%. Every scooter costs $5.00 an hour. A scooter is not a kind of bike: it is not docked at a station.

Write a class called `Scooter` that has a serial, a charge, and whether it needs repair. It should answer the questions "can this scooter be rented?" and "what does this scooter cost an hour?"

| Write           | Takes                                                    | Does                                                                               |
| --------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `__init__`      | a serial, a charge, and whether the scooter needs repair | Stores them as `serial`, `charge`, and `needs_repair`                              |
| `is_rentable()` | nothing                                                  | Returns `True` when the scooter does not need repair and its charge is at least 20 |
| `hourly_rate()` | nothing                                                  | Returns `5.00`                                                                     |

**Requirements:** `Scooter` must **not** inherit from `Bike`. A test checks for this.

```python
scooter = Scooter("S1", charge=80, needs_repair=False)
scooter.is_rentable()                                     # Returns True
scooter.hourly_rate()                                     # Returns 5.0

Scooter("S2", charge=10, needs_repair=False).is_rentable()  # Returns False, because its charge is below 20
Scooter("S3", charge=95, needs_repair=True).is_rentable()   # Returns False, because it needs repair
isinstance(scooter, Bike)                                   # Returns False

# Your fleet_revenue from Question 1 works on a list of scooters and bikes, unchanged
fleet_revenue([scooter, ClassicBike("A1", "Grand Army", needs_repair=False)], hours=2)   # Returns 18.0
```

### Question 3: `Rentable` and `Helmet`

Boro Bikes also rents helmets, at $1.00 an hour. A helmet has a serial, and it can be rented unless it needs cleaning.

Everything Boro Bikes rents must be able to say whether it can be rented and what it costs an hour. Those two methods, `is_rentable()` and `hourly_rate()`, are the contract that `fleet_revenue` depends on.

Write an abstract base class called `Rentable` that names both methods of the contract. Then write a class called `Helmet` that inherits from `Rentable`. A helmet should answer the questions "can this helmet be rented?" and "what does this helmet cost an hour?"

| Class      | Write           | Takes                                           | Does                                                  |
| ---------- | --------------- | ----------------------------------------------- | ----------------------------------------------------- |
| `Rentable` | `is_rentable()` | nothing                                         | An abstract method                                    |
| `Rentable` | `hourly_rate()` | nothing                                         | An abstract method                                    |
| `Helmet`   | `__init__`      | a serial, and whether the helmet needs cleaning | Stores them as `serial` and `needs_cleaning`          |
| `Helmet`   | `is_rentable()` | nothing                                         | Returns `True` when the helmet does not need cleaning |
| `Helmet`   | `hourly_rate()` | nothing                                         | Returns `1.00`                                        |

`ABC` and `abstractmethod` are already imported at the top of `src/from_scratch.py`.

```python
helmet = Helmet("H1", needs_cleaning=False)
helmet.is_rentable()                               # Returns True
helmet.hourly_rate()                               # Returns 1.0
Helmet("H2", needs_cleaning=True).is_rentable()    # Returns False
isinstance(helmet, Rentable)                       # Returns True

Rentable()
# TypeError: Can't instantiate abstract class Rentable without an implementation for abstract methods 'hourly_rate', 'is_rentable'
```

### Question 4: Testing `Rentable`

Everything Boro Bikes rents must define `is_rentable()` and `hourly_rate()`. An abstract base class that enforces this contract keeps two promises: it refuses a subclass that is missing one of the methods, and it allows a subclass that defines both. A mistake in the abstract base class can break either promise, so each promise needs its own test.

Write two pytest tests that answer the questions "is a subclass missing `hourly_rate()` refused?" and "is a subclass that defines both methods allowed?" Write them in `my_tests/test_rentable.py`, which already imports `pytest` and `Rentable` and names both tests for you.

| Write                                                     | Does                                                                                                                                                                    |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_a_rentable_missing_hourly_rate_cannot_be_created()` | Defines a subclass of `Rentable` inside the test that defines only `is_rentable()`, and uses `pytest.raises(TypeError)` to check that creating one raises a `TypeError` |
| `test_a_complete_rentable_can_be_created()`               | Defines a subclass of `Rentable` inside the test that defines both methods, creates one, and asserts the value its `hourly_rate()` returns                              |

Run your tests with:

```sh
pytest my_tests
```

Both tests should pass once your `Rentable` from Question 3 works. The assignment's own tests then check each of your tests twice: once against a `Rentable` that works, where it must pass, and once against a `Rentable` that breaks the rule it checks, where it must fail. The first test must fail against a `Rentable` whose `hourly_rate()` is not abstract. The second test must fail against a `Rentable` that refuses every subclass.

> Your tests go in `my_tests/` rather than `tests/` because `tests/` is replaced with the assignment's own tests when your work is graded, so anything you write there is lost.

### Question 5: `Fleet`

Boro Bikes keeps every bike, scooter and helmet it rents in one fleet. Staff search the fleet with many different questions: which items can be rented right now, which items cost less than $5.00 an hour, which items are scooters.

Write a class called `Fleet` that has a list of items. It should answer any question of the form "which items in the fleet match this test?", where the caller passes the test in as a function.

**`is_cheap(item)` is already written for you** in `src/from_scratch.py`. It returns `True` when an item costs less than $5.00 an hour.

| Write                 | Takes                                                        | Does                                                                         |
| --------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `Fleet.__init__`      | nothing                                                      | Starts an empty list of items as `items`                                     |
| `Fleet.add(item)`     | one bike, scooter, or helmet                                 | Adds the item to the end of `items`                                          |
| `Fleet.find(matches)` | a function that takes one item and returns `True` or `False` | Returns a **new** list of the items for which `matches(item)` returns `True` |

```python
fleet = Fleet()
fleet.add(ClassicBike("A1", "Grand Army", needs_repair=False))                     # 4.00 an hour
fleet.add(ElectricBike("E9", "Borough Hall", needs_repair=True, battery_range=24))  # 7.50 an hour
fleet.add(Scooter("S1", charge=80, needs_repair=False))                             # 5.00 an hour
fleet.add(Helmet("H1", needs_cleaning=False))                                       # 1.00 an hour

cheap = fleet.find(is_cheap)
for item in cheap:
    print(item.serial)
# A1
# H1

rentable = fleet.find(lambda item: item.is_rentable())
for item in rentable:
    print(item.serial)
# A1
# S1
# H1

scooters = fleet.find(lambda item: item.serial.startswith("S"))
for item in scooters:
    print(item.serial)
# S1
```

### Question 6: Sorting the Fleet

Staff also list the fleet from the cheapest item to the most expensive, and look up the single most expensive item.

Add two methods to your `Fleet`. **`rate_of(item)` is already written for you** in `src/from_scratch.py`. It returns an item's hourly rate.

| Write                    | Takes    | Does                                                                            |
| ------------------------ | -------- | ------------------------------------------------------------------------------- |
| `Fleet.cheapest_first()` | nothing  | Returns a **new** list of the items, from the lowest hourly rate to the highest |
| `Fleet.priciest()`       | nothing  | Returns the one item with the highest hourly rate                               |

**Requirements:** Tests check both of these.

- `cheapest_first()` calls `sorted()` with `rate_of` as the key.
- `priciest()` calls `max()` with a `lambda` as the key.

```python
# the same fleet as Question 5
by_rate = fleet.cheapest_first()
for item in by_rate:
    print(item.serial)
# H1
# A1
# S1
# E9

priciest = fleet.priciest()
print(priciest.serial)
# E9

for item in fleet.items:   # still in the order the items were added
    print(item.serial)
# A1
# E9
# S1
# H1
```

### Question 7: `costs_less_than`

Staff search the fleet for items under many different hourly rates: under $2.00, under $5.00, under $8.00. `find()` calls its callback with one argument, the item, so the callback cannot also receive the limit.

Write a function called `costs_less_than` that takes a limit and returns a new function. The function it returns answers the question "does this item cost less than the limit an hour?", and it can be passed straight to `find()`.

| Write                    | Takes          | Does                                                                                                       |
| ------------------------ | -------------- | ---------------------------------------------------------------------------------------------------------- |
| `costs_less_than(limit)` | an hourly rate | Returns a function that takes one item and returns `True` when the item's hourly rate is less than `limit` |

```python
# the same fleet as Question 5
under_five = fleet.find(costs_less_than(5.00))
for item in under_five:
    print(item.serial)
# A1
# H1

under_two = fleet.find(costs_less_than(2.00))
for item in under_two:
    print(item.serial)
# H1

under_eight = costs_less_than(8.00)
print(under_eight(Scooter("S1", charge=80, needs_repair=False)))   # True
```

## Modify

Change the code in `src/modify.py`. Its classes are separate from your From Scratch answers, so you can start here before From Scratch is finished.

### Question 8: `late_fee`

Boro Bikes charges a late fee for every hour a bike is returned late. A classic bike's late fee is $1.50 an hour, an electric bike's is $4.50 an hour, and a cargo bike's is $2.50 an hour.

`late_fee(bike, hours)` in `src/modify.py` works out the fee with an `isinstance()` chain. Move each fee onto the class it belongs to, so that `late_fee` calls a method on the bike instead of checking its class.

**Requirements:**

- `Bike`, `ClassicBike`, `ElectricBike` and `CargoBike` each have a `late_fee_per_hour()` method that returns that kind's fee per hour. `Bike`'s returns `0.00`, the value of the chain's `else` branch.
- `late_fee(bike, hours)` has no `isinstance()` and no `type()` in it.

These lines must give the same results before and after your change:

```python
late_fee(ClassicBike("A1", "Grand Army", needs_repair=False), hours=2)                        # Returns 3.0
late_fee(ElectricBike("E9", "Borough Hall", needs_repair=False, battery_range=24), hours=2)   # Returns 9.0
late_fee(CargoBike("C3", "Grand Army", needs_repair=False, crate_litres=90), hours=2)         # Returns 5.0
late_fee(Bike("B0", "Grand Army", needs_repair=False), hours=5)                               # Returns 0.0
```

## Debug

Fix the code in `src/debug.py`.

### Question 9: `charging_list`

A scooter needs charging when its charge is below 20%. `charging_list(scooters)` should return the scooters that need charging. It raises an error instead:

```python
scooters = [
    Scooter("S1", charge=80, needs_repair=False),
    Scooter("S2", charge=10, needs_repair=False),
]
low = charging_list(scooters)
for scooter in low:
    print(scooter.serial)
# Should print S2, but the first line raises:
# TypeError: needs_charging() missing 1 required positional argument: 'scooter'
```

**Requirements:** Fix `charging_list`. Leave `needs_charging` and `scooters_where` as they are, because both are correct.

> Hint: read the message in two parts: which function was called, and what that call left out. Then find the line in `charging_list` where that call happens.

## Submitting

```sh
git add -A
git commit -m "your message"
git push
```

Pushing runs the tests on GitHub. Check the **Actions** tab to see which passed, then open a pull request to your instructor for feedback.

## Good luck!

You got this!
