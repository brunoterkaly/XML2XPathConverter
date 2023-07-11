from lxml import etree


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
        for element in xml:
            if element.tag == "Expression":
                self._parse_expression(element)
            elif element.tag == "SimpleExpression":
                self._parse_simple_expression(element)


    def _parse_simple_expression(self, xml):
        value1 = ""
        operator = ""
        value2 = ""

        for element in xml:
            if element.tag == "ValueExpression":
                if value1 == "":
                    value1 = self._parse_value_expression(element)
                else:
                    value2 = self._parse_value_expression(element)
            elif element.tag == "Operator":
                operator = element.text

        expression = f"{value1} {operator} {value2}"
        self.stack.append(expression)


    def _parse_value_expression(self, xml):
        for element in xml:
            if element.tag == "XPathQuery":
                return element.text
            elif element.tag == "Value":
                return f"'{element.text}'"

    def _build_where_clause(self):
        self.where_clause = "WHERE " + " ".join(self.stack)


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
parsed_result = parser.parse(etree.fromstring(xml))
print(parsed_result)
