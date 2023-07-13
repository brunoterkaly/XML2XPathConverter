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

# 1. We start with the root node of the XML tree, push it into the stack and then enter the main loop of the algorithm.
# 2. In each iteration of the loop, we pop an element from the top of the stack. This element is now considered the "current" element.
# 3. If this "current" element is a "SimpleExpression", we process it and add the resulting condition to our list of conditions.
# 4. Regardless of whether the "current" element was a "SimpleExpression" or not, we then push all of its child elements onto the stack. This ensures that in the next iterations of the loop, we'll be processing these child elements. If any of these child elements also have children, they'll be pushed onto the stack when their parent becomes the "current" element. This continues until we've processed all elements in the tree.
# 5. Once all the children of the current node are processed, the loop moves to the next node present in the stack (which may be the sibling of the current node or a node from the upper level or any unprocessed node in the tree). This continues until the stack is empty.



# This function simplifies XML by transforming it into a SQL WHERE clause.
# It's specifically designed to handle XML that represents conditions in an SQL query.
def simplify_xml(xml_string):
    # Parse the XML string into an ElementTree
    root = ET.fromstring(xml_string)
    
    # We're using this list to store the conditions found in the XML
    conditions = []
    
    # Initialize a stack and push the root element onto it
    stack = Stack()
    stack.push(root)

    # Run loop until the stack is empty
    while stack.elements:
        # Remove the topmost element from the stack
        element = stack.pop()

        # If the element is a 'SimpleExpression', extract the condition it represents
        if element.tag == "SimpleExpression":
            # The key of the condition is the text of the 'XPathQuery' sub-element
            key = element.find("ValueExpression/XPathQuery").text
            
            # The operator of the condition is the text of the 'Operator' sub-element
            operator = element.find("ValueExpression/Operator").text
            
            # The value of the condition is the text of the 'Value' sub-element
            value = element.find("ValueExpression/Value").text
            
            # Form the condition and append it to our list of conditions
            conditions.append(f"{key} {operator} '{value}'")

        # Push all of the current element's children onto the stack
        for child in element:
            stack.push(child)

    # Join all the conditions with 'AND' to form a WHERE clause
    where_clause = " AND ".join(conditions)
    
    # Return the resulting WHERE clause
    return where_clause

# Testing the function
if __name__ == "__main__":
    # Define a sample XML string
    xml_string = """
    <xml>
        <Expression>
            <SimpleExpression>
                <ValueExpression>
                    <XPathQuery>color</XPathQuery>
                    <Operator>Equal</Operator>
                    <Value>blue</Value>
                </ValueExpression>
            </SimpleExpression>
        </Expression>
    </xml>
    """
    # Call the simplify_xml function and print the result
    where_clause = simplify_xml(xml_string)
    print(where_clause) # Output: color Equal 'blue'
