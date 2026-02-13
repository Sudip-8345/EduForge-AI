from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY, MODEL_NAME
from schemas import GeneratorOutput


GENERATE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert educational content creator. "
        "Generate content that is age-appropriate for Grade {grade} students. "
        "Use simple vocabulary and short sentences for lower grades. "
        "All concepts must be factually correct."
    ),
    (
        "human",
        "Create an educational lesson on the topic: \"{topic}\" for Grade {grade}.\n\n"
        "Produce:\n"
        "1. A clear explanation of the topic (3-5 sentences, grade-appropriate language).\n"
        "2. Exactly 3 multiple-choice questions, each with 4 options (A, B, C, D) "
        "and the correct answer letter.\n\n"
        "Return ONLY the structured JSON."
    ),
])

REFINE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert educational content creator. "
        "A reviewer found issues with your previous draft. "
        "Fix every issue while keeping the content for Grade {grade}."
    ),
    (
        "human",
        "Topic: \"{topic}\"  |  Grade: {grade}\n\n"
        "Previous draft:\n{previous_draft}\n\n"
        "Reviewer feedback:\n{feedback}\n\n"
        "Produce a fully corrected version. "
        "Return ONLY the structured JSON."
    ),
])



def _get_llm() -> ChatGroq:
    return ChatGroq(
        model=MODEL_NAME,
        api_key=GROQ_API_KEY,
        temperature=0.3,
    )



def generate_content(grade: int, topic: str) -> GeneratorOutput:
    llm = _get_llm().with_structured_output(GeneratorOutput)
    chain = GENERATE_PROMPT | llm
    result = chain.invoke({"grade": grade, "topic": topic})
    return result


def refine_content(
    grade: int,
    topic: str,
    previous_draft: GeneratorOutput,
    feedback: list[str],
) -> GeneratorOutput:
    llm = _get_llm().with_structured_output(GeneratorOutput)
    chain = REFINE_PROMPT | llm
    result = chain.invoke({
        "grade": grade,
        "topic": topic,
        "previous_draft": previous_draft.model_dump_json(indent=2),
        "feedback": "\n".join(f"- {f}" for f in feedback),
    })
    return result
