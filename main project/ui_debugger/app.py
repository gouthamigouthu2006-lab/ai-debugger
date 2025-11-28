from flask import Flask, render_template, request
from sandbox import sandbox_run_python
from analyzer import analyze_error

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    error = ""
    patch_text = ""
    final_code = ""

    if request.method == "POST":
        user_code = request.form["code"]
        current_code = user_code

        # Run → Patch → Run loop (2 iterations)
        for _ in range(2):
            result = sandbox_run_python(current_code)

            output = result["stdout"]
            error = result["stderr"]

            if error.strip() == "":
                final_code = current_code
                break

            patch = analyze_error(error, current_code)

            if patch:
                patch_text = patch.patch
                current_code = patch.updated_code
            else:
                break

        final_code = current_code

    return render_template("index.html",
                           output=output,
                           error=error,
                           patch=patch_text,
                           final_code=final_code)

if __name__ == "__main__":
    app.run(debug=True)