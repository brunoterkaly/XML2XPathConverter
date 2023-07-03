# XML-to-XPath Python Parser

This Python script reads an XML document, parses it into a dictionary tree, traverses the tree, and generates XPath expressions. These expressions are then written to an output file. The script uses various helper functions to assist with these tasks and performs lookups in dictionaries to convert certain strings to their corresponding XPath equivalents.

## Features

- Parse XML documents and represent them as dictionary trees.
- Generate XPath expressions based on the parsed XML tree.
- Write XPath expressions to an output file.

## How to Run

1. Ensure you have Python 3.x installed.
2. Place your input XML document in the same directory as the script, or update the file path in the `main()` function.
3. Run the script using the following command:
    ```
    python <script_name>.py
    ```
4. The script will generate an output text file (`output.txt`) in the same directory, containing the XPath expressions.

## Functionality

- `parse_expression()`: Parses XML string and returns a dictionary representing the XML structure.
- `parse_node()`: Recursively traverses XML node tree and builds a dictionary.
- `generate_value_expression()`: Generates value expression from a node in the tree.
- `generate_simple_expression()`: Generates simple expression using the operator and the values.
- `process_trees()`: Traverses the XML tree and processes each 'Workload' tag.
- `process_tree()`: Performs depth-first traversal of the XML tree and generates XPath expressions.
- `generate_where_clause()`: Generates WHERE clause for the expression.
- `get_dictionary_lookup()`: Returns corresponding value from the dictionary. If not found, returns the parameter as is.
- `need_quotes()`: Checks if parameter needs to be enclosed in quotes.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
