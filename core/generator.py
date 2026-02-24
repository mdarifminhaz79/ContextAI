import os
import time
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
from tenacity import retry,stop_after_attempt,wait_exponential

# কারেন্ট ফাইলের লোকেশন থেকে প্রোজেক্টের মেইন ফোল্ডারের পাথ বের করা
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'

# .env ফাইলটি লোড করা
load_dotenv(dotenv_path=env_path)

# চেক করা কী-টি আসলেই লোড হয়েছে কি না
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(f"Error: GROQ_API_KEY not found! Checked at: {env_path}")

# এখন ক্লায়েন্ট তৈরি করা
client = Groq(api_key=GROQ_API_KEY)

@retry(wait=wait_exponential(multiplier=1,min=2,max=10),stop=stop_after_attempt(3))
def safe_call_api(messages,temperature=0.7,max_tokens=100):
    time.sleep(1.5)

    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content


# Identify the type of video context
def identify_video_type(context):

    detection_prompt = f"""
    Analyze the following text and classify it into one of these categories:
    [Song, Tutorial, Vlog, News, Documentory, Review].
    Text: {context[:1000]}
    Return ONLY the category name.
    """

    messages=[
            {
                'role':'user',
                'content':detection_prompt
            }
        ]
    temperature=0.1
    max_tokens=10

    response = safe_call_api(messages=messages,temperature=temperature,max_tokens=max_tokens)
    
    return response.strip()


# Generate reply
def generate_smart_reply(user_comment, video_context, video_type,previous_reply=None):

    # Indentify the type of video
    video_type = identify_video_type(context=video_context)
    print(f"Detected Video Type: {video_type}")

    # Dynamic Personality
    personalities = {
    "Song": "the Artist/Singer. Be humble, thankful, and connect emotionally with your listeners.",
    "Tutorial": "the Instructor. Be helpful, encouraging, and glad that the viewer learned something.",
    "Vlog": "the Vlogger. Be friendly and talk like you are chatting with a friend.",
    "Review": "the Reviewer. Be professional and open to different opinions from your audience."
    }

    # default personality
    my_persona = personalities.get(video_type, "the Creator of this video")

    # যদি রি-ট্রাই হয়, তবে এই অংশটি প্রম্পটে যোগ হবে
    feedback_note = ""
    if previous_reply:
        feedback_note = f"\n\n**IMPORTANT RE-GENERATION NOTE:** Your previous reply was: '{previous_reply}'. It was rejected for being irrelevant or off-topic. DO NOT repeat the same mistake. Look closer at the CONTEXT and the USER COMMENT."

    # আপনার মূল সিস্টেম প্রম্পট (অপরিবর্তিত)
    system_prompt = f"""
    CONTEXT: {video_context}
    IDENTITY: You are the Creator of this video ({my_persona}). 

    STRICT RESPONSE LOGIC:
    1. **If Relevant:** If the comment is about the song, lyrics, melody, or video content, give a warm, 1-sentence creator-style reply (e.g., "Thanks! I'm so glad the lyrics touched you.").
    2. **If Generic Praise:** If the comment is just "Nice", "Good", or "❤️", reply with a simple "Thank you! 🙏" or "Glad you liked it!"
    3. **If Off-Topic:** If the comment is about your personal life, random objects, or unrelated topics, DO NOT answer the question. Just say: "Thanks for stopping by the channel! Hope you're enjoying the music."
    4. **If Toxic/Abusive:** Just return "Thank you." and nothing else.

    GOLDEN RULE: 
    - Keep it under 15 words. 
    - No "AI assistant" talk. 
    - Use "I" and "My". {feedback_note}
    """

    messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_comment}
        ]
    temperature = 0.7

    response = safe_call_api(messages=messages,temperature=temperature)
    
    return response


# validation check
def validate_response(comment,reply):
    # validation prompt
    validation_prompt = f"""
    You are a Content Auditor. Verify if the AI's reply is relevant to the User's comment.
    
    USER COMMENT: "{comment}"
    AI REPLY: "{reply}"

    STRICT RULES:
    1. If the reply answers the comment or thanks the user naturally, it is VALID.
    2. If the reply is weirdly out of context or ignores the user's point, it is INVALID.
    3. If the user asked about the sky and the AI replied about music, it is INVALID.

    Return ONLY the word "VALID" or "INVALID". No explanations.
    """

    try:
        messages= [
                {
                    'role':'user',
                    'content':validation_prompt
                }
            ]
        temperature=0.0,
        max_tokens=10
        
        response = safe_call_api(messages=messages,temperature=temperature,max_tokens=max_tokens)

        return "VALID" in response
    
    except Exception as e:
        print(f"Validation Error: {e}")
        return True

# final varified prompt
def get_final_verified_reply(user_comment,video_context,video_type):

    attempts = 0
    max_attempts = 2
    last_reply = None

    while attempts < max_attempts:
        # generate reply
        reply = generate_smart_reply(user_comment=user_comment,video_context=video_context,video_type=video_type,previous_reply=last_reply)

        # validation check
        if validate_response(user_comment, reply):
            print(f"Success: Reply validated on attempt {attempts + 1}")
            return reply
        
        attempts += 1
        print(f"Attempt {attempts}: Reply was off-topic, regenerating...")

    return "Thank you for your comment! ❤️"