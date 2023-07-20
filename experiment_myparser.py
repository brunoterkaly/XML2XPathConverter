import xml.etree.ElementTree as ET

class Parser:
    def __init__(self, text):
        self.root = ET.fromstring(text)

    def parse(self):
        return self.parse_queries(self.root)

    def parse_queries(self, node):
        queries = {}
        for child in node:
            if child.tag == 'Workload':
                queries['Workload'] = self.parse_workload(child)
        return queries

    def parse_workload(self, node):
        workload = {}
        for child in node:
            if child.tag == 'LogName':
                workload['LogName'] = self.parse_logname(child)
            elif child.tag == 'Expression':
                workload['Expression'] = self.parse_expression(child)
        return workload

    def parse_logname(self, node):
        logname = {}
        for child in node:
            if child.tag == 'ValueExpression':
                logname['ValueExpression'] = self.parse_value_expression(child)
        return logname

    def parse_expression(self, node):
        expression = {}
        for child in node:
            if child.tag == 'And':
                expression['And'] = self.parse_and(child)
            elif child.tag == 'Or':
                expression['Or'] = self.parse_or(child)
            elif child.tag == 'SimpleExpression':
                expression['SimpleExpression'] = self.parse_simple_expression(child)
        return expression

    def parse_and(self, node):
        and_expr = []
        for child in node:
            if child.tag == 'Expression':
                and_expr.append(self.parse_expression(child))
            elif child.tag == 'Or':
                and_expr.append({'Or': self.parse_or(child)})
        return and_expr

    def parse_or(self, node):
        or_expr = []
        for child in node:
            if child.tag == 'Expression':
                or_expr.append(self.parse_expression(child))
        return or_expr

    def parse_simple_expression(self, node):
        simple_expression = {}
        for child in node:
            if child.tag == 'ValueExpression':
                simple_expression['ValueExpression'] = self.parse_value_expression(child)
            elif child.tag == 'Operator':
                simple_expression['Operator'] = child.text
        return simple_expression

    def parse_value_expression(self, node):
        value_expression = {}
        for child in node:
            if child.tag == 'XPathQuery':
                value_expression['XPathQuery'] = {'Type': child.attrib['Type'], 'Value': child.text}
            elif child.tag == 'Value':
                value_expression['Value'] = {'Type': child.attrib['Type'], 'Value': child.text}
        return value_expression



xml_input = """
<Queries>
	<Workload>
		<LogName>
			<ValueExpression>
				<Value Type="String">Application</Value>
			</ValueExpression>
		</LogName>
		<Expression>
			<And>
				<Or>
					<Expression>
						<SimpleExpression>
							<ValueExpression>
								<XPathQuery Type="Boolean">color</XPathQuery>
							</ValueExpression>
							<Operator>Equal</Operator>
							<ValueExpression>
								<Value Type="Boolean">blue</Value>
							</ValueExpression>
						</SimpleExpression>
					</Expression>
					<Expression>
						<SimpleExpression>
							<ValueExpression>
								<XPathQuery Type="Boolean">size</XPathQuery>
							</ValueExpression>
							<Operator>Equal</Operator>
							<ValueExpression>
								<Value Type="Boolean">large</Value>
							</ValueExpression>
						</SimpleExpression>
					</Expression>
				</Or>
				<Expression>
					<SimpleExpression>
						<ValueExpression>
							<XPathQuery Type="Boolean">weight</XPathQuery>
						</ValueExpression>
						<Operator>Equal</Operator>
						<ValueExpression>
							<Value Type="Boolean">100</Value>
						</ValueExpression>
					</SimpleExpression> 
				</Expression> 
			</And> 
		 </Expression> 
  </Workload> 
 </Queries>"""

def generate_output(result):
    def parse_expression(expression):
        if 'And' in expression:
            and_expr = expression['And']
            return '(' + ' and '.join([parse_expression(expr) for expr in and_expr]) + ')'
        elif 'Or' in expression:
            or_expr = expression['Or']
            return '(' + ' or '.join([parse_expression(expr) for expr in or_expr]) + ')'
        elif 'SimpleExpression' in expression:
            simple_expr = expression['SimpleExpression']
            value_expr = simple_expr['ValueExpression']
            operator = simple_expr['Operator']
            if 'XPathQuery' in value_expr:
                return f"{value_expr['XPathQuery']['Value']} {operator} {value_expr['Value']['Value']}"
            elif 'Value' in value_expr:
                return f"{value_expr['Value']['Value']} {operator} {value_expr['Value']['Value']}"

    workload = result['Workload']
    expression = workload['Expression']
    output = f"where {parse_expression(expression)}"
    return output



parser = Parser(xml_input)
result = parser.parse()
print(result)
output = generate_output(result)
print(output)
