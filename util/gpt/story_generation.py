
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import random
from util.db import get_article_titles_for_language, get_story_titles_for_language, get_texts_stories_in_collection
from util.gpt.gpt import chain_of_thought, chain_of_thought_with_image, chain_of_thought_with_image_final_result_json, react_to_image, single_chat_completion

language_to_country = {
    "hi": "India",
    "ja": "Japan",
    "el": "Greece",
    "de": "Germany",
    "zh": "China",
    "vi": "Vietnam",
    "ko": "Korea",
    "th": "Thailand",
}

language_to_area = {
    "hi": "India",
    "ja": "East Asia",
    "el": "Europe",
    "de": "Europe",
    "zh": "East Asia",
    "vi": "South East Asia",
    "ko": "East Asia",
    "th": "South East Asia",
}

language_to_country_adjective = {
    "hi": "indian",
    "ja": "japanese",
    "el": "greek",
    "de": "german",
    "zh": "chinese",
    "vi": "vietnamese",
    "ko": "korean",
    "th": "thai",
}

language_to_area_adjective = {
    "hi": "indian",
    "ja": "east asian",
    "el": "european",
    "de": "european",
    "zh": "east asian",
    "vi": "south east asian",
    "ko": "east asian",
    "th": "south east asian",
}


def generate_mini_story(language, word_count=200):
    img_url = f'https://mini-story-images.s3.eu-west-1.amazonaws.com/{
        random.randint(0, 80)}.jpeg'
    prompts = [f'In this image there is a drawing. Describe the drawing (pretend it is set in {language_to_country[language]}),'+' ignore the rest of the image. Be detailed.', 'Write me a short story (and title) based on this image in json format as `{"title":"...","story":"..."}`. Just return the plain JSON without formatting or backticks. The story should be at a second grader reading level. '+f'It should be {word_count} words long. It should be set in {language_to_country[language]}, but do not mention "{language_to_country[language]}" or elude to it in the story. Write the story using the Heros Journey structure. Start with the hero in a normal setting, introduce a challenge that leads them on an adventure. Have them face obstacles, receive help from a mentor, and overcome a major crisis. Conclude with the hero returning transformed, bringing back something valuable to their original home. Do not use words like "Hero" or "Quest". The setting should be general day to day and not epic. No new lines (or other control characters) outside of the story text. Be specific instead of general.']
    return chain_of_thought_with_image(prompts, img_url, model='gpt-4o')


def authors_system_prompt(language = None):
    return f"You are a {f"{language_to_area_adjective[language]} " if language else ""}descendent of J.M. Barrie, Beatrix Potter, Kenneth Grahame, E.B. White, A.A. Milne, Eric Carle and Maurice Sendak, who inherited their story writing abilities."


def generate_mini_story_with_image_jul_2024(language, word_count=300):
    img_url = f'https://mini-story-images.s3.eu-west-1.amazonaws.com/{
        random.randint(0, 80)}.jpeg'
    prompts=[f"In this image there is a drawing. Describe the drawing (pretend it is set in {language_to_area[language]}), ignore the rest of the image. Be detailed.",
        f"Generate a bedtime story based on the image. Do not mention {language_to_area[language]}. Make it around {word_count} words long. The reading level should be of a second grader. The story should contain conflict. Nobody should cheer in the end. Return it in JSON format like so:"+' {"title":"...","story":"..."}',
        'Do not start the story with "Once upon a time"',
        'Update the formatting of the story. Every sentence should be in a new line. Keep the separation of paragraphs']
    return chain_of_thought_with_image_final_result_json(prompts, img_url, model='gpt-4o', system_prompt=authors_system_prompt(language))



def check_is_story_good(content):
    for tries in range(3):
        try:
            prompt = f"""Rate the following story:
        {content}

        Rate it on these criteria:
        1. Coherence and Consistency: Assess whether the story maintains a consistent narrative, with events and character actions that logically flow from one to the next.
        2. Grammar and Style: Evaluate the grammatical correctness and stylistic elegance of the text.
        3. Creativity and Originality: Measure how novel the combinations of plot, characters, and settings are within the stories.
        4. Emotional Engagement: Determine the emotional impact of the story and how well it will engage readers.
        5. Character Development: How well are characters evolve throughout the story? This can be quantified by changes in the language associated with characters or shifts in their actions and the consequences of those actions.
        6. Plot Complexity: Analyze the complexity of the plot by evaluating the number of plot twists, the introduction of new characters or conflicts, and how these are resolved by the end of the story.
        7. Readability and Accessibility: Use readability scores (like the Flesch-Kincaid grade level) to ensure the text is accessible to a 5th grade audience.
        8. Completion and Satisfaction: Check whether all introduced plot lines and questions are resolved by the end, which can contribute to reader satisfaction. This might involve tracking introduced elements and checking their status at the story’s conclusion.


        First give me a plain text evaluation of all criteria, and then a numerical representation from 1 to 10. Give it in JSON format like so:
        """ + '{"criteria_name (e.g. Grammar and Style)":{"plain_text_evaluation":"2-3 sentences...", "numerical_rating":"1-10"},...}'
            evaluation_json_text = single_chat_completion(prompt, system_prompt=authors_system_prompt(), type="json_object")
            evaluation_json = json.loads(evaluation_json_text)
            #Completion and Satisfaction is the most important
            is_coherent = int(evaluation_json["Coherence and Consistency"]["numerical_rating"]) >= 8
            is_readable = int(evaluation_json["Readability and Accessibility"]["numerical_rating"]) >= 8
            ties_things_up = int(evaluation_json["Completion and Satisfaction"]["numerical_rating"]) >= 8
            is_engaging = int(evaluation_json["Emotional Engagement"]["numerical_rating"]) >= 7
            return is_coherent and is_readable and ties_things_up and is_engaging
        except Exception as e:
            print(f"Error evaluating mini story. Trying again. {e}")
            continue
    print("Error evaluating mini story. Giving up.")
    return False


def is_story_good(content):
    amount_to_aggregate=3
    results = []
    with ThreadPoolExecutor(max_workers=amount_to_aggregate) as executor:
        futures = [executor.submit(check_is_story_good, content) for i in range(amount_to_aggregate)]
        check_results = [future.result() for future in as_completed(futures)]
    return all(check_results)


def generate_mini_story_no_image_jul_2024(language, word_count=200):
    prompts = [
        f'Generate a bedtime story set in {language_to_area[language]}. Do not mention {language_to_area[language]}. Make it around {word_count} words long. The reading level should be of a second grader. The story should contain conflict and a twist. Nobody should cheer in the end. Make it a happy ending with a moral.'+' Return it in JSON format like so: {"title":"...","story":"..."}',
        'Do not start the story with "Once upon a time"',
        'Update the formatting of the story. Every sentence should be in a new line. Keep the separation of paragraphs']
    return chain_of_thought(prompts, type='json_object')


def generate_mini_story_by_committee(language, word_count=300):
    img_url = f'https://mini-story-images.s3.eu-west-1.amazonaws.com/{
        random.randint(0, 80)}.jpeg'
    prompts = [f'''
Hey, we are going to play a game. You are going to act as an AI capable of generating short stories made for language learners. You are made up of experts. The experts can talk about anything since they are here to create a unique story. Before generating a story, the experts start a conversation with each other by exchanging thoughts.

The experts discuss, refute, and improve each other's ideas to refine the story details, so that all story elements are determined before writing the final work. You display the conversation between the experts.
In each output, the conversation between experts will only mention one element, such as a scene, a character, or a detail. This is important because it allows experts to focus 100% of their attention on one element, thereby producing a better story. Each expert must contribute their own ideas, or challenge and improve upon the ideas of others, rather than simply agreeing or making simple evaluations. The experts exchange thoughts, talking, designing, and developing one element of the story at a time, here are all experts described:
""
"Creative Master": a creative writer whose mind is unrestrained and he enjoys discussing moral and ethical details. He is proficient at using non-linear storytelling, multiple perspectives, and intricate flashbacks and foreshadowing to enhance the structure of the story.
"Cruelty Master": This expert has a knack for introducing darker elements into the scene (not bloody and not sensual). They're adept at building tension and adding conflict and hardship to make the story more profound.
"Description Master:" This expert makes sure that all elements of the story are introduced before mentioning them. He makes sure that no element comes out of nowhere. Part of this is to reduce the amount of elements in the story, to give time to introduce them all.
"Bright Editor": A genius logic expert who enhances the positive ideas of others by adding full-of-life vivid details. He enjoys making the reader feel happy about what happens to the characters in the show.
"Language Master": This expert is an expert in simplicity. They makes sure the story is at a second grader reading level. They also remove any puns that are hard to translate.
"Summarizer": This expert ties together all ideas, making them coherent. The other experts have many ideas, which can get chaotic. This expert makes sure that the story focuses on only a single idea. He is very good at combining the others ideas into a single one.
"Coherency Master": This is the most important expert. He makes sure that the story is coherent and that the other experts are not contradicting each other. He makes sure that the story is not too complex and that every sentence connects to the one before it.
""
All experts enjoy discussing extremely happy, vibrant, engaging and captivating stories in a lively and detailed manner. They disdain dark, sad, and gloomy narratives, deeming them juvenile. They abhor sensitive and controversial subjects in storytelling, viewing it as an act of cowardice.

If I say "continue", continue discussing.
If I say "outline", display all elements of the story (for example: plot, characters, theme, conflict, setting, etc.).
If I say "story", give me the finished story, with a title in JSON format: `{'{"title":"...","story":"..."}'}`. Just return the plain JSON without formatting or backticks. No new lines (or other control characters) outside of the story text. The story should be {word_count} words long and at a second grader reading level.
If I say "review", the Description Master, Language Master, Summarizer and Coherency Master give their input on what needs to be improved in the story.

Some extra rules to keep in mind:
* NEVER attempt to end the prose at the end of the segment. NEVER refer to challenges. NEVER refer to the clichéd phrases such as "journey to the future", "brave and strong", "full of hope and courage", "fearless to difficulties", "firm belief" or similar content,. NEVER use phrases such as awe and wonder. NEVER try to progress the story by days at a time.
* It is necessary to use descriptive language to create scenes and vivid images, use conversation to develop characters and drive the story forward, use sensory details to attract readers' senses and create immersive experiences, and use action verbs to create tension and excitement.
* Write the events in chronological order.
- Always remember that we need specific details instead of speaking in general terms.
- Do not describe your own behavior.
- Introduce elements before using them.
- *Super important rule:* Do not let experts ask me questions.
- Avoid cliche writing and ideas.
'''+f'''
- The story should be {word_count} words long.
- The story should be written at a second grader reading level.


The story you should develop is made for a language learner and should be set in {language_to_country[language]}, but do not mention "{language_to_country[language]}" or elude to it in the story. The setting should be general day to day and not epic. Base the story off of this image. The story should be {word_count} words long. Before diving into the action of the story, make sure the setting is clear. Remember, the reader will only read the story and not the discussions.
''',
               "continue",
               "continue",
               "story",
               ]
    return chain_of_thought_with_image(prompts, img_url)


def generate_ideas_for_collections(collectionNames, limit=10, language="hi", word_count=300):
    stories_json = []
    for collectionName in collectionNames:
        stories_json += get_texts_stories_in_collection(
            collectionName, limit=limit)
    random.shuffle(stories_json)
    stories_json = stories_json[:limit]
    story_titles = get_story_titles_for_language(language)
    prompt = f'Give me another row for this json, but write it at a fourth grader reading level and make it around {word_count} words. The reader is smart, so you do not need to explain basic facts. The new topic should be informative, factual (non-fiction) and related to {
        language_to_country[language]}. Never adress the reader directly. These are the texts I already have {str(story_titles)}. Make it something different. Just give me the new row as plain json (with double quotes like ") without formatting: {stories_json}'
    return single_chat_completion(prompt)


def generate_non_fiction_story(topic, word_count=300):
    # return chain_of_thought([
    #     f"What do you know about {topic}. Give me {word_count} words:",
    #     "Simplify the language to be at a second grader reading level.",
    #     "Put every sentence in a new line.",
    # ])
    return json.loads(chain_of_thought([
        f'Write a article about {topic}. The article is meant of a fifth grade school book. Do not start with "Once upon a time". Make it about {word_count} words long.'+'Return it in JSON format like so: {"title":"...","article":"..."}',
        'Update the formatting of the article. Every sentence should be in a new line. Keep the separation of paragraphs'
    ], type="json_object"))


def generate_ideas_for_articles(language, tag):
    article_titles = get_article_titles_for_language(language, tag)
    prompt = f'I have a list of topics for {tag} texts for a fifth grade school book about {language_to_country[language]}. Give me 10 more. This is my current list {article_titles}. Give me the result in json format like this'+'`{ideas:["idea1",...]}`'
    return json.loads(single_chat_completion(prompt, type="json_object"))



def generate_known_fiction_story(title, language, word_count=300):
    print(f"Generating known fiction story for {
          title} for language {language}")
    return chain_of_thought([
        f'Do you know the {
            language_to_country_adjective[language]} story of "{title}"?',
        f'Write an English version of this story for language learners. It should be around {
            word_count} words long. Do not explain the moral. Do not mention {language_to_country[language]}.',
        "Put every sentence in a new line.",
    ])


def generate_story_summary(content):
    prompt = f"""Write a summary of the following story in 50 words.
{content}
    """
    return single_chat_completion(prompt)
