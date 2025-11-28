import difflib
import re

class PatchResult:
    def __init__(self, explanation, patch, updated_code):
        self.explanation = explanation     # Why the fix is needed
        self.patch = patch                 # Unified diff
        self.updated_code = updated_code   # New repaired code


# ----------------------------------------------------
#  MAIN ERROR ANALYZER FUNCTION
# ----------------------------------------------------
def analyze_error(stderr: str, code: str):
    """
    Takes stderr + original code.
    Detects error type and returns a PatchResult object.
    If no fix is found → returns None.
    """

    # No error → no fix needed
    if stderr.strip() == "":
        return None

    # 1. SyntaxError
    if "SyntaxError" in stderr:
        return fix_syntax_error(stderr, code)

    # 2. IndentationError
    if "IndentationError" in stderr:
        return fix_indentation_error(stderr, code)

    # 3. IndexError
    if "IndexError" in stderr:
        return fix_index_error(stderr, code)

    # 4. TypeError
    if "TypeError" in stderr:
        return fix_type_error(stderr, code)

    # 5. NameError
    if "NameError" in stderr:
        return fix_name_error(stderr, code)

    # 6. ZeroDivisionError
    if "ZeroDivisionError" in stderr:
        return fix_zero_division(stderr, code)

    # No rule found
    return None


# ----------------------------------------------------
#  ERROR-SPECIFIC FIX FUNCTIONS
# ----------------------------------------------------

# 1️⃣ SyntaxError Fix
def fix_syntax_error(stderr, code):
    """
    Common SyntaxError fix:
    - Missing colon at end of statements (def, if, for, while)
    """
    lines = code.splitlines()

    match = re.search(r"line (\d+)", stderr)
    if match:
        line_no = int(match.group(1)) - 1

        if 0 <= line_no < len(lines):
            line = lines[line_no]

            # detect missing colon
            if ("def " in line or "if " in line or "elif " in line or
                "for " in line or "while " in line or "else" in line) and not line.strip().endswith(":"):

                lines[line_no] = line + ":"
                patched_code = "\n".join(lines)

                patch = generate_diff(code, patched_code)

                return PatchResult(
                    "Added missing ':' to fix SyntaxError.",
                    patch,
                    patched_code
                )

    return None


# 2️⃣ IndentationError Fix
def fix_indentation_error(stderr, code):
    """
    Simple auto-indent: adds 4 spaces to lines that are not empty.
    """
    lines = code.splitlines()
    fixed = []

    for line in lines:
        if line.strip() != "":
            fixed.append("    " + line)
        else:
            fixed.append(line)

    patched_code = "\n".join(fixed)
    patch = generate_diff(code, patched_code)

    return PatchResult(
        "Auto-indented code to fix IndentationError.",
        patch,
        patched_code
    )


# 3️⃣ IndexError Fix (off-by-one)
def fix_index_error(stderr, code):
    """
    Detects range(len(...)) loops and adjusts to prevent IndexError.
    """
    fixed = code.replace("range(len(", "range(len(").replace("))", ") - 1))")

    patch = generate_diff(code, fixed)

    return PatchResult(
        "Adjusted loop index to avoid IndexError.",
        patch,
        fixed
    )


# 4️⃣ TypeError Fix
def fix_type_error(stderr, code):
    """
    Converts wrong type operations:
    e.g. "hello" + 5 → "hello" + str(5)
    """
    fixed = re.sub(r'(\+\s*\d+)', r'+ str(\1)', code)

    patch = generate_diff(code, fixed)

    return PatchResult(
        "Wrapped incompatible types with str() to fix TypeError.",
        patch,
        fixed
    )


# 5️⃣ NameError Fix
def fix_name_error(stderr, code):
    """
    Adds a missing variable declaration
    Example:
        NameError: name 'x' is not defined
    → Adds: x = 0 at the top
    """
    match = re.search(r"name '(\w+)' is not defined", stderr)
    if match:
        var = match.group(1)

        new_code = f"{var} = 0\n" + code
        patch = generate_diff(code, new_code)

        return PatchResult(
            f"Added missing variable declaration for '{var}'.",
            patch,
            new_code
        )

    return None


# 6️⃣ ZeroDivisionError Fix
def fix_zero_division(stderr, code):
    """
    Replace /0 with /1
    """
    fixed = code.replace("/0", "/1")
    patch = generate_diff(code, fixed)

    return PatchResult(
        "Replaced division by zero with division by 1.",
        patch,
        fixed
    )


# ----------------------------------------------------
#  DIFF GENERATOR
# ----------------------------------------------------
def generate_diff(original, updated):
    """
    Generates unified diff patch like git.
    """
    diff = difflib.unified_diff(
        original.splitlines(),
        updated.splitlines(),
        fromfile="original.py",
        tofile="updated.py",
        lineterm=""
    )
    return "\n".join(diff) 