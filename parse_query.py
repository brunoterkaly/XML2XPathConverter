import xml.etree.ElementTree as ET
import re

def parse_expression(expression):
    root = ET.fromstring(expression)
    return parse_node(root)

def parse_node(node):
    tree = {
        'tag': node.tag,
        'attrib': node.attrib,
        'text': node.text if node.text else "",  # add this line
        'children': []
    }
    for child in node:
        tree['children'].append(parse_node(child))
    return tree



def generate_value_expression(node):
    value = ""
    for child in node['children']:
        if child['tag'] == 'XPathQuery' or child['tag'] == 'Value':
            value += child['attrib'].get('Type', "") + child.get('text', "")
    return value

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

'''
--------------------------
def process_tree(tree):
--------------------------
In essence, this function performs a depth-first traversal of the XML tree,
collecting expressions and the log name along the way, and then constructs and
prints an XPath expression.

- The function process_tree is defined with tree as a parameter. tree is
expected to be a dictionary representation of the parsed XML tree.

- A list named stack is initialized with the tree as its first element. This
list will be used as a stack data structure, which follows the
Last-In-First-Out (LIFO) principle.

- An empty list expressions and a None variable log_name are initialized.
expressions will store all the simple expressions obtained from the XML tree,
and log_name will store the log name value from the XML tree.

- A helper function push is defined within the scope of process_tree to add a
child element to the stack.

- A while loop begins which will run as long as there are elements in the
stack.

- Inside the while loop, the pop method removes the last element from the stack
and assigns it to the variable current.

- Then there's an if check to see if the 'tag' of the current element is
'LogName'. If it is, it retrieves the 'text' from its first child's first child
and assigns it to log_name.

- Another if check follows to see if the 'tag' of the current element is
'Expression'. If it is, a nested loop iterates over its 'children'. If any
child has a 'tag' of 'SimpleExpression', the generate_where_clause function is
called on it to generate a where clause, which is then appended to the
expressions list.

- After checking and processing 'LogName' and 'Expression' tags, the while loop
iterates over the 'children' of the current node and uses the push function to
add each child to the stack. This way, the while loop will process all nodes in
the tree in a depth-first manner.

- Once the while loop finishes (meaning there are no more elements left in the
stack), there is a check to see if log_name is not None. If it's not, it
constructs an XPath expression using log_name and all the expressions collected
in the expressions list, and prints it.

'''

def process_tree(tree):
    stack = [tree]
    expressions = []
    log_name = None

    def push(child):
        stack.append(child)

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
    
    while stack:
        current = stack.pop()
        if current['tag'] == 'LogName':
            log_name = current['children'][0]['children'][0]['text']
        if current['tag'] == 'Expression':
            for child in current['children']:
                if child['tag'] == 'SimpleExpression':
                    where_clause = generate_where_clause(child)
                    expressions.append(where_clause)
                elif child['tag'] == 'RegExExpression':
                    regex_clause = generate_regex_clause(child)
                    expressions.append(regex_clause)
        for child in current['children']:
            push(child)

    if log_name is not None:
        xpath_expression = f"{log_name}!*[{log_name}[{ ' and '.join(expressions) }]]"
        print(xpath_expression)


def generate_where_clause(expression):
    value_expression_1 = get_dictionary_lookup( expression['children'][0]['children'][0]['text'])
    operator = get_dictionary_lookup(expression['children'][1]['text'])
    value_expression_2 = get_dictionary_lookup(expression['children'][2]['children'][0]['text'])

    if need_quotes(value_expression_1):
        value_expression_2 = fr"\'{value_expression_2}\'"

    where_clause = f"({value_expression_1}{operator}{value_expression_2})"
    return where_clause

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

def need_quotes(parameter):
    dictionary = {
        'Provider[@Name': True,
        'EventID': False
    }

    if parameter in dictionary:
        return dictionary[parameter]
    else:
        return False


expression = '''
<Workload>
    <LogName>
        <ValueExpression>
            <Value Type="String">Application</Value>
        </ValueExpression>
    </LogName>
    <Expression>
        <SimpleExpression>
            <ValueExpression>
                <XPathQuery Type="String">PublisherName</XPathQuery>
            </ValueExpression>
            <Operator>Equal</Operator>
            <ValueExpression>
                <Value Type="String">Microsoft-Windows-IIS-W3SVC-WP</Value>
            </ValueExpression>
        </SimpleExpression>
    </Expression>
    <Expression>
        <SimpleExpression>
            <ValueExpression>
                <XPathQuery>EventDisplayNumber</XPathQuery>
            </ValueExpression>
            <Operator>Equal</Operator>
            <ValueExpression>
                <Value>2216</Value>
            </ValueExpression>
        </SimpleExpression>
    </Expression>
</Workload>
'''

expression2 = '''
<Workload>
    <LogName>
        <ValueExpression>
            <Value Type="String">System</Value>
        </ValueExpression>
    </LogName>
	<Expression>
		<SimpleExpression>
			<ValueExpression>
				<XPathQuery>EventDisplayNumber</XPathQuery>
			</ValueExpression>
			<Operator>Equal</Operator>
			<ValueExpression>
				<Value>5152</Value>
			</ValueExpression>
		</SimpleExpression>
	</Expression>
	<Expression>
		<SimpleExpression>
			<ValueExpression>
				<XPathQuery Type="String">PublisherName</XPathQuery>
			</ValueExpression>
			<Operator>Equal</Operator>
			<ValueExpression>
				<Value Type="String">Microsoft-Windows-WAS</Value>
			</ValueExpression>
		</SimpleExpression>
	</Expression>
</Workload>
'''

expression3 = '''
<Workload>
    <LogName>
        <ValueExpression>
            <Value Type="String">System</Value>
        </ValueExpression>
    </LogName>
	<Expression>
		<RegExExpression>
			<ValueExpression>
				<XPathQuery>EventDisplayNumber</XPathQuery>
			</ValueExpression>
			<Operator>MatchesRegularExpression</Operator>
			<Pattern>^(5010|5011|5012|5013)$</Pattern>
		</RegExExpression>
	</Expression>
	<Expression>
		<SimpleExpression>
			<ValueExpression>
				<XPathQuery Type="String">PublisherName</XPathQuery>
			</ValueExpression>
			<Operator>Equal</Operator>
			<ValueExpression>
				<Value Type="String">Microsoft-Windows-WAS</Value>
			</ValueExpression>
		</SimpleExpression>
	</Expression>
</Workload>
'''

'''
System!*[System[(Provider[@Name=\'Microsoft-Windows-WAS\') and (EventID=5010 or EventID=5011 or EventID=5012 or EventID=5013)]]
'''

tree = parse_expression(expression)
process_tree(tree)
