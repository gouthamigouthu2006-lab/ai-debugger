from sandbox import sandbox_run_python

code = """
for i in range(3):
    print("Hi", i)
"""

result = sandbox_run_python(code)
print(result)