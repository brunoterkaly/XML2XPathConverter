import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import itertools


class CopiableIterator:
    def __init__(self, iterable):
        self.it = iter(iterable)
        self.cache = []
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.cache) > self.index:
            item = self.cache[self.index]
        else:
            item = next(self.it)
            self.cache.append(item)
        self.index += 1
        return item

    def copy(self):
        new_it = CopiableIterator(itertools.chain(self.cache, self.it))
        new_it.index = self.index
        return new_it


class Parser:
    def __init__(self):
        self.stack = []
        self.where_clause = ""

    def parse(self, xml):
        self.stack = []
        self.where_clause = ""
        self._parse_expression(CopiableIterator(xml))
        self._build_where_clause()
        return self.where_clause

    def _parse_expression(self, xml):
        iterator_stack = [xml]

        while iterator_stack:
            try:
                element = next(iterator_stack[-1])
            except StopIteration:
                self.pop(iterator_stack)
                continue

            if element.tag == "Expression":
                self.push(iterator_stack, CopiableIterator(element))
            elif element.tag == "SimpleExpression":
                self._parse_simple_expression(element)

    def _parse_simple_expression(self, xml):
        expression_stack = []

        for element in xml:
            if element.tag == "ValueExpression":
                value = self._parse_value_expression(element)
                self.push(expression_stack, value)
            elif element.tag == "Operator":
                operator = element.text

        value2 = self.pop(expression_stack)
        value1 = self.pop(expression_stack)

        expression = f"{value1} {operator} {value2}"
        self.push(self.stack, expression)

    def push(self, stack, value):
        copied_it = value.copy() if isinstance(value, CopiableIterator) else value
        print(
            f"Stack before push: {[list(x.copy()) if isinstance(x, CopiableIterator) else x for x in stack]}"
        )
        stack.append(value)
        print(
            f"Stack after push: {[list(x.copy()) if isinstance(x, CopiableIterator) else x for x in stack]}"
        )

    def pop(self, stack):
        print(
            f"Stack before pop: {[list(x.copy()) if isinstance(x, CopiableIterator) else x for x in stack]}"
        )
        value = stack.pop()
        print(
            f"Stack after pop: {[list(x.copy()) if isinstance(x, CopiableIterator) else x for x in stack]}"
        )
        return value

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
formatted_xml = "\n".join(line for line in formatted_xml.split("\n") if line.strip())

print(formatted_xml)
parsed_result = parser.parse(tree)
print(parsed_result)
