import os
import google.generativeai as genai
from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
load_dotenv()
# --- Configure Google Generative AI ---
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except KeyError:
    print("Error: GEMINI_API_KEY environment variable not set.")
    print("Please set it before running the application. You can get one from Google AI Studio.")
    exit(1)

# Initialize the Gemini model
MODEL_NAME = "gemini-2.0-flash"  # You can experiment with "gemini-1.5-flash" for potentially faster responses
model = genai.GenerativeModel(MODEL_NAME)

app = Flask(__name__)

# We'll keep the PromptEnhancer class for structured input,
# but the AI will primarily enhance the *combined* version of it.


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
        Generates a semi-structured prompt from user inputs, to be given to the AI for full enhancement.
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

        if not parts:  # If nothing was entered
            return "The user has not provided any specific prompt components yet. Please provide a general purpose prompt to start, or ask what they want to achieve."

        return "\n\n".join(parts)


def ai_rephrase_and_enhance_prompt(user_input_for_ai):
    """
    Uses Google AI Studio (Gemini) to rephrase and enhance the user's prompt
    for better AI interaction, reducing hallucination and increasing efficiency.
    It also provides suggestions about what can go wrong.
    """
    try:
        # System instruction to guide the AI's behavior
        system_instruction = (
            "You are an expert Prompt Engineer specializing in crafting highly effective prompts "
            "for large language models. Your goal is to take a user's initial or semi-structured prompt "
            "and transform it into an optimal prompt that:\n"
            "1.  **Reduces Hallucination:** Adds clarity, specificity, and constraints to minimize invented information.\n"
            "2.  **Increases Efficiency:** Makes the request precise, direct, and unambiguous for faster, more relevant responses.\n"
            "3.  **Adds Crucial Elements:** Infers and adds elements like a specific role (e.g., 'Act as a senior Python developer'), "
            "    desired output format (e.g., 'Provide code in a Markdown block'), or specific constraints if beneficial, "
            "    even if not explicitly provided by the user.\n"
            "4.  **Provides Pitfall Warnings:** Identifies potential issues or common mistakes related to the prompt "
            "    that could lead to undesirable AI behavior (e.g., 'model might assume...').\n\n"
            "Your output MUST be in two distinct sections, clearly labeled:\n"
            "**Enhanced Prompt:** [Your completely rewritten and optimized prompt goes here]\n\n"
            "**Potential Pitfalls & Suggestions:** [Bulleted list of what could go wrong and how to mitigate it]\n"
        )

        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [{"text": system_instruction}]},
                {"role": "user", "parts": [{"text": f"Here is the user's input for a prompt:\n\n{user_input_for_ai}\n\nPlease provide the enhanced prompt and potential pitfalls:"}]}
            ]
        )

        # Parse the AI's response into two parts
        response_text = response.text
        enhanced_prompt_start = response_text.find("**Enhanced Prompt:**")
        pitfalls_start = response_text.find("**Potential Pitfalls & Suggestions:**")

        enhanced_prompt_content = ""
        pitfalls_content = ""

        if enhanced_prompt_start != -1 and pitfalls_start != -1:
            enhanced_prompt_content = response_text[enhanced_prompt_start + len("**Enhanced Prompt:**"):pitfalls_start].strip()
            pitfalls_content = response_text[pitfalls_start + len("**Potential Pitfalls & Suggestions:**"):].strip()
        elif enhanced_prompt_start != -1:  # Only enhanced prompt found
            enhanced_prompt_content = response_text[enhanced_prompt_start + len("**Enhanced Prompt:**"):].strip()
        elif pitfalls_start != -1:  # Only pitfalls found (less likely, but for robustness)
            pitfalls_content = response_text[pitfalls_start + len("**Potential Pitfalls & Suggestions:**"):].strip()
        else:  # Cannot parse, return raw response
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

        # This is the prompt that gets sent to our "AI Prompt Engineer"
        user_input_for_ai = enhancer.generate_raw_prompt_for_ai()

        # Always call AI to enhance
        ai_enhanced_prompt_output, ai_pitfalls_output = ai_rephrase_and_enhance_prompt(user_input_for_ai)

        # The initial user-assembled prompt can still be shown if helpful for comparison
        user_assembled_prompt = enhancer.generate_raw_prompt_for_ai()

    return render_template("index.html",
                           user_assembled_prompt=user_assembled_prompt,
                           ai_enhanced_prompt_output=ai_enhanced_prompt_output,
                           ai_pitfalls_output=ai_pitfalls_output)


if __name__ == "__main__":
    app.run(debug=True)
