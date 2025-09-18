# prompt-enhancer

AI Prompt Enhancer
This is a simple web tool that helps you create better prompts for large language models (LLMs) like Gemini. You give it your basic idea, and it uses AI to turn it into a more effective and efficient prompt.
What It Does
 * Structured Input: Lets you break down your prompt idea into parts like role, task, context, and constraints.
 * AI-Powered Enhancement: Uses the Google Gemini model to rewrite your prompt, making it clearer and more specific.
 * Reduces Errors: The enhanced prompts are designed to reduce the chance of the AI making up information (hallucination).
 * Identifies Problems: The tool also gives you a list of "Potential Pitfalls," which are warnings about what might go wrong with your prompt and how to fix it.
How It Works
 * You Fill Out a Form: You enter your ideas into different fields on a webpage, such as a base prompt, a role for the AI, and the specific task.
 * The App Assembles a "Raw" Prompt: The code takes all your inputs and puts them together into a single, semi-structured prompt.
 * It Asks an AI for Help: This raw prompt is sent to the Google Gemini AI. [cite_start]The app tells Gemini to act like an expert "Prompt Engineer."
 * Gemini Rewrites the Prompt: The Gemini model analyzes your input and creates a new, optimized prompt. [cite_start]It also creates a bulleted list of potential problems and suggestions.
 * Results are Displayed: The app shows you the final "Enhanced Prompt" and the "Potential Pitfalls" on the webpage.
How to Set Up and Run
1. Prerequisites
You need to have Python 3 and pip installed on your computer.
2. Install Required Libraries
This project uses a few Python libraries. You can install them using pip:
pip install Flask google-generativeai python-dotenv

3. Get a Google Gemini API Key
This program needs a Google Gemini API key to work.
 * Go to Google AI Studio to get your key.
 * Create a file named .env in the same folder as the main.py file.
 * Inside the .env file, add your API key like this:
   GEMINI_API_KEY="YOUR_API_KEY_HERE"

   Replace "YOUR_API_KEY_HERE" with your actual key.
4. Run the Application
Once the setup is complete, you can run the app with this command:
python main.py

The program will start a local web server. Open your web browser and go to the address it shows (usually http://127.0.0.1:3000).
How to Use the Tool
 * Open the web page in your browser.
 * Fill in any of the form fields. You can start with just a "Base Prompt" or add more details like "Role," "Task," "Constraints," etc.
 * Click the "Enhance Prompt" button.
 * The page will reload with the AI-generated "Enhanced Prompt" and the "Potential Pitfalls & Suggestions" sections filled in.