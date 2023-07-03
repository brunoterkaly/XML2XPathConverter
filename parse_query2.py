# Import necessary libraries
import xml.etree.ElementTree as ET
import re
import os


# Parse XML string and return a dictionary representing the XML structure
def parse_expression(expression):
    root = ET.fromstring(expression)
    return parse_node(root)


# Recursively traverse XML node tree and build a dictionary
def parse_node(node):
    tree = {
        'tag': node.tag,
        'attrib': node.attrib,
        'text': node.text if node.text else "",  # Add empty string if node.text is None
        'children': []
    }
    for child in node:
        tree['children'].append(parse_node(child))  # Recursive call for each child
    return tree


# Generate value expression from a node in the tree
def generate_value_expression(node):
    value = ""
    for child in node['children']:
        # Concatenate Type and text if the tag is either 'XPathQuery' or 'Value'
        if child['tag'] == 'XPathQuery' or child['tag'] == 'Value':
            value += child['attrib'].get('Type', "") + child.get('text', "")
    return value


# Generate simple expression using the operator and the values
def generate_simple_expression(node):
    value_expressions = []
    operator = ""

    for child in node['children']:
        if child['tag'] == 'ValueExpression':
            value_expressions.append(generate_value_expression(child))
        elif child['tag'] == 'Operator':
            # Check if 'text' attribute exists before accessing it
            operator = child.get('text', "")
            operator = get_dictionary_lookup(operator)

    result = [operator]
    result.extend(value_expressions)
    return result


# Traverse the XML tree and process each 'Workload' tag
def process_trees(root, file):
    for workload in root['children']:
        if workload['tag'] == 'Workload':
            process_tree(workload, file)


# Perform depth-first traversal of the XML tree and generate XPath expressions
def process_tree(tree, file):
    stack = [tree]
    expressions = []
    log_name = None

    # Helper function to add child element to the stack
    def push(child):
        stack.append(child)

    # Generate regex clause from the node in the tree
    def generate_regex_clause(node):
        xpath_query = node['children'][0]['children'][0]['text']
        # Lookup in dictionary
        xpath_expression = get_dictionary_lookup(xpath_query)
        pattern = node['children'][2]['text']

        # Extract the IDs from the pattern using a regular expression
        id_list = re.findall(r'\b\d+\b', pattern)

        # Generate the clause
        clause = " or ".join([f"{xpath_expression}={id}" for id in id_list])

        return "(" + clause + ")"

    # Begin traversing the tree
    while stack:
        current = stack.pop()
        # Get log name
        if current['tag'] == 'LogName':
            log_name = current['children'][0]['children'][0]['text']
        # Generate expressions
        if current['tag'] == 'Expression':
            for child in current['children']:
                if child['tag'] == 'SimpleExpression':
                    where_clause = generate_where_clause(child)
                    expressions.append(where_clause)
                elif child['tag'] == 'RegExExpression':
                    regex_clause = generate_regex_clause(child)
                    expressions.append(regex_clause)
        # Traverse children of current node
        for child in current['children']:
            push(child)

    # Construct XPath expression if log_name is defined
    if log_name is not None:
        expanded = ' and '.join(expressions)
        xpath_expression = log_name + "!*" + "[" + log_name + "[" + expanded + "]]"
        print(xpath_expression)
        file.write(xpath_expression + "\r\n")


# Generate WHERE clause for the expression
def generate_where_clause(expression):
    value_expression_1 = get_dictionary_lookup(expression['children'][0]['children'][0]['text'])
    operator = get_dictionary_lookup(expression['children'][1]['text'])
    value_expression_2 = get_dictionary_lookup(expression['children'][2]['children'][0]['text'])

    if need_quotes(value_expression_1):
        value_expression_2 = fr"\'{value_expression_2}]\'"

    where_clause = f"({value_expression_1}{operator}{value_expression_2})"
    return where_clause


# Return corresponding value from the dictionary. If not found, return the parameter as is
def get_dictionary_lookup(parameter):
    dictionary = {
        'Equal': '=',
        'PublisherName': 'Provider[@Name',
        'EventDisplayNumber': 'EventID'
    }

    if parameter in dictionary:
        return dictionary[parameter]
    else:
        return parameter


# Check if parameter needs to be enclosed in quotes
def need_quotes(parameter):
    dictionary = {
        'Provider[@Name': True,
        'EventID': False
    }

    if parameter in dictionary:
        return dictionary[parameter]
    else:
        return False

def main():
    # Open and read XML file
    with open("./allqueriesxml.xml", "r") as file:
        content = file.read()

    # Output file path
    file_path = './output.txt'

    # If output file already exists, delete it
    if os.path.exists(file_path):
        os.remove(file_path)

    # Parse XML content and generate dictionary tree
    tree = parse_expression(content)

    # Write XPath expressions to output file
    with open(file_path, "a") as file:
        process_trees(tree, file)

# Call the main function
if __name__ == "__main__":
    main()