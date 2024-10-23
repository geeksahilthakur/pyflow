from flask import Flask, render_template, request, jsonify
import ast

app = Flask(__name__)

class CodeFlowExtractor(ast.NodeVisitor):
    def __init__(self):
        self.flowchart_steps = []

    def visit_FunctionDef(self, node):
        self.flowchart_steps.append({'name': f'Start Function: {node.name}', 'children': []})
        for n in node.body:
            self.visit(n)

    def visit_If(self, node):
        condition = ast.unparse(node.test)
        decision_node = {'name': f'Decision: {condition}', 'children': []}
        self.flowchart_steps[-1]['children'].append(decision_node)

        for n in node.body:
            self.visit(n)

        if node.orelse:
            else_node = {'name': 'Else', 'children': []}
            self.flowchart_steps[-1]['children'].append(else_node)
            for n in node.orelse:
                self.visit(n)

    def visit_Return(self, node):
        value = ast.unparse(node.value) if node.value else 'None'
        self.flowchart_steps.append({'name': f'Return: {value}', 'children': []})

    def extract_flow(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        return self.flowchart_steps


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    code = request.form['code']
    extractor = CodeFlowExtractor()
    flowchart_data = extractor.extract_flow(code)

    # Return the flowchart data as JSON
    return jsonify(flowchart_data)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
