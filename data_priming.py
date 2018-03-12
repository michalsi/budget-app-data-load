import argparse
import logging
import psycopg2
import requests
import json



class DataLoader(object):
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',datefmt='%H:%M:%S', level=logging.INFO)
        self.args = parse_args()
        print_args_info(self.args)

        self.conn = psycopg2.connect("dbname=" + self.args.dbname +
                                     " user=" + self.args.dbuser +
                                     " password=" + self.args.dbpassword)
        self.session = requests.Session()

    def main(self):
        self.setup_app_users(self.args.numberOfUsers)
        self.conn.close()
        logging.info("Script is finished")

    def setup_app_users(self, no_of_users_to_create):
        root_url = self.args.url
        current_id = self.select_max_id_from_table("users")
        headers = {'Content-Type': 'application/json;charset=UTF-8'}

        for _ in xrange(no_of_users_to_create):
            current_id += 1

            user_data = json.dumps({'username':'user'+ str(current_id) +'@test.com','password':'Password1'})
            r = self.session.post(url = root_url + '/api/users', data = user_data, headers = headers)
            print r.text

    def select_max_id_from_table(self, table_name, column="id"):
        cur = self.conn.cursor()
        select_query = "SELECT MAX( " + column + ") FROM " + table_name + " ;"
        # data = (column, )
        cur.execute(select_query)
        max_id = cur.fetchone()[0]
        if max_id is None:
            max_id = 0
        cur.close()
        return max_id

# def main():
#     """business logic for when running this module as the primary one!"""
#
#
#     GenerateCases().setup_app_users(args.numberOfUsers)
#     self.conn.close()
#     logging.info("Script is finished")

def parse_args():
    parser = argparse.ArgumentParser(description="Data Priming for Budget App. Creates users")
    parser.add_argument("-u", "--url", default="localhost:8080", help="Target URL of application")
    parser.add_argument("-d", "--dbname", default="budgetapp", help="Budget App Data Base name")
    parser.add_argument("-s", "--dbuser", default="budgetuser", help="Budget App Data Base user")
    parser.add_argument("-p", "--dbpassword", default="mysecretpassword", help="Budget App Data Base user")

    parser.add_argument("-n", "--numberOfUsers", type=int, default=1, help="Target URL of application")
    return parser.parse_args()

def print_args_info(args):
    logging.info("Script invoked with the following arguments: ")
    for arg in vars(args):
        logging.info("{0}: {1}".format(arg, getattr(args, arg)))

# if __name__ == '__main__':
#     main()

if __name__ == '__main__':
    DataLoader().main()