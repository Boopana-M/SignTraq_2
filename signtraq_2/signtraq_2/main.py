import speech_recognition as sr
import cv2
import os
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

# Dictionary mapping keywords to video paths
video_dict = {
    "hello": "sign_videos/hello.mp4",
    "good morning": "sign_videos/good_morning.mp4",
    "how are you": "sign_videos/how_are_you.mp4",
    "had your food": "sign_videos/had_your_food.mp4",
    "i am a software engineer": "sign_videos/i_am_a_software_engineer.mp4",
    "i love my mother": "sign_videos/i_love_my_mother.mp4",
    "she is sleeping": "sign_videos/she_is_sleeping.mp4",
    
    "welcome": "sign_videos/welcome.mp4",
    "what are you doing": "sign_videos/what_are_you_doing.mp4",
}

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[Microphone Ready] Please speak now.")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Helps with background noise[6]
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)  # Prevents indefinite waiting[6]
    try:
        print("[Recognizing speech...]")
        text = recognizer.recognize_google(audio).lower()  # Uses free Google Web Speech API[5][7]
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
    except sr.RequestError:
        print("API unavailable or network error.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def play_video(video_path):
    if not os.path.exists(video_path):
        print("Video file not found:", video_path)
        return
    cap = cv2.VideoCapture(video_path)
    print("[Playing video]")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Sign Language Output', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def main():
    print("=== Voice to Sign Language Translator ===")
    input("Press Enter to turn on the microphone and start speaking...")
    spoken_text = recognize_speech_from_mic()
    if spoken_text:
        for keyword in video_dict:
            if keyword in spoken_text:
                play_video(video_dict[keyword])
                break
        else:
            print("No matching sign video found for:", spoken_text)

def converter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            spoken_text = data.get('spoken_text', '').lower()
            print(f"[DEBUG] Received spoken_text: {spoken_text}")
            video_path = None
            for keyword, path in video_dict.items():
                if keyword in spoken_text:
                    video_path = path
                    print(f"[DEBUG] Matched keyword: {keyword}, video_path: {video_path}")
                    break
            if video_path:
                return JsonResponse({'video_path': video_path})
            else:
                print("[DEBUG] No matching keyword found.")
                return JsonResponse({'video_path': None, 'message': 'dataset not found'})
        except Exception as e:
            import traceback
            print(f"[ERROR] Exception in converter view: {e}")
            traceback.print_exc()
            return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)
    return render(request, 'learninsilence_app/converter.html')

if __name__ == "__main__":
    main()
