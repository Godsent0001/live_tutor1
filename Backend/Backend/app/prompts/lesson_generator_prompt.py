from typing import List, Optional


def build_subtopics_prompt(
    topic: str,
    extra_materials: Optional[List[str]] = None,
    context_prompt: Optional[str] = None
) -> str:
    """
    Generates a prompt to get a granular list of sub-topics.
    """
    materials_text = ""
    if extra_materials:
        materials_text = "\n".join([f"- {m}" for m in extra_materials])

    context_text = ""
    if context_prompt:
        context_text = f"\nSPECIAL INSTRUCTION FROM STUDENT:\n{context_prompt}\n"

    return f"""
You are an expert educational architect. Your task is to take a main topic and break it down into a highly granular, detailed list of sub-topics for a comprehensive course.

MAIN TOPIC:
{topic}

EXTRA MATERIALS (if any):
{materials_text if materials_text else "None"}
{context_text}

---
STRICT RULES:
1. Break down the topic into as many sub-topics as possible (aim for 25, 50, or even 100 if the topic allows).
2. Each sub-topic should be a single, clear learning objective or concept.
3. The list must be progressive, moving from foundational concepts to advanced ones.
4. Output MUST be valid JSON only.
5. Do NOT include markdown or explanations.

REQUIRED JSON FORMAT:
{{
  "lesson_title": "A clear, engaging title for the entire course",
  "sub_topics": [
    "Sub-topic 1 title",
    "Sub-topic 2 title",
    ...
  ]
}}

OUTPUT NOW:
Return ONLY the JSON.
"""

def build_single_module_prompt(
    lesson_title: str,
    sub_topic: str,
    context_prompt: Optional[str] = None
) -> str:
    """
    Generates a prompt to create content for a single sub-topic (module).
    """
    context_text = ""
    if context_prompt:
        context_text = f"\nSPECIAL INSTRUCTION FROM STUDENT: {context_prompt}\n"

    return f"""
You are a system that generates structured learning modules.

You do NOT explain the topic outside the JSON.
You ONLY output valid JSON in the required format.

---

COURSE TITLE:
{lesson_title}

CURRENT SUB-TOPIC TO TEACH:
{sub_topic}
{context_text}

---

STRICT RULES:

- Output MUST be valid JSON only
- Do NOT include markdown or extra text
- Follow the structure exactly
- Keep language simple and clear (Grade 8 level)

---

MODULE STRUCTURE FORMAT:

{{
  "module_title": "{sub_topic}",
  "steps": [
    {{
      "step_id": "unique_string",
      "speech": "Explain this concept in plain, everyday language. Write like you are talking to a friend who has never heard of this before. No jargon. Maximum 3 sentences.",
      "board": {{
        "type": "one of: hierarchy | flowchart | table | bullet | timeline | formula | comparison | process",
        "content": ["short phrase 1", "short phrase 2", "short phrase 3"]
      }},
      "question": {{
        "type": "recall | explanation | application | multiple_choice | true_false",
        "text": "A short, simple question."
      }},
      "expected_concepts": ["concept 1", "concept 2"]
    }}
  ]
}}

---

IMPORTANT DESIGN RULES:
1. Generate exactly ONE module for this sub-topic.
2. The module MUST have 5 steps.
3. Every step MUST include: speech, board, question.
4. Use real-world examples and analogies.
5. Write speech at a Grade 8 reading level.
6. Board content items must be SHORT — max 8 words each.

---

BOARD USAGE RULES:
- hierarchy | flowchart | table | bullet | timeline | formula | comparison | process

QUESTION DESIGN RULES:
- recall | explanation | application | multiple_choice | true_false

OUTPUT NOW:
Return ONLY the JSON module.
"""

def build_lesson_prompt(
    topic: str,
    extra_materials: Optional[List[str]] = None,
    context_prompt: Optional[str] = None
) -> str:
    """
    DEPRECATED: Use build_subtopics_prompt and build_single_module_prompt instead.
    Generates a strict prompt that forces the LLM
    to output structured lesson JSON only.
    """

    materials_text = ""
    if extra_materials:
        materials_text = "\n".join([f"- {m}" for m in extra_materials])

    context_text = ""
    if context_prompt:
        context_text = f"\nSPECIAL INSTRUCTION FROM STUDENT:\n{context_prompt}\n"

    return f"""
You are a system that generates structured learning lessons.

You do NOT explain the topic.
You do NOT write essays.
You ONLY output valid JSON in the required format.

---

TASK:
Create a structured lesson for the topic below.

TOPIC:
{topic}

EXTRA MATERIALS (if any):
{materials_text if materials_text else "None"}
{context_text}
---

STRICT RULES:

- Output MUST be valid JSON only
- Do NOT include markdown
- Do NOT include explanations
- Do NOT include extra text outside JSON
- Every lesson MUST follow this structure exactly
- Keep language simple and clear

---

LESSON STRUCTURE FORMAT:

{{
  "lesson_title": "...",

  "modules": [
    {{
      "module_title": "...",

      "steps": [
        {{
          "step_id": "string or number",

          "speech": "Explain this concept in plain, everyday language. Write like you are talking to a friend who has never heard of this before. No jargon. No technical terms unless absolutely necessary — and if you must use one, explain it immediately in simple words. Maximum 3 sentences.",

          "board": {{
            "type": "one of: hierarchy | flowchart | table | bullet | timeline | formula | comparison | process",

            "content": [
              "short phrase 1",
              "short phrase 2",
              "short phrase 3"
            ]
          }},

          "question": {{
            "type": "recall | explanation | application | multiple_choice | true_false",

            "text": "A short, simple question. Avoid complex wording."
          }},

          "expected_concepts": [
            "concept 1",
            "concept 2"
          ]
        }}
      ]
    }}
  ]
}}

---

IMPORTANT DESIGN RULES:

1. Every module MUST teach ONE clear idea
2. Every step MUST be small and easy to understand
3. Every step MUST include: speech, board, question
4. Use real-world examples and analogies wherever possible
5. AVOID complex academic language entirely
6. Keep steps short (micro-learning style)
7. Make learning progressive (easy → harder)
8. Generate as many modules as the topic requires — one module per subtopic
9. Do NOT artificially limit or pad the number of modules
10. Each module MUST have between 3 and 5 steps
11. Cover every major subtopic — do not skip or merge unrelated concepts
12. A simple topic may have 2–3 modules; a complex topic may have 10, 15, or more
13. NEVER stop generating modules just because you have reached 6 — that is NOT a limit
14. You MUST continue until EVERY distinct subtopic has its own module
15. Do NOT merge unrelated subtopics into one module to save space
16. Do NOT write a summary/wrap-up module — end when content is fully covered
17. If the topic is a full document or course material, expect 10+ modules

---

LANGUAGE LEVEL RULES (CRITICAL):

- Write speech at a Grade 8 reading level (age 13–14)
- Avoid: "Furthermore", "It is important to note", "In conclusion", "Pertaining to"
- Use instead: "Also", "Remember", "So basically", "Think of it like..."
- Board content items must be SHORT — max 8 words each
- Questions must be answerable in 1–3 sentences
- If explaining something complex, use an analogy first

---

BOARD USAGE RULES:

- hierarchy → concepts and their relationships
- flowchart → processes and flows
- table → comparisons (pair items: key, value, key, value...)
- bullet → simple listing of key points
- timeline → sequences or history
- formula → mathematical or structured logic
- comparison → differences between two ideas
- process → step-by-step actions

---

QUESTION DESIGN RULES:

- recall → simple memory check ("What is X?")
- explanation → student explains in own words ("Explain X in your own words")
- application → real-world usage ("Give an example of X in real life")
- multiple_choice → structured options (include 4 options in the text, e.g. "A) ... B) ... C) ... D) ...")
- true_false → simple verification ("True or false: X does Y")

---

OUTPUT NOW:
Return ONLY the JSON lesson.
"""
