import pytest
from util.gpt.story_generation import evaluate_mini_story, evaluation_min_value, is_story_good

@pytest.mark.parametrize("story", [
"""Once upon a time, in a quiet pond, lived a brave little frog named Freddy. Freddy loved to explore new places. One day, he saw the tallest cliff he had ever seen.'I’m going to climb that cliff!' he told his friends, Lilly, Tommy, and Sammy.

Lilly, Tommy, and Sammy jumped to the edge of the cliff to watch Freddy. They were worried, but also curious. Freddy began his climb. He used his strong legs to push himself up and grabbed onto the rocks with his sticky feet. The cliff was steep and very tough to climb.His legs started to hurt, and his feet were slipping on the rough surface. Freddy's heart pounded. He looked down and saw Lilly, Tommy, and Sammy watching him closely. 

Freddy took a deep breath. 'I can do this,' he whispered to himself. Freddy focused and tried even harder. Slowly and carefully, he climbed higher and higher. But the cliff remained steep and difficult. Near the top, Freddy was so tired. He didn’t know if he could make it.

Then, without saying a word, Lilly, Tommy, and Sammy jumped down to help their friend. They gently guided Freddy back to the safety of the pond. 'We’re glad you’re safe,' they said. Freddy smiled. He had tried his best, and that was enough. They all sat by the pond, happy to be together.""",

"""In a cozy little house, lived a kind lady named Clara. 
She always helped everyone in the village. 
One sunny morning, a young girl named Lucy came to Clara, looking very upset. 
'What’s wrong, Lucy?' Clara asked with a gentle smile. 
'I lost my magic comb,' Lucy said with teary eyes. 
'It always made my hair shine and now I can't find it anywhere.'

Clara patted Lucy on the shoulder. 
'Don’t worry, we will find it together,' she said. 
They looked all around Lucy's house, under her bed, and even in the garden. 
But the comb was nowhere to be found. 
Lucy started to cry. 
Clara thought for a moment and said, 'Lucy, sometimes we have to let go of things we love. 
But that doesn’t mean we can’t find new magic.'

Just then, Lucy remembered where she had left her comb. 
She hurried back to her room and found it hidden under her pillow. 
She was happy and thankful to Clara. 
Clara smiled and said, 'See, Lucy, sometimes the magic is just hiding.' 
They shared a hug, and Lucy felt better. 
But she knew she had to be more careful with her special things."""
])
def test_good_story(story):
    # Test for a high bar
    assert any([is_story_good(story) for _ in range(5)])




@pytest.mark.parametrize("story", [
"""Once upon a time in a small village, there lived a noble who wore fancy clothes. He had a blue tunic with golden designs and a red hat with a shiny gold piece on it. One day, a humble farmer came to see the noble. The farmer wore simple robes and walked barefoot. He carried a small sack in his hand. The farmer hoped the noble would accept the sack as a gift, for inside were the last of his precious seeds. These seeds were very important to him because he needed them to plant food for his family. 

The noble looked at the farmer and the small sack. He thought for a moment, tapping his mouth with one hand. The noble wasn’t sure if he should help the farmer or keep the seeds for himself. The farmer, kneeling with respect, feared what the noble might decide. His family depended on these seeds to eat. 

The noble finally spoke, but his words were not kind. He decided to keep the seeds, leaving the farmer in worry and sadness. The farmer walked back to his family, unsure how they would survive the upcoming season. The sky above seemed to reflect the sadness in the farmer's heart.""",
"""Leo loved adventure and wore his favorite yellow shirt every day. One sunny afternoon, he found an envelope in his mailbox. The envelope had no name and looked very old.

Curious, Leo opened it. The letter inside said, 'Meet me at the old tree house. It's urgent!' Leo felt worried and confused. Who could have sent such a message?

He decided to go to the tree house to find out. When he got there, he saw a small, dusty box. Carefully, he opened it and found another letter. This one was from his friend Mia. Mia wrote that she needed help because her favorite pet bird was missing.

Leo felt sad for Mia. He knew how much she loved her pet. But it was getting dark, and the woods looked scary at night. Leo needed to go back home and make a plan to help Mia in the morning.

As he lay in bed, Leo couldn't stop thinking about the mysterious letter and Mia's lost bird. He hoped they could solve the mystery together.""",
"""Leo lived in a cozy village and spent most of his days playing in the fields. One sunny morning, he received a letter. He looked worried as he held it tightly in his hand.

Leo had never received a letter before. He quickly ran to his room and opened it. The letter said, 'Meet me at the old oak tree at sunset. Important.'

Leo's heart raced. He thought, 'Who could have sent this? What do they want?' He decided to go, even though he was nervous.

As the sun began to set, Leo reached the old oak tree. There, under the tree, stood an elderly man with a long grey beard. He looked kind but serious.

'Hello, Leo,' the old man said. 'I need your help. A special book has gone missing from the village library. You are the only one who can find it.'

Leo was confused. 'Me? But why?' he asked.

'You have a good heart and keen eyes,' the old man replied. 'Will you help me?'

Leo took a deep breath and nodded. He knew it wouldn't be easy, but he decided to try his best. And so, Leo's adventure began, with the old man's words echoing in his mind. He hoped he could find the missing book and bring it back to the village."""
])
def test_bad_story(story):
    # Test for a high bar
    assert all([not is_story_good(story) for _ in range(5)])