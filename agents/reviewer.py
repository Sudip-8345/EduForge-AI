from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY, MODEL_NAME
from schemas import GeneratorOutput, ReviewerOutput


REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a strict educational content reviewer. "
        "Evaluate the content against three criteria:\n"
        "1. Age appropriateness — vocabulary and sentence length must suit Grade {grade}.\n"
        "2. Conceptual correctness — all facts and MCQ answers must be accurate.\n"
        "3. Clarity — the explanation must be easy to follow; questions must be unambiguous.\n\n"
        "Be fair but thorough. Only mark 'fail' if there are real problems."
    ),
    (
        "human",
        "Grade: {grade}  |  Topic: \"{topic}\"\n\n"
        "Content to review:\n{content}\n\n"
        "Return a JSON with:\n"
        "- \"status\": \"pass\" or \"fail\"\n"
        "- \"feedback\": a list of specific issues (empty list if pass)\n\n"
        "Return ONLY the structured JSON."
    ),
])



def _get_llm() -> ChatGroq:
    return ChatGroq(
        model=MODEL_NAME,
        api_key=GROQ_API_KEY,
        temperature=0.0,
    )



def review_content(
    grade: int,
    topic: str,
    content: GeneratorOutput,
) -> ReviewerOutput:
    llm = _get_llm().with_structured_output(ReviewerOutput)
    chain = REVIEW_PROMPT | llm
    result = chain.invoke({
        "grade": grade,
        "topic": topic,
        "content": content.model_dump_json(indent=2),
    })
    return result
