from openai import OpenAI
client = OpenAI()


def get_img_url_fiction(text):
    prompt = f"""Generate a single illustration, that captures the most important scene of the following fable in a flat, colorful style. Make the shapes clear and the content simple. The image should contain at most 3 characters. All characters should look friendly:
{text}
Style: flat, colorful"""
    return dalle3_image_url(prompt)


def get_img_url_non_fiction(text):
    prompt = f"""Generate a title image for the following text. Generate a single illustration, that captures the most important part of the text, in a flat, colorful style. Make the shapes clear and the content simple:
{text}
Style: flat, colorful"""
    return dalle3_image_url(prompt)


def dalle3_image_url(prompt, tries=0):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        if "content_policy_violation" in str(e) and tries < 5:
            print("Content policy violation. Trying again.")
            return dalle3_image_url(prompt, tries+1)
        else:
            raise e
