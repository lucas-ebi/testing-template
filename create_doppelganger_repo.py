import os
import ast
import astunparse
import argparse
import black

def replicate_directory_structure(src_dir, dst_dir):
    for root, dirs, files in os.walk(src_dir):
        # Compute destination directory
        relative_path = os.path.relpath(root, src_dir)
        dest_path = os.path.join(dst_dir, relative_path)

        # Create destination directory if it doesn't exist
        os.makedirs(dest_path, exist_ok=True)

        # Process each file
        for file in files:
            if file.endswith('.py'):
                create_stub_file(os.path.join(root, file), os.path.join(dest_path, file))

def create_stub_file(src_file, dst_file):
    with open(src_file, 'r') as file:
        source_code = file.read()

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Visit each node and create stubs
    class StubGenerator(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            # Replace the function body with a pass statement
            node.body = [ast.Pass()]
            return node

        def visit_AsyncFunctionDef(self, node):
            # Replace the async function body with a pass statement
            node.body = [ast.Pass()]
            return node

        def visit_ClassDef(self, node):
            # Replace methods within the class with pass statements
            new_body = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    item.body = [ast.Pass()]
                new_body.append(item)
            node.body = new_body
            return node

        def visit_Module(self, node):
            # Remove top-level docstrings and comments
            new_body = []
            for item in node.body:
                if isinstance(item, ast.Expr) and isinstance(item.value, ast.Str):
                    continue  # Skip string expressions (likely comments)
                if isinstance(item, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                    new_body.append(self.visit(item))
                else:
                    # For other top-level items, add a pass statement if they are not functions or classes
                    new_body.append(item)
            node.body = new_body
            return node

    transformed_tree = StubGenerator().visit(tree)
    stub_code = astunparse.unparse(transformed_tree)
    formatted_stub_code = black.format_str(stub_code, mode=black.FileMode())

    # Write the formatted stub code to the destination file
    with open(dst_file, 'w') as file:
        file.write(formatted_stub_code)

def create_doppelganger_repo(main_repo, doppelganger_repo):
    # Create the sibling repository directory
    os.makedirs(doppelganger_repo, exist_ok=True)
    # Replicate the directory structure and create stubs
    replicate_directory_structure(main_repo, doppelganger_repo)

def main():
    parser = argparse.ArgumentParser(description="Create a doppelgänger repository with stubs for a main repository.")
    parser.add_argument("main_repo", help="Path to the main repository")
    parser.add_argument("doppelganger_repo", help="Path to the doppelgänger repository")

    args = parser.parse_args()

    create_doppelganger_repo(args.main_repo, args.doppelganger_repo)

if __name__ == '__main__':
    main()
