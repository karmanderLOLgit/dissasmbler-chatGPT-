#dissasmbler 
import asyncio
import os
import ast
import dis
import openai

# key
openai.api_key = "s"
# extract functions
def func(file_path):
    """Read a Python file and extract all functions."""
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
    return functions

# Function to disassemble a single Python function
def disassemble(func_code):
    """Disassemble a single function and return its bytecode."""
    bytecode = dis.Bytecode(func_code)
    disassembled_code = []
    for instruction in bytecode:
        disassembled_code.append(f"{instruction.opname} {instruction.argval if instruction.arg is not None else ''}")
    return '\n'.join(disassembled_code)

# Function to disassemble all functions in the file
def disassemble_all_functions(file_path):
    """Disassemble all functions in the given Python file."""
    functions = get_functions_from_file(file_path)
    disassembled_code = {}

    with open(file_path, 'r') as file:
        code = file.read()

    for function_node in functions:
        function_name = function_node.name
        # Compile the function code into a code object
        function_code = compile(ast.Module(body=[function_node], type_ignores=[]), '<string>', 'exec')
        # Disassemble the function code
        disassembled_code[function_name] = disassemble_function(function_code)

    return disassembled_code

async def openai(bytecode):
    """Use OpenAI to explain the bytecode mnemonics asynchronously."""
    prompt = f"Please explain the following Python bytecode mnemonics:\n\n{bytecode}"

    try:
        # Correct API call for completion request
        response = openai.Completion.create(
            model="gpt-4",  # Use the appropriate model
            prompt=prompt,
            max_tokens=150,
            temperature=0.5,
            stream=False  # Setting stream=False for a simple response
        )

        # Extract the explanation from the response
        explanation = response['choices'][0]['text'].strip()
        return explanation

    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Error: Failed to get explanation from OpenAI."

# Main function to drive the script
async def main():
    # Get the file path from the user via console input
    file_path = input("Enter the path to the Python file you want to analyze: ").strip()

    try:
        # Disassemble all functions in the given Python file
        disassembled_code = disassemble_all_functions(file_path)

        if disassembled_code:
            # Process each function's bytecode asynchronously
            for function_name, bytecode in disassembled_code.items():
                print(f"\nExplaining bytecode for function: {function_name}")
                explanation = await openai(bytecode)  # Await the async function call
                print(f"Explanation for {function_name}:\n{explanation}\n")
        else:
            print("No functions found in the given Python file or an error occurred during disassembly.")
    except Exception as e:
        print(f"Error: {e}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())  # Run the main function within asyncio event loop
