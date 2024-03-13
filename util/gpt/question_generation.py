
from util.gpt.gpt import chat_completion
import json


def get_questions_for_story(story) -> list[dict]:
    prompt = '''Give me 10 multiple choice questions to this text. The questions should have 4 possible answers, 1 should be the correct one (mark this one with a *), 3 should be incorrect. The questions are intended to test the reading comprehension of an English language learner, so the answers should not be obvious. Return the questions in the following json format:
```
{"question":"...", "correctAnswer":"...", "otherOptions":["...", "...", "..."]}
```
Just return the plain JSON without formatting or backticks.
Here is the text:
"""
''' + story + '\n"""'
    return json.loads(chat_completion([{"role": "user", "content": prompt}]))