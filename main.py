import os

from dotenv import load_dotenv
from flask import Flask, render_template, request

# --- New SDK Imports ---
from google import genai
from google.genai import types

load_dotenv()

# --- Configure Google Gen AI Client ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    print("Please set it before running the application.")
    exit(1)

# Initialize the Client (replaces genai.configure)
client = genai.Client(api_key=api_key)

# Update to a valid model name for the new SDK (e.g., gemini-2.0-flash)
MODEL_NAME = "gemini-2.5-flash"

app = Flask(__name__)


class PromptEnhancer:
    def __init__(self, base_prompt=""):
        self.base_prompt = base_prompt
        self.context = []
        self.role = ""
        self.task = ""
        self.format = ""
        self.constraints = []
        self.examples = []

    def set_base_prompt(self, prompt):
        self.base_prompt = prompt

    def add_context(self, context_info):
        if context_info:
            self.context.append(context_info)

    def set_role(self, role_description):
        self.role = role_description

    def set_task(self, task_description):
        self.task = task_description

    def set_format(self, format_description):
        self.format = format_description

    def add_constraint(self, constraint_description):
        if constraint_description:
            self.constraints.append(constraint_description)

    def add_example(self, example_text):
        if example_text:
            self.examples.append(example_text)

    def generate_raw_prompt_for_ai(self):
        """
        Generates a semi-structured prompt from user inputs.
        """
        parts = []
        if self.base_prompt:
            parts.append(f"User's Initial Request: {self.base_prompt}")
        if self.role:
            parts.append(f"User suggested role: {self.role}")
        if self.task:
            parts.append(f"User suggested task: {self.task}")
        if self.format:
            parts.append(f"User suggested format: {self.format}")
        if self.context:
            parts.append("User provided context:")
            for item in self.context:
                parts.append(f"- {item}")
        if self.constraints:
            parts.append("User provided constraints:")
            for item in self.constraints:
                parts.append(f"- {item}")
        if self.examples:
            parts.append("User provided examples:")
            for item in self.examples:
                parts.append(f"- {item}")

        if not parts:
            return "The user has not provided any specific prompt components yet."

        return "\n\n".join(parts)


def ai_rephrase_and_enhance_prompt(user_input_for_ai):
    """
    Uses the new Google Gen AI SDK to rephrase and enhance the prompt.
    """
    try:
        # Define the system instruction text
        system_instruction_text = (
            "You are an expert Prompt Engineer specializing in crafting highly effective prompts "
            "for large language models. Your goal is to take a user's initial or semi-structured prompt "
            "and transform it into an optimal prompt that:\n"
            "1.  **Reduces Hallucination:** Adds clarity and constraints.\n"
            "2.  **Increases Efficiency:** Makes the request precise.\n"
            "3.  **Adds Crucial Elements:** Infers missing roles, formats, or constraints.\n"
            "4.  **Provides Pitfall Warnings:** Identifies potential issues.\n\n"
            "Your output MUST be in two distinct sections, clearly labeled:\n"
            "**Enhanced Prompt:** [Your completely rewritten and optimized prompt goes here]\n\n"
            "**Potential Pitfalls & Suggestions:** [Bulleted list of what could go wrong]\n"
        )

        # --- New SDK Generation Call ---
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"Here is the user's input for a prompt:\n\n{user_input_for_ai}\n\nPlease provide the enhanced prompt and potential pitfalls:",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction_text,
                temperature=0.7,  # Optional: Adjust creativity
            ),
        )

        response_text = response.text

        # Parse the AI's response (same logic as before)
        enhanced_prompt_start = response_text.find("**Enhanced Prompt:**")
        pitfalls_start = response_text.find("**Potential Pitfalls & Suggestions:**")

        enhanced_prompt_content = ""
        pitfalls_content = ""

        if enhanced_prompt_start != -1 and pitfalls_start != -1:
            enhanced_prompt_content = response_text[
                enhanced_prompt_start + len("**Enhanced Prompt:**") : pitfalls_start
            ].strip()
            pitfalls_content = response_text[
                pitfalls_start + len("**Potential Pitfalls & Suggestions:**") :
            ].strip()
        elif enhanced_prompt_start != -1:
            enhanced_prompt_content = response_text[
                enhanced_prompt_start + len("**Enhanced Prompt:**") :
            ].strip()
        elif pitfalls_start != -1:
            pitfalls_content = response_text[
                pitfalls_start + len("**Potential Pitfalls & Suggestions:**") :
            ].strip()
        else:
            return "Could not parse AI response. Raw response:\n" + response_text, "N/A"

        return enhanced_prompt_content, pitfalls_content

    except Exception as e:
        return f"Error enhancing prompt with AI: {e}", "Error in AI call."


@app.route("/", methods=["GET", "POST"])
def index():
    user_assembled_prompt = ""
    ai_enhanced_prompt_output = ""
    ai_pitfalls_output = ""

    if request.method == "POST":
        enhancer = PromptEnhancer()
        enhancer.set_base_prompt(request.form.get("base_prompt", ""))
        enhancer.set_role(request.form.get("role", ""))
        enhancer.set_task(request.form.get("task", ""))
        enhancer.set_format(request.form.get("format", ""))

        context_items = request.form.getlist("context[]")
        for item in context_items:
            enhancer.add_context(item.strip())

        constraint_items = request.form.getlist("constraint[]")
        for item in constraint_items:
            enhancer.add_constraint(item.strip())

        example_items = request.form.getlist("example[]")
        for item in example_items:
            enhancer.add_example(item.strip())

        user_input_for_ai = enhancer.generate_raw_prompt_for_ai()

        ai_enhanced_prompt_output, ai_pitfalls_output = ai_rephrase_and_enhance_prompt(
            user_input_for_ai
        )

        user_assembled_prompt = enhancer.generate_raw_prompt_for_ai()

    return render_template(
        "index.html",
        user_assembled_prompt=user_assembled_prompt,
        ai_enhanced_prompt_output=ai_enhanced_prompt_output,
        ai_pitfalls_output=ai_pitfalls_output,
    )


if __name__ == "__main__":
    app.run(debug=True)
