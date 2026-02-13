# 🎓 EduForge-AI

AI-powered educational content generator and reviewer built with **LangGraph**, **LangChain**, and **Panel**.

## Wanna try it ?
Click this link -> [**HuggingFace**](https://huggingface.co/spaces/tagc23/EduForge-AI)

## Architecture

**Generator Agent** — produces a grade-appropriate explanation + 3 MCQs.  
**Reviewer Agent** — evaluates for age appropriateness, correctness, and clarity.  
If the review fails, the Generator refines its output using the feedback (max 1 refinement pass).

## Project Structure

```
├── config.py            # env vars, model settings
├── schemas.py           # Pydantic models (input/output)
├── agents/
│   ├── generator.py     # Generator Agent
│   ├── reviewer.py      # Reviewer Agent
│   └── graph.py         # LangGraph workflow
├── app.py               # Panel UI
├── requirements.txt
└── .env.example
```

## Setup

```bash
# 1. Clone & enter the repo
git clone https://github.com/your-user/EduForge-AI.git
cd EduForge-AI

# 2. Create a virtual env & activate
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenAI key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 5. Run the Panel app
panel serve app.py --show
```

The browser will open at `http://localhost:5006/app`.

## Usage

1. Select a **Grade Level** (1-12).
2. Enter a **Topic** (e.g. "Types of angles").
3. Click **Generate & Review**.
4. View the tabs: **Generated Draft**, **Review Feedback**, **Refined Output**.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Your Groq API Key |
| `MODEL_NAME` | `llama-3.1-8b-instant` | Model to use for both agents |

## License

See [LICENSE](LICENSE).