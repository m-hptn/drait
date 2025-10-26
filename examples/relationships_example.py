"""
Example demonstrating all relationship types in UML class diagrams.

This example shows:
1. Inheritance: Manager inherits from Employee
2. Composition: Car owns Engine (strong ownership)
3. Aggregation: Employee has Department (weak ownership)
4. Dependency: OrderProcessor uses Order and Customer (no storage)
"""

from typing import List, Optional
from datetime import datetime


# ============================================================================
# Example 1: Inheritance Relationship
# ============================================================================

class Employee:
    """Base employee class."""

    def __init__(self, name: str, employee_id: str):
        self.name: str = name
        self.employee_id: str = employee_id
        self.hire_date: datetime = datetime.now()

    def get_info(self) -> str:
        return f"{self.name} ({self.employee_id})"


class Manager(Employee):
    """Manager inherits from Employee (INHERITANCE)."""

    def __init__(self, name: str, employee_id: str, department: str):
        super().__init__(name, employee_id)
        self.department: str = department
        self.team_size: int = 0

    def add_team_member(self) -> None:
        self.team_size += 1


# ============================================================================
# Example 2: Composition Relationship (Strong Ownership)
# ============================================================================

class Engine:
    """Engine that is owned by a Car."""

    def __init__(self, horsepower: int, cylinders: int):
        self.horsepower: int = horsepower
        self.cylinders: int = cylinders

    def start(self) -> None:
        print(f"Engine started: {self.horsepower}hp")


class Car:
    """Car owns an Engine (COMPOSITION)."""

    def __init__(self, model: str, horsepower: int):
        self.model: str = model
        # Engine is created here - strong ownership (composition)
        self.engine: Engine = Engine(horsepower, 4)

    def start_car(self) -> None:
        self.engine.start()


# ============================================================================
# Example 3: Aggregation Relationship (Weak Ownership)
# ============================================================================

class Department:
    """Department that can be shared by multiple employees."""

    def __init__(self, name: str, code: str):
        self.name: str = name
        self.code: str = code
        self.budget: float = 0.0


class Person:
    """Person has a Department (AGGREGATION)."""

    def __init__(self, name: str, department: Optional[Department] = None):
        self.name: str = name
        # Department is passed in - weak ownership (aggregation)
        self.department: Optional[Department] = department
        self.projects: List[str] = []

    def assign_department(self, dept: Department) -> None:
        self.department = dept


# ============================================================================
# Example 4: Dependency Relationship (Uses but doesn't store)
# ============================================================================

class Order:
    """Order class."""

    def __init__(self, order_id: str, total: float):
        self.order_id: str = order_id
        self.total: float = total
        self.status: str = "pending"


class Customer:
    """Customer class."""

    def __init__(self, customer_id: str, name: str):
        self.customer_id: str = customer_id
        self.name: str = name
        self.email: str = ""


class OrderProcessor:
    """OrderProcessor uses Order and Customer but doesn't store them (DEPENDENCY)."""

    def __init__(self):
        self.processed_count: int = 0

    def process_order(self, order: Order, customer: Customer) -> bool:
        """Process order for customer - uses both but doesn't store."""
        print(f"Processing order {order.order_id} for {customer.name}")
        self.processed_count += 1
        return True

    def validate_order(self, order: Order) -> bool:
        """Validate order - uses but doesn't store."""
        return order.total > 0

    def get_customer_info(self) -> Customer:
        """Return customer - uses but doesn't store."""
        return Customer("C001", "John Doe")


# ============================================================================
# Example 5: Multiple Relationships
# ============================================================================

class Address:
    """Address that can be shared."""

    def __init__(self, street: str, city: str):
        self.street: str = street
        self.city: str = city


class Company:
    """
    Company demonstrating multiple relationships:
    - Composition: owns Address (not shared)
    - Aggregation: has Employees (shared)
    """

    def __init__(self, name: str, street: str, city: str):
        self.name: str = name
        # Address is created here - composition
        self.headquarters: Address = Address(street, city)
        # Employees are shared - aggregation
        self.employees: List[Employee] = []

    def hire_employee(self, employee: Employee) -> None:
        """Uses Employee but in aggregation (collection)."""
        self.employees.append(employee)

    def process_payroll(self, processor: OrderProcessor) -> None:
        """Uses OrderProcessor - dependency."""
        print(f"Processing payroll using {processor}")


if __name__ == "__main__":
    print("Relationships Example")
    print("=" * 50)
    print("1. Inheritance: Manager -> Employee")
    print("2. Composition: Car *-- Engine")
    print("3. Aggregation: Person o-- Department")
    print("4. Dependency: OrderProcessor ..> Order, Customer")
    print("5. Multiple: Company *-- Address, Company o-- Employee")
