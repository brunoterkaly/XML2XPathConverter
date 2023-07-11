import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

class Parser:
    def __init__(self):
        self.stack = []
        self.where_clause = ""

    def parse(self, xml):
        self.stack = []
        self.where_clause = ""
        self._parse_expression(xml)
        self._build_where_clause()
        return self.where_clause

    def _parse_expression(self, xml):
        iterator_stack = [iter(xml)]
        
        while iterator_stack:
            try:
                element = next(iterator_stack[-1])
            except StopIteration:
                iterator_stack.pop()
                continue

            if element.tag == "Expression":
                iterator_stack.append(iter(element))
            elif element.tag == "SimpleExpression":
                self._parse_simple_expression(element)

    def _parse_simple_expression(self, xml):
        expression_stack = []

        for element in xml:
            if element.tag == "ValueExpression":
                value = self._parse_value_expression(element)
                self._push(expression_stack, value)
            elif element.tag == "Operator":
                operator = element.text

        value2 = self._pop(expression_stack)
        value1 = self._pop(expression_stack)

        expression = f"{value1} {operator} {value2}"
        self._push(self.stack, expression)

    def _push(self, stack, value):
        stack.append(value)

    def _pop(self, stack):
        return stack.pop()

    def _parse_value_expression(self, xml):
        for element in xml:
            if element.tag == "XPathQuery":
                return element.text
            elif element.tag == "Value":
                return f"'{element.text}'"

    def _build_where_clause(self):
        if self.stack:
            self.where_clause = "WHERE " + " ".join(self.stack)
        else:
            self.where_clause = "WHERE"

xml = """
<xml>
    <Expression>
        <SimpleExpression>
            <ValueExpression>
                <XPathQuery>color</XPathQuery>
            </ValueExpression>
            <Operator>Equal</Operator>
            <ValueExpression>
                <Value>blue</Value>
            </ValueExpression>
        </SimpleExpression>
    </Expression>
</xml>
"""

parser = Parser()
tree = ET.fromstring(xml)
formatted_xml = minidom.parseString(ET.tostring(tree)).toprettyxml(indent="  ")
formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if line.strip())

print(formatted_xml)
parsed_result = parser.parse(tree)
print(parsed_result)
