from api.common_responses import success
import util.db as db


def update_story_images(query):
    story_id = query["id"]
    story = db.get_story_by_id(story_id)
    image_title = story["title"].replace("'","")
    story["imageUrl"] = f"https://backend.linguin.co/storage/v1/object/public/storyImages/{image_title}.gif"
    story["previewImageUrl"] = f"https://backend.linguin.co/storage/v1/object/public/storyImages/{image_title}_preview.gif"
    db.update_story(story)
    return success



def update_images_for_stories_without_images():
    stories = db.get_stories_done_without_images()
    for i, story in enumerate(stories):
        print(f"Updating Images {story['id']}; {i+1}/{len(stories)}")
        update_story_images({"id": story["id"]})
    return success