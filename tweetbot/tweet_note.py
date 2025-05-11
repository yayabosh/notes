import os
import io
import tweepy
import requests
import base64
from PIL import ImageGrab
from dotenv import load_dotenv
from io import BytesIO


# Load Twitter credentials from .env
load_dotenv()

# Set up Twitter client (v2)
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_SECRET")
)

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")

def upload_clipboard_image_to_imgur():
    img = ImageGrab.grabclipboard()
    if not img:
        return None

    # Convert image to base64 bytes so Imgur can handle it via HTTP POST
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    data = {"image": img_str, "type": "base64"}
    
    response = requests.post(
            "https://api.imgur.com/3/image",
            headers=headers,
            data=data
    )

    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        print("❌ Imgur upload failed: ", response.json())
        return None

def main():
    print("Choose Tweet type:")
    print("[c] Caption only")
    print("[i] Image + caption")

    choice = input("Enter c or i: ").strip().lower()
    
    caption = input("📝 Enter a caption for your Tweet "
                    "(or leave blank for no caption): ")

    match choice:
        # Just post the caption
        case "c":
            if caption:
                response = client.create_tweet(text=caption)
                print("✅ Text tweet posted successfully!")
                print(f"🔗 https://x.com/yayabosh/status/{response.data['id']}")

        case "i":
            print("📸 Uploading clipboard image to Imgur...")
            imgur_url = upload_clipboard_image_to_imgur()

            if not imgur_url:
                print("😵 No image found in clipboard or upload failed.")
                return

            tweet_text = f"{caption}\n{imgur_url}" if caption else imgur_url
            response = client.create_tweet(text=tweet_text)
            print("✅ Tweet with image link posted successfully!")
            print(f" https://x.com/me/status/{response.data['id']}")

        case _:
            print("❌ Invalid choice. Please select c or i.")


if __name__ == "__main__":
    main()
        
