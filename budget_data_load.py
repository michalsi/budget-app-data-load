import psycopg2
import names
from datetime import datetime
import logging

# TODO: setup DB user first ?

class BudgetDataLoad(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
        self.no_of_users_to_create = 2
        self.conn = psycopg2.connect("dbname=budgetapp user=budgetuser")

    def main(self):
        self.setup_app_users(self.no_of_users_to_create)
        self.conn.close()
        logging.info("Script is finished")

    def setup_app_users(self, no_of_users_to_create):
        current_id = self.select_max_id_from_table("users")
        for _ in xrange(no_of_users_to_create):
            current_id += 1
            self.insert_new_user_with_id(current_id)
            self.insert_budget_types(current_id)
            self.insert_categories_for_user(current_id)
            self.insert_budgets_for_user(current_id)

    def select_max_id_from_table(self, table_name, column="id"):
        cur = self.conn.cursor()
        select_query = "SELECT MAX( " +column+ ") FROM "+table_name +" ;"
        # data = (column, )
        cur.execute(select_query)
        max_id = cur.fetchone()[0]
        if max_id is None:
            max_id = 0
        cur.close()
        return max_id

    def insert_new_user_with_id(self, user_id):
        USER_PASSWORD = '79140b5312f64f7ccc7a3cdea8d2981be3925116598d14b0e997ef40e04bd609ff22248d1f273151'  # Password1
        currency = 'EUR'
        username = 'user' + str(user_id) + '@test.com'

        cur = self.conn.cursor()
        cur.execute("""
                    INSERT INTO users (id, username,password,name,created_at,currency)
                    VALUES (%s, %s, %s,%s, %s, %s);
                    """,
                    (user_id,
                     username,
                     USER_PASSWORD,
                     names.get_full_name(),
                     self.get_timestamp(),
                     currency))
        self.conn.commit()
        cur.close()
        logging.info('User: ' + str(username) + ' inserted into USERS table')

    # TODO: check if that is not automatically created when creating budgets for the first time
    def insert_budget_types(self, user):
        BUDGET_TYPES_PER_USER = 65
        max_id = self.select_max_id_from_table("budget_types")
        for _ in xrange(BUDGET_TYPES_PER_USER):
            max_id += 1
            self.insert_new_budget_type_with_id(max_id)
        logging.info('Budget types created for user Id : ' + str(user))

    def insert_new_budget_type_with_id(self, id):
        cur = self.conn.cursor()
        cur.execute("""
                    INSERT INTO budget_types (id, created_at)
                    VALUES (%s, %s);
                    """,
                    (id,
                     self.get_timestamp()))
        self.conn.commit()
        cur.close()

    def insert_categories_for_user(self, user_id):
        categories = ["Income", "Home", "Transportation", "Health", "Charity/Gifts", "Daily Living", "Entertainment",
                      "Savings", "Obligations", "Miscellaneous"]

        for category in categories:
            self.insert_category_type_for_user(category, user_id)
        logging.info("Categories inserted for user: " + str(user_id))


    def insert_category_type_for_user(self, category, user_id):
        type = "INCOME" if category == "Income" else "EXPENDITURE"
        cur = self.conn.cursor()
        cur.execute("""
                    INSERT INTO categories (name,type,created_at,user_id)
                    VALUES (%s, %s,%s, %s);
                    """,
                    (category, type, self.get_timestamp(), user_id))
        self.conn.commit()
        cur.close()

    def insert_budgets_for_user(self, user_id):
        names = {"Wages & Tips": 1, "Interest Income": 1, "Dividends": 1, "Gifts Received": 1,
                 "Refunds/Reimbursements": 1, "Transfer From Savings": 1, "Mortgage/Rent": 2,
                 "Home/Rental Insurance": 2, "Electricity": 2, "Gas/Oil": 2, "Water/Sewer/Trash": 2, "Phone": 2,
                 "Cable/Satellite": 2, "Internet": 2, "Furnishings/Appliances": 2, "Maintenance/Supplies": 2,
                 "Vehicle Payments": 3, "Auto Insurance": 3, "Fuel": 3, "Bus/Taxi/Train Fare": 3, "Repairs": 3,
                 "Registration/License": 3, "Health Insurance": 4, "Doctor/Dentist": 4, "Medicine/Drugs": 4,
                 "Health Club Dues": 4, "Life Insurance": 4, "Veterinarian/Pet Care": 4, "Gifts Given": 5,
                 "Charitable Donations": 5, "Religious Donations": 5, "Groceries": 6, "Personal Supplies": 6,
                 "Clothing": 6, "Cleaning": 6, "Education/Lessons": 6, "Dining/Eating Out": 6, "Salon/Barber": 6,
                 "Pet Food": 6, "Videos/DVDs": 7, "Music": 7, "Games": 7, "Rentals": 7, "Movies/Theater": 7,
                 "Concerts/Plays": 7, "Books": 7, "Hobbies": 7, "Film/Photos": 7, "Sports": 7, "Outdoor Recreation": 7,
                 "Toys/Gadgets": 7, "Vacation/Travel": 7, "Emergency Fund": 8, "Transfer to Savings": 8,
                 "Retirement (401k  IRA)": 8, "Investments": 8, "Education": 8, "Student Loan": 9, "Other Loan": 9,
                 "Credit Cards": 9, "Alimony/Child Care": 9, "Federal Taxes": 9, "State/Local Taxes": 9,
                 "Bank Fees": 10, "Postage": 10}
        current_type_id = self.select_max_id_from_table("budgets", "type_id")
        for budget, category_id in names.items():
            current_type_id += 1
            self.insert_budget_for_user(budget, category_id, user_id, current_type_id)
        logging.info("Budgets inserted for user: " + str(user_id))

    def insert_budget_for_user(self, budget, category_id, user_id, type_id):
        projected_amount = 0
        actual_amount = 0
        period = datetime.utcnow().replace(day=1).strftime('%Y-%m-%d')
        cur = self.conn.cursor()

        cur.execute("""
                        INSERT INTO budgets (name,projected,actual,period_on,created_at,user_id,category_id,type_id)
                        VALUES (%s, %s,%s, %s,%s,%s,%s,%s);
                        """,
                    (budget, projected_amount, actual_amount, period, self.get_timestamp(), user_id, category_id,
                     type_id ))
        self.conn.commit()
        cur.close()

    @staticmethod
    def get_timestamp():
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')


if __name__ == '__main__':
    BudgetDataLoad().main()