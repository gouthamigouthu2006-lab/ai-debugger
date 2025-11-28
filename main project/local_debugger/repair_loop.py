from sandbox import sandbox_run_python
from analyzer import analyze_error

def repair_code(code, max_iterations=3):
    current_code = code

    for i in range(max_iterations):
        print(f"\n=== Iteration {i+1} ===")

        # Step 1: Run in sandbox
        result = sandbox_run_python(current_code)

        print("\n--- Program Output ---")
        print(result["stdout"])
        print(result["stderr"])

        # If no errors → DONE
        if result["stderr"].strip() == "":
            print("\n✔ Code executed successfully!")
            return current_code

        # Step 2: Analyze error & generate patch
        patch = analyze_error(result["stderr"], current_code)

        if not patch:
            print("\n✖ No fix could be generated.")
            return current_code

        print("\n--- Patch Suggested ---")
    
        print(patch.explanation)
        print(patch.patch)

        # Step 3: Apply patch
        current_code = patch.updated_code

    print("\n✖ Reached max repair iterations.")

    return current_code


if __name__ == "__main__":
    # Example wrong code to test
    broken_code = """
def greet(name)
    print("Hello", name)

greet("Amrutha")
"""

    repaired = repair_code(broken_code)
    print("\n=== Final Repaired Code ===")
    print(repaired)
    
