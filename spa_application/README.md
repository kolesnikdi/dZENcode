Description in English and Ukrainian
# LoanCalculator
Create loan agreements with an annuity payment schedule. Review agreements and payment schedules.
Change the body of any payment with subsequent recalculation of the entire payment schedule. Saving the history of all
payments.
## Project launch 
docker-compose up --build

## Endpoints
### http://127.0.0.1:8000/loan/ --> Creating a new Loan with payments to it.
#### loan_amount = from 0,01 to 99999999,99.
#### loan_start_date = format 2023-07-10.
#### periodicity_amount = from 1 to 365.
#### periodicity = 1 - day, 2 - week, 3 - month.
#### number_of_payments =  from 1 to 365.
#### interest_rate = % from 0,01 to 99.
### http://127.0.0.1:8000/loan/<uuid4:contract>/ --> Revision of the loan agreement and payment schedule.
### http://127.0.0.1:8000/loan/payment/<int:id>/ --> Change the payment body and recreate the payment schedule.
#### subtract_sum =  to the value of the current payment body.

## Test by Pytest

# LoanCalculator
Створення кредитних договорів з ануїтетним графіком погашення. Перегляд договорів та графіків платежів.
Зміна тіла будь-якого платежу з подальшим перерахунком всього графіку платежів. Збереження історії всіх платежів.
## Запуск проекту 
docker-compose up --build

#### Test by Pytest
pytest

## Endpoints
### http://127.0.0.1:8000/loan/ --> Створення нового Кредиту з платежами до нього.
#### loan_amount = від 0,01 до 99999999,99.
#### loan_start_date = формат 2023-07-10.
#### periodicity_amount = від 1 до 365.
#### periodicity = 1 - день, 2 - тиждень, 3 - місяць.
#### number_of_payments =  від 1 до 365.
#### interest_rate = % від 0,01 до 99.
### http://127.0.0.1:8000/loan/<uuid4:contract>/ --> Перегляд кредитного договору та графіку платежів.
### http://127.0.0.1:8000/loan/payment/<int:id>/ --> Зміна тіла платежу та перествореня графіку платежів.
#### subtract_sum =  від 0,01 до значення тіла поточного платежу.
