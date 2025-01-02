# Splitwise_machine_coding_python

## Overview
An expense sharing application allows users to add their expenses and split them among multiple people. The app maintains balances between people, showing who owes how much to whom.

## Features
- **Add Expenses:** Users can add expenses and split them equally, exactly, or by percentage.
- **View Balances:** The app displays balances for a single user or all users.
- **Precise Calculations:** Supports decimal values up to two decimal places for percentages and amounts.
- **Validation:** Ensures the sum of percentages equals 100 for `PERCENT` splits and the sum of shares equals the total amount for `EXACT` splits.
- **Rounded Splits:** Handles rounding discrepancies when splitting amounts equally.

## User Requirements
Each user has the following attributes:
- **UserId**: Unique identifier
- **Name**: Full name
- **Email**: Email address
- **Mobile Number**: Contact number

## Expense Types
1. **EQUAL:** Splits the expense equally among selected users.
2. **EXACT:** Specifies exact amounts for each user.
3. **PERCENT:** Allocates expense based on specified percentages.

## Functional Requirements
### Expense Input Format
```
EXPENSE <user-id-of-person-who-paid> <amount> <no-of-users> <space-separated-list-of-users> <EQUAL/EXACT/PERCENT> <optional-space-separated-values>
```
### Show Balances Input Format
1. Show all balances:
   ```
   SHOW
   ```
2. Show balances for a specific user:
   ```
   SHOW <user-id>
   ```

### Validation Rules
- **PERCENT:** Total sum of percentages must equal 100.
- **EXACT:** Total sum of specified amounts must equal the total expense amount.

### Output Format
1. **Balances:**
   ```
   <user-id-of-x> owes <user-id-of-y>: <amount>
   ```
2. **No Balances:**
   ```
   No balances
   ```

### Rounding Rules
- Amounts are rounded to two decimal places.
- For equal splits, discrepancies are handled by assigning the largest rounded share to the first user and evenly distributing the remaining amounts.

## Sample Input & Output
### Input:
```
SHOW
SHOW u1
EXPENSE u1 1000 4 u1 u2 u3 u4 EQUAL
SHOW u4
SHOW u1
EXPENSE u1 1250 2 u2 u3 EXACT 370 880
SHOW
EXPENSE u4 1200 4 u1 u2 u3 u4 PERCENT 40 20 20 20
SHOW u1
SHOW
```
### Output:
```
No balances
No balances
User4 owes User1: 250
User2 owes User1: 250
User3 owes User1: 250
User4 owes User1: 250
User2 owes User1: 620
User3 owes User1: 1130
User4 owes User1: 250
User1 owes User4: 230
User2 owes User1: 620
User3 owes User1: 1130
User1 owes User4: 230
User2 owes User1: 620
User2 owes User4: 240
User3 owes User1: 1130
User3 owes User4: 240
```

## Implementation Details
### Classes
1. **User**:
   - Attributes: `userId`, `name`, `email`, `mobile`
2. **Expense**:
   - Attributes: `paidBy`, `amount`, `users`, `type`, `values`
3. **ExpenseSharingApp**:
   - Attributes: `users`, `balances`
   - Methods:
     - `add_user(userId, name, email, mobile)`
     - `add_expense(paidBy, amount, users, type, values)`
     - `show_balances(userId=None)`

### Validations
- **PERCENT Splits:** Ensure percentages sum to 100.
- **EXACT Splits:** Ensure the sum of exact amounts matches the total.

### Balances
- Maintain balances as a dictionary of dictionaries for efficient updates and queries.

## Dependencies
- Python 3.x

## Running the Application
1. Define users in the main method.
2. Parse input for expenses and balance queries.
3. Use appropriate methods to handle inputs and display results.
