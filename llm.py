from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import json
import re

load_dotenv()

categories = [
    "Work",
    "Personal",
    "Health",
    "Shopping",
    "Urgent",
    "Other",
]

priority=["High", "Medium", "Low"]


def llm_query_optimization(content: str) -> list[str]:
    """
    Break a long multi-hop request into smaller actionable queries.
    """
    try:
        llm = ChatOpenAI(model="gpt-5-nano")
        messages = [
            (
                "system",
                """
                You are a query planner for a todo assistant.
                Convert the user request into a sequence of smaller, clear, actionable sub-queries.

                RULES:
                1. Return ONLY valid JSON.
                2. JSON format must be:
                {
                    "queries": ["string", "string"]
                }
                3. Each query should be atomic and executable as one todo item.
                4. Preserve the user intent and logical order.
                5. Do not include markdown, or extra keys.
                """,
            ),
            ("user", content),
        ]

        response = llm.invoke(messages)
        predicted = str(response.content).strip()
        if predicted.startswith("```") and predicted.endswith("```"):
            predicted = re.sub(r"^```(?:json)?\s*", "", predicted, flags=re.IGNORECASE)
            predicted = re.sub(r"\s*```$", "", predicted).strip()

        payload = json.loads(predicted)
        queries = payload.get("queries", [])
        if not isinstance(queries, list):
            return [content]

        cleaned_queries = [str(q).strip() for q in queries if str(q).strip()]
        return cleaned_queries if cleaned_queries else [content]
    except Exception as e:
        print(f"llm_query_optimization error: {e}")
        return [content]

def llm_categorization(content: str) -> str:
    try:
        llm = ChatOpenAI(model="gpt-5-nano")
        messages = [
            (
                "system",
                f"""
                You are a task assistant. Your role is to categroise, summarise and prioritise the task.
                RULES:
                1. Categorize the user's task into ONLY one of these categories:
                {categories}
                2. Set the priority of the task, based on any of the options : {priority}
                3. Summarize the whole task in short, not more than 10 words.

                JSON format:
                {{
                    "category" : "string",
                    "priority" : "string",
                    "summary" : "string"
                }}
                """
            ),
            ("user", content),
        ]

        response = llm.invoke(messages)
        predicted = response.content.strip()
        
        # print("CONTENT:")
        # print(response.content)

        return predicted
    except Exception as e:
        print(f"LLM ERROR: {e}")
        return "Other"

#Extact output of llm fields
def extract_llm_fields(content: str) -> tuple[str, str, str]:
    llm_response = llm_categorization(content)
    default_values = ("Other", "Low", "")

    if isinstance(llm_response, dict):
        payload = llm_response
    else:
        try:
            cleaned_response = str(llm_response).strip()
            if cleaned_response.startswith("```") and cleaned_response.endswith("```"):
                cleaned_response = re.sub(r"^```(?:json)?\s*", "", cleaned_response, flags=re.IGNORECASE)
                cleaned_response = re.sub(r"\s*```$", "", cleaned_response)
                cleaned_response = cleaned_response.strip()

            # If there is surrounding text, extract the first JSON object.
            if not cleaned_response.startswith("{"):
                json_match = re.search(r"\{[\s\S]*\}", cleaned_response)
                if json_match:
                    cleaned_response = json_match.group(0)

            payload = json.loads(cleaned_response)
        except (TypeError, json.JSONDecodeError) as e:
            print(f"extract_llm_fields parse error: {e}")
            print(f"Raw llm_response: {llm_response!r}")
            return default_values

    try:
        category = str(payload["category"]).strip()
        priority = str(payload["priority"]).strip()
        summary = str(payload["summary"]).strip()
        # print(f"Extracted content : {category}, {priority}, {summary}")
    except (TypeError, KeyError) as e:
        print(f"extract_llm_fields payload error: {e}")
        print(f"Payload received: {payload!r}")
        return default_values

    return category, priority, summary