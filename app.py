from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional
from decimal import Decimal

class ExpenseType(Enum):
    EQUAL = auto()
    EXACT = auto()
    PERCENT = auto()

@dataclass
class User:
    id: str
    name: str
    email: str
    phone: str

@dataclass
class ExpenseMetadata:
    name: str
    img_url: str
    notes: str

@dataclass
class Split(ABC):
    user: User
    amount: Decimal = Decimal('0')

@dataclass
class EqualSplit(Split):
    pass

# @dataclass
class ExactSplit(Split):
    def __init__(self, user: User, amount: Decimal):
        super().__init__(user)
        self.amount = amount

# @dataclass
class PercentSplit(Split):
    percent: Decimal

    def __init__(self, user: User, percent: Decimal):
        super().__init__(user)
        self.percent = percent

@dataclass
class Expense(ABC):
    amount: Decimal
    paid_by: User
    splits: List[Split]
    metadata: Optional[ExpenseMetadata] = None
    id: Optional[str] = None

    @abstractmethod
    def validate(self) -> bool:
        pass

@dataclass
class EqualExpense(Expense):
    def validate(self) -> bool:
        return all(isinstance(split, EqualSplit) for split in self.splits)

@dataclass
class ExactExpense(Expense):
    def validate(self) -> bool:
        if not all(isinstance(split, ExactSplit) for split in self.splits):
            return False
        
        total_amount = sum(split.amount for split in self.splits)
        return abs(total_amount - self.amount) < Decimal('0.01')

@dataclass
class PercentExpense(Expense):
    def validate(self) -> bool:
        if not all(isinstance(split, PercentSplit) for split in self.splits):
            return False
        
        total_percent = sum(split.percent for split in self.splits)
        return abs(total_percent - Decimal('100')) < Decimal('0.01')

class ExpenseService:
    @staticmethod
    def create_expense(expense_type: ExpenseType, amount: Decimal, paid_by: User, 
                      splits: List[Split], metadata: Optional[ExpenseMetadata] = None) -> Optional[Expense]:
        if expense_type == ExpenseType.EXACT:
            expense = ExactExpense(amount, paid_by, splits, metadata)
        
        elif expense_type == ExpenseType.PERCENT:
            for split in splits:
                if isinstance(split, PercentSplit):
                    split.amount = (amount * split.percent) / Decimal('100')
            expense = PercentExpense(amount, paid_by, splits, metadata)
        
        elif expense_type == ExpenseType.EQUAL:
            total_splits = len(splits)
            split_amount = round((amount * Decimal('100')) / total_splits) / Decimal('100')
            
            for split in splits:
                split.amount = split_amount
            
            # Handle rounding errors
            splits[0].amount += amount - (split_amount * total_splits)
            expense = EqualExpense(amount, paid_by, splits, metadata)
        
        else:
            return None
        
        return expense if expense.validate() else None

class ExpenseManager:
    def __init__(self):
        self.expenses: List[Expense] = []
        self.user_map: Dict[str, User] = {}
        self.balance_sheet: Dict[str, Dict[str, Decimal]] = {}

    def add_user(self, user: User) -> None:
        self.user_map[user.id] = user
        self.balance_sheet[user.id] = {}

    def add_expense(self, expense_type: ExpenseType, amount: Decimal, paid_by: str,
                   splits: List[Split], metadata: Optional[ExpenseMetadata] = None) -> None:
        expense = ExpenseService.create_expense(
            expense_type, amount, self.user_map[paid_by], splits, metadata
        )
        if not expense:
            print("Invalid expense")
            return

        self.expenses.append(expense)
        
        for split in expense.splits:
            paid_to = split.user.id
            
            # Update payer's balance sheet
            if paid_to not in self.balance_sheet[paid_by]:
                self.balance_sheet[paid_by][paid_to] = Decimal('0')
            self.balance_sheet[paid_by][paid_to] += split.amount
            
            # Update payee's balance sheet
            if paid_by not in self.balance_sheet[paid_to]:
                self.balance_sheet[paid_to][paid_by] = Decimal('0')
            self.balance_sheet[paid_to][paid_by] -= split.amount

    def show_balance(self, user_id: Optional[str] = None) -> None:
        if user_id:
            balances = self.balance_sheet.get(user_id, {})
            is_empty = True
            for other_user_id, amount in balances.items():
                if amount != 0:
                    is_empty = False
                    self._print_balance(user_id, other_user_id, amount)
            
            if is_empty:
                print("No balances")
        else:
            is_empty = True
            for user_id, balances in self.balance_sheet.items():
                for other_user_id, amount in balances.items():
                    if amount > 0:
                        is_empty = False
                        self._print_balance(user_id, other_user_id, amount)
            
            if is_empty:
                print("No balances")

    def _print_balance(self, user1_id: str, user2_id: str, amount: Decimal) -> None:
        user1_name = self.user_map[user1_id].name
        user2_name = self.user_map[user2_id].name
        
        if amount < 0:
            print(f"{user1_name} owes {user2_name}: {abs(amount):.2f}")
        elif amount > 0:
            print(f"{user2_name} owes {user1_name}: {abs(amount):.2f}")

def main():
    expense_manager = ExpenseManager()
    
    # Add users
    users = [
        User("u1", "User1", "user1@example.com", "9876543210"),
        User("u2", "User2", "user2@example.com", "9876543210"),
        User("u3", "User3", "user3@example.com", "9876543210"),
        User("u4", "User4", "user4@example.com", "9876543210"),
    ]
    
    for user in users:
        expense_manager.add_user(user)

    while True:
        try:
            command = input().strip().split()
            if not command:
                continue

            if command[0] == "SHOW":
                if len(command) == 1:
                    expense_manager.show_balance()
                else:
                    expense_manager.show_balance(command[1])
            
            elif command[0] == "EXPENSE":
                paid_by = command[1]
                amount = Decimal(command[2])
                num_users = int(command[3])
                expense_type = command[4 + num_users]
                
                splits = []
                if expense_type == "EQUAL":
                    splits = [EqualSplit(expense_manager.user_map[command[4 + i]]) 
                            for i in range(num_users)]
                
                elif expense_type == "EXACT":
                    splits = [ExactSplit(expense_manager.user_map[command[4 + i]], 
                             Decimal(command[5 + num_users + i])) 
                             for i in range(num_users)]
                
                elif expense_type == "PERCENT":
                    splits = [PercentSplit(expense_manager.user_map[command[4 + i]], 
                             Decimal(command[5 + num_users + i])) 
                             for i in range(num_users)]
                
                expense_manager.add_expense(ExpenseType[expense_type], amount, paid_by, splits)
            
            else:
                print("Invalid command")

        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()