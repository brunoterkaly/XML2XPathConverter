# Import necessary libraries
import xml.etree.ElementTree as ET
import re
import os


# Parse XML string and return a dictionary representing the XML structure
def parse_expression(expression):
    root = ET.fromstring(expression)
    return parse_node(root)


# Recursively traverse XML node tree and build a dictionary
def parse_node(root):
    # Initialize the root dictionary
    root_dict = {
        'tag': root.tag,
        'attrib': root.attrib,
        'text': root.text if root.text else "",
        'children': []
    }

    # Initialize the stack with the root node and its dictionary
    stack = [(root, root_dict)]

    while stack:
        node, node_dict = stack.pop()

        # Iterate over all child nodes
        for child in node:
            # Create a new dictionary for each child
            child_dict = {
                'tag': child.tag,
                'attrib': child.attrib,
                'text': child.text if child.text else "",
                'children': []
            }

            # Append the dictionary to the children of the current node
            node_dict['children'].append(child_dict)

            # Push the child node and its dictionary to the stack
            stack.append((child, child_dict))

    # Return the dictionary of the root node
    return root_dict



# Generate value expression from a node in the tree
def generate_value_expression(node):
    value = ""
    for child in node['children']:
        # Concatenate Type and text if the tag is either 'XPathQuery' or 'Value'
        if child['tag'] == 'XPathQuery' or child['tag'] == 'Value':
            value += child['attrib'].get('Type', "") + child.get('text', "")
    return value



# Traverse the XML tree and process each 'Workload' tag
def process_trees(root, file):
    for workload in root['children']:
        if workload['tag'] == 'Workload':
            process_tree(workload, file)

def generate_simple_expression(node):
    value_expressions = []
    operator = ""

    for child in node['children']:
        if child['tag'] == 'ValueExpression':
            value_expressions.append(generate_value_expression(child))
        elif child['tag'] == 'Operator':
            operator = child.get('text', "")
            operator = get_dictionary_lookup(operator)

    result = [operator]
    result.extend(value_expressions)
    return ' '.join(result)


def generate_where_clause(node):
    return ' '.join(generate_simple_expression(node))


def process_tree(tree, file):
    stack = [tree]
    expressions = []
    log_name = None

    # Helper function to add child element to the stack
    def push(child):
        stack.append(child)

    # Begin traversing the tree
    while stack:
        current = stack.pop()
        #----------------------------------------------
        # We only care about LogName and Expression at top level
        #----------------------------------------------
        # Get log name
        if current['tag'] == 'LogName':
            log_name = generate_value_expression(current['children'][0])
        
        # We found Expression, so loop through children
        
        elif current['tag'] == 'Expression':
            for child in current['children']:
                if child['tag'] == 'SimpleExpression':
                    where_clause = generate_where_clause(child)
                    expressions.append(where_clause)
                elif child['tag'] == 'Or':
                    # If we encounter an Or tag, we join the expressions by 'or' instead of 'and'
                    or_expressions = []
                    for nested_child in child['children']:
                        or_clause = generate_where_clause(nested_child)
                        or_expressions.append(or_clause)
                    expressions.append("(" + " or ".join(or_expressions) + ")")

        # Traverse children of current node
        for child in current['children']:
            push(child)

    # Construct XPath expression if log_name is defined
    if log_name is not None:
        expanded = ' and '.join(expressions)
        xpath_expression = f"{log_name}!*[{log_name}[{expanded}]]"
        print(xpath_expression)
        file.write(xpath_expression + "\r\n")



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
    with open("./allqueriesxml_complex.xml", "r") as file:
        content = file.read()

    # Output file path
    file_path = './output2.txt'

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