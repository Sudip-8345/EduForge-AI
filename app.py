import json
import panel as pn
from schemas import GeneratorOutput, ReviewerOutput
from agents.graph import run_pipeline

pn.extension(design="material", sizing_mode="stretch_width")

# Input Widgets
grade_input = pn.widgets.IntSlider(
    name="Grade Level", start=1, end=12, step=1, value=4, width=300
)
topic_input = pn.widgets.TextInput(
    name="Topic", placeholder="e.g. Types of angles", width=400
)
run_button = pn.widgets.Button(name="Generate & Review", button_type="primary")
status_spinner = pn.indicators.LoadingSpinner(value=False, size=25, visible=False)


# Output Panes 
draft_pane = pn.pane.Markdown("", styles={"background": "#f8f9fa", "padding": "15px", "border-radius": "8px"})
review_pane = pn.pane.Markdown("", styles={"background": "#f8f9fa", "padding": "15px", "border-radius": "8px"})
refined_pane = pn.pane.Markdown("", styles={"background": "#f8f9fa", "padding": "15px", "border-radius": "8px"})
flow_pane = pn.pane.Markdown("", styles={"padding": "10px"})


# Formatting Helpers 
def format_content(content: GeneratorOutput) -> str:
    lines = ["### 📖 Explanation", "", content.explanation, "", "### ❓ MCQs", ""]
    for i, mcq in enumerate(content.mcqs, 1):
        lines.append(f"**Q{i}. {mcq.question}**")
        for opt in mcq.options:
            lines.append(f"- {opt}")
        lines.append(f"  \n✅ **Answer:** {mcq.answer}")
        lines.append("")
    return "\n".join(lines)


def format_review(review: ReviewerOutput) -> str:
    badge = "✅ **PASS**" if review.status == "pass" else "❌ **FAIL**"
    lines = [f"### Status: {badge}", ""]
    if review.feedback:
        lines.append("**Feedback:**")
        for fb in review.feedback:
            lines.append(f"- {fb}")
    else:
        lines.append("_No issues found._")
    return "\n".join(lines)


def format_flow(state: dict) -> str:
    steps = ["**Generate** ➜ **Review**"]
    if state.get("refined"):
        steps.append("➜ **Refine** ➜ **Review Refined**")
    return "### 🔄 Pipeline Flow\n\n" + " ".join(steps)


# Callback 
def on_run(event):
    topic = topic_input.value.strip()
    if not topic:
        draft_pane.object = "⚠️ Please enter a topic."
        return

    # Reset outputs
    draft_pane.object = ""
    review_pane.object = ""
    refined_pane.object = ""
    flow_pane.object = ""

    # Show spinner
    status_spinner.visible = True
    status_spinner.value = True
    run_button.disabled = True

    try:
        state = run_pipeline(grade=grade_input.value, topic=topic)

        # Draft
        draft_pane.object = format_content(state["draft"])

        # Review
        review_pane.object = format_review(state["review"])

        # Refined (if applicable)
        if state.get("refined"):
            refined_md = format_content(state["refined"])
            review_refined_md = ""
            if state.get("review_refined"):
                review_refined_md = "\n\n---\n\n" + format_review(state["review_refined"])
            refined_pane.object = refined_md + review_refined_md
        else:
            refined_pane.object = "_No refinement needed — content passed review._"

        # Flow
        flow_pane.object = format_flow(state)

    except Exception as exc:
        draft_pane.object = f"❌ **Error:** {exc}"

    finally:
        status_spinner.value = False
        status_spinner.visible = False
        run_button.disabled = False


run_button.on_click(on_run)


# Layout 
header = pn.pane.Markdown(
    "# 🎓 EduForge-AI\n**AI-powered educational content generator & reviewer**",
    styles={"text-align": "center"},
)

input_row = pn.Row(grade_input, topic_input, run_button, status_spinner, align="end")

tabs = pn.Tabs(
    ("📝 Generated Draft", draft_pane),
    ("🔍 Review Feedback", review_pane),
    ("✨ Refined Output", refined_pane),
    dynamic=True,
)

layout = pn.Column(
    header,
    pn.layout.Divider(),
    input_row,
    pn.layout.Divider(),
    flow_pane,
    tabs,
    max_width=900,
    styles={"margin": "0 auto"},
)

layout.servable()
