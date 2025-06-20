import itertools

import psycopg2 as pg

conn_params = {
    'dbname': 'project_v3',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}


class AssociationRules:
    """
    Association rules implementation using the Apriori algorithm.
    """
    def __init__(self, transactions, min_support, min_confidence, db_connection):
        self.conn = db_connection
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.rules = []
        self.item_support_dict = {}
        self.item_count_dict = self.get_item_count()
        self.l2 = self.get_itemsets(2)
        self.l3 = self.get_itemsets(3)
        self.l4 = self.get_itemsets(4)

    def get_item_count(self):
        cursor = self.conn.cursor()

        cursor.execute('select item, count(*) from items group by item')
        rows = cursor.fetchall()

        item_count_dict = {}
        for row in rows:
            item_count_dict[row[0]] = row[1]

        return item_count_dict

    def get_all_transactions(self):
        cursor = self.conn.cursor()

        cursor.execute('select * from items')
        rows = cursor.fetchall()

        return rows

    def calculate_support(self, items_list):
        """
        Calculate the support for a list of items
        :param items_list: list of items
        :return: support values
        """

        support = 0
        num_of_items = len(items_list.split(","))

        if num_of_items == 1:
            support = self.item_count_dict.get(items_list) / self.transactions
        elif num_of_items == 2:
            support = self.l2[items_list] / self.transactions
        elif num_of_items == 3:
            support = self.l3[items_list] / self.transactions
        elif num_of_items == 4:
            support = self.l4[items_list] / self.transactions

        return support

    def calculate_confidence(self, rule):
        """
        Calculate the confidence for a rule
        :param rule: string in X->Y format
        :return: confidence value
        """
        x, y = rule.split("->")
        x_items = x.split(",")
        y_items = y.split(",")
        xy_items = x_items + y_items

        x_str = ",".join(sorted(x_items))
        xy_str = ",".join(sorted(xy_items))

        support_x = self.item_support_dict.get(x_str)
        support_xy = self.item_support_dict.get(xy_str)

        if support_x is None:
            support_x = self.calculate_support(x_str)
        if support_xy is None:
            support_xy = self.calculate_support(xy_str)

        # Calculate confidence
        confidence = support_xy / support_x if support_x > 0 else 0

        return confidence, support_xy

    def get_itemsets(self, level):
        """
        Get the itemsets for a given level
        :param level: level of the itemset
        :return: itemsets, list of lists
        """
        cursor = self.conn.cursor()

        cursor.execute(f'select * from L{level}')
        rows = cursor.fetchall()

        rows = {",".join(row[:-1]): row[-1] for row in rows}

        return rows

    def get_rules(self, level=2):
        """
        Generate association rules based on frequent itemsets
        :param level: level of itemsets to generate rules from
        :return: list of association rules
        """
        rules = []

        cursor = self.conn.cursor()

        cursor.execute(f'select * from L{level}')
        rows = cursor.fetchall()

        # Get itemsets for the specified level
        for row in rows:
            itemset = row[:-1]

            # Generate all possible rules from this itemset
            for rule_size in range(1, len(itemset)):
                # Generate all possible combinations of antecedents
                for antecedent in itertools.combinations(itemset, rule_size):
                    # The consequent is the remaining items
                    consequent = [item for item in itemset if item not in antecedent]

                    # Create rule strings
                    antecedent_str = ",".join(sorted(antecedent))
                    consequent_str = ",".join(sorted(consequent))
                    rule = f"{antecedent_str}->{consequent_str}"

                    # Calculate confidence
                    confidence, support = self.calculate_confidence(rule)

                    rule = f"[{antecedent_str}] -> [{consequent_str}]"

                    # Check if rule meets minimum confidence and minimum support threshold
                    if confidence >= self.min_confidence and support >= self.min_support:
                        rules.append(rule)

        self.rules.extend(rules)

    def print_rules(self, level):
        """
        Print the association rules to a file
        :param level: level of itemsets to generate rules from
        :return: None
        """
        self.get_rules(level)

        with open(f'rules_{level}.txt', 'w') as f:
            for rule in self.rules:
                f.write(f"{rule}\n")

def main():
    with pg.connect(**conn_params) as conn:
        cursor = conn.cursor()
        cursor.execute(f'select count(*) from items')
        transactions = cursor.fetchone()[0]

        min_conf = {
            2: 0.8,
            3: 0.8,
            4: 0.9
        }

        min_sup = {
            2: 0.08,
            3: 0.08,
            4: 0.085
        }

        for i in range(2, 5):
            ar = AssociationRules(transactions, min_sup[i], min_conf[i], conn)
            ar.print_rules(i)

if __name__ == '__main__':
    main()

