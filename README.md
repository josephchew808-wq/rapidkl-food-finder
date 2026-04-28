RapidKL Food Finder (AI-Powered)
Core Concept:
This project demonstrates the use of LLMs to automate the creation of a local transit-food database.

Instead of manually typing menus, update_data.py uses the Gemini 2.0 Flash and Llama 3.1 APIs to identify real eateries near lrt/mrt/monorail stations.
The script uses Python logic to verify that the AI isn't giving false data.
The AI outputs raw JSON which is immediately ready for use.

Additionally, the system uses a decoupled architecture. 
I run the AI scouting agent locally to ensure data integrity and manage API costs. 
Once the AI generates the new JSON database, I push it to GitHub, which triggers a continuous deployment to the Streamlit frontend.
