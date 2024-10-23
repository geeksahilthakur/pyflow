import ast


class CodeFlowExtractor(ast.NodeVisitor):
    def __init__(self):
        self.flowchart_steps = []
        self.node_counter = 0  # To uniquely identify nodes

    def add_step(self, step):
        """Add a step to the flowchart."""
        self.flowchart_steps.append(step)

    def visit_FunctionDef(self, node):
        func_name = node.name
        self.add_step(f"{func_name}[{func_name}()]")
        self.generic_visit(node)

    def visit_If(self, node):
        condition = ast.unparse(node.test)  # Converts AST node to code-like string
        decision_id = f"Decision_{self.node_counter}"
        self.node_counter += 1
        self.add_step(f"{decision_id}{{{condition}}}")

        # Link the decision to the first statement in the body
        if self.flowchart_steps:
            prev_node = self.flowchart_steps[-1].split("-->")[0]
            self.add_step(f"{prev_node} --> {decision_id}")

        # Visit body statements
        for stmt in node.body:
            self.visit(stmt)

        if node.orelse:
            else_id = f"Else_{self.node_counter}"
            self.node_counter += 1
            self.add_step(f"{decision_id} -->|No| {else_id}[Else]")
            for stmt in node.orelse:
                self.visit(stmt)

    def visit_Return(self, node):
        value = ast.unparse(node.value) if node.value else "None"
        return_id = f"Return_{self.node_counter}"
        self.node_counter += 1
        self.add_step(f"{return_id}[Return: {value}]")

        if self.flowchart_steps:
            prev_node = self.flowchart_steps[-1].split("-->")[0]
            self.add_step(f"{prev_node} --> {return_id}")

    def visit_For(self, node):
        target = ast.unparse(node.target)
        iter_ = ast.unparse(node.iter)
        loop_id = f"Loop_{self.node_counter}"
        self.node_counter += 1
        self.add_step(f"{loop_id}[Loop: for {target} in {iter_}]")

        if self.flowchart_steps:
            prev_node = self.flowchart_steps[-1].split("-->")[0]
            self.add_step(f"{prev_node} --> {loop_id}")

        for stmt in node.body:
            self.visit(stmt)

    def visit_While(self, node):
        condition = ast.unparse(node.test)
        loop_id = f"Loop_{self.node_counter}"
        self.node_counter += 1
        self.add_step(f"{loop_id}[Loop: while {condition}]")

        if self.flowchart_steps:
            prev_node = self.flowchart_steps[-1].split("-->")[0]
            self.add_step(f"{prev_node} --> {loop_id}")

        for stmt in node.body:
            self.visit(stmt)

    def extract_flow(self, code):
        """Parse the code and extract flowchart steps."""
        try:
            tree = ast.parse(code)
            self.visit(tree)
            return "\n".join(self.flowchart_steps)
        except SyntaxError as e:
            return f"Syntax error in code: {str(e)}"
        except Exception as e:
            return f"An error occurred: {str(e)}"


# Example Python code to test the flow extraction
code = """
class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            return None

    def is_empty(self):
        return len(self.stack) == 0
"""

# Extract and print the flowchart steps
extractor = CodeFlowExtractor()
flowchart_data = extractor.extract_flow(code)

# Generate final Mermaid.js syntax
mermaid_syntax = "graph TD;\n" + flowchart_data
print(mermaid_syntax)