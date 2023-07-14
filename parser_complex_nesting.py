# Implementing Stack Data Structure
class Stack:
    # Initializing the stack as an empty list
    def __init__(self):
        self.elements = []

    # Method to add an element to the stack
    def push(self, element):
        self.elements.append(element)

    # Method to remove the topmost element from the stack
    def pop(self):
        return self.elements.pop()

# Importing ElementTree for XML parsing
import xml.etree.ElementTree as ET

# This function simplifies XML by transforming it into a SQL WHERE clause.
def simplify_xml(xml_string):
    root = ET.fromstring(xml_string)
    
    conditions = []
    logical_operators = []
    
    stack = Stack()
    stack.push(root)

    while stack.elements:
        element = stack.pop()

        if element.tag == "SimpleExpression":
            key = element.find("ValueExpression/XPathQuery").text
            operator = element.find("ValueExpression/Operator").text
            value = element.find("ValueExpression/Value").text
            
            conditions.append(f"{key} {operator} '{value}'")

        if element.tag == "Or":
            logical_operators.append("OR")
        elif element.tag == "And":
            logical_operators.append("AND")

        for child in element:
            stack.push(child)

    where_clause = " "
    for i in range(len(conditions)):
        if i < len(logical_operators):
            where_clause += conditions[i] + " " + logical_operators[i] + " "
        else:
            where_clause += conditions[i]
    
    return where_clause.strip()

# Testing the function
if __name__ == "__main__":
    xml_string = """
    <xml>
        <And>
        <Expression>
            <SimpleExpression>
                <ValueExpression>
                    <XPathQuery>color</XPathQuery>
                    <Operator>Equal</Operator>
                    <Value>blue</Value>
                </ValueExpression>
            </SimpleExpression>
        </Expression>
        <Expression>
            <SimpleExpression>
                <ValueExpression>
                    <XPathQuery>color</XPathQuery>
                    <Operator>Equal</Operator>
                    <Value>Green</Value>
                </ValueExpression>
            </SimpleExpression>
        </Expression>
        </And>
    </xml>
    """
    xml_string2 = """
    <xml>
        <Or>
            <Expression>
                <SimpleExpression>
                    <ValueExpression>
                        <XPathQuery>color</XPathQuery>
                        <Operator>Equal</Operator>
                        <Value>blue</Value>
                    </ValueExpression>
                </SimpleExpression>
            </Expression>
            <And>
                <Expression>
                    <SimpleExpression>
                        <ValueExpression>
                            <XPathQuery>color</XPathQuery>
                            <Operator>Equal</Operator>
                            <Value>blue</Value>
                        </ValueExpression>
                    </SimpleExpression>
                </Expression>
                <Expression>
                    <SimpleExpression>
                        <ValueExpression>
                            <XPathQuery>color</XPathQuery>
                            <Operator>Equal</Operator>
                            <Value>Green</Value>
                        </ValueExpression>
                    </SimpleExpression>
                </Expression>
            </And>
        </Or>
    </xml>

    """
    where_clause = simplify_xml(xml_string2)
    print(where_clause) # Output: color Equal 'blue' OR color Equal 'Green'
