"""
Phase 4: Advanced Python Features Example

Demonstrates:
1. Abstract classes and methods (ABC, @abstractmethod)
2. Decorators (@dataclass, @property, custom decorators)
3. Properties (getter/setter/deleter)
4. Static and class methods
5. Protocol classes (typing.Protocol)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol, List, ClassVar
from functools import lru_cache


# ============================================================================
# 1. Abstract Base Classes
# ============================================================================

class Shape(ABC):
    """Abstract base class for shapes."""

    def __init__(self, name: str):
        self.name: str = name

    @abstractmethod
    def area(self) -> float:
        """Calculate area - must be implemented by subclasses."""
        pass

    @abstractmethod
    def perimeter(self) -> float:
        """Calculate perimeter - must be implemented by subclasses."""
        pass

    def describe(self) -> str:
        """Concrete method available to all shapes."""
        return f"{self.name}: area={self.area()}, perimeter={self.perimeter()}"


class Rectangle(Shape):
    """Concrete implementation of Shape."""

    def __init__(self, width: float, height: float):
        super().__init__("Rectangle")
        self.width: float = width
        self.height: float = height

    def area(self) -> float:
        """Implement abstract method."""
        return self.width * self.height

    def perimeter(self) -> float:
        """Implement abstract method."""
        return 2 * (self.width + self.height)


# ============================================================================
# 2. Dataclasses
# ============================================================================

@dataclass
class Point:
    """Simple dataclass for 2D point."""
    x: float
    y: float


@dataclass(frozen=True)
class ImmutablePoint:
    """Frozen (immutable) dataclass."""
    x: float
    y: float


@dataclass
class Person:
    """Dataclass with default values and field metadata."""
    name: str
    age: int
    email: str = ""
    friends: List[str] = field(default_factory=list)
    _internal_id: int = field(default=0, repr=False)


# ============================================================================
# 3. Properties (getter/setter/deleter)
# ============================================================================

class Temperature:
    """Class demonstrating properties."""

    def __init__(self, celsius: float = 0.0):
        self._celsius: float = celsius

    @property
    def celsius(self) -> float:
        """Get temperature in Celsius."""
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        """Set temperature in Celsius."""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """Get temperature in Fahrenheit."""
        return self._celsius * 9/5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        """Set temperature in Fahrenheit."""
        self.celsius = (value - 32) * 5/9


# ============================================================================
# 4. Static and Class Methods with Decorators
# ============================================================================

class MathUtils:
    """Utility class with static and class methods."""

    version: ClassVar[str] = "1.0"

    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    @staticmethod
    @lru_cache(maxsize=128)
    def fibonacci(n: int) -> int:
        """Calculate Fibonacci number with caching."""
        if n < 2:
            return n
        return MathUtils.fibonacci(n-1) + MathUtils.fibonacci(n-2)

    @classmethod
    def get_version(cls) -> str:
        """Get the version of this class."""
        return cls.version


# ============================================================================
# 5. Protocol (Structural Subtyping)
# ============================================================================

class Drawable(Protocol):
    """Protocol for drawable objects."""

    def draw(self) -> str:
        """Draw the object."""
        ...

    def get_color(self) -> str:
        """Get the object's color."""
        ...


# ============================================================================
# 6. Custom Decorators
# ============================================================================

def validate_positive(func):
    """Custom decorator to validate positive numbers."""
    def wrapper(self, value):
        if value <= 0:
            raise ValueError(f"{func.__name__} must be positive")
        return func(self, value)
    return wrapper


class BankAccount:
    """Class with custom decorators."""

    def __init__(self, balance: float = 0.0):
        self._balance: float = balance

    @property
    def balance(self) -> float:
        """Get current balance."""
        return self._balance

    @validate_positive
    def deposit(self, amount: float) -> None:
        """Deposit money (must be positive)."""
        self._balance += amount

    @validate_positive
    def withdraw(self, amount: float) -> None:
        """Withdraw money (must be positive)."""
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount


# ============================================================================
# 7. Mixed Advanced Features
# ============================================================================

@dataclass
class Employee(ABC):
    """Abstract dataclass - combines @dataclass with ABC."""
    name: str
    employee_id: str
    salary: float

    @abstractmethod
    def calculate_bonus(self) -> float:
        """Calculate bonus - must be implemented."""
        pass

    @property
    def annual_salary(self) -> float:
        """Calculate annual salary."""
        return self.salary * 12


@dataclass
class Manager(Employee):
    """Concrete implementation of abstract dataclass."""
    team_size: int = 0

    def calculate_bonus(self) -> float:
        """Implement abstract method."""
        return self.salary * 0.1 * self.team_size


if __name__ == "__main__":
    print("Phase 4: Advanced Features Example")
    print("=" * 50)
    print("1. Abstract classes: Shape (ABC)")
    print("2. Dataclasses: Point, Person (with @dataclass)")
    print("3. Properties: Temperature (celsius/fahrenheit)")
    print("4. Static/Class methods: MathUtils")
    print("5. Protocols: Drawable (Protocol)")
    print("6. Custom decorators: BankAccount (@validate_positive)")
    print("7. Mixed: Employee (ABC + @dataclass)")
