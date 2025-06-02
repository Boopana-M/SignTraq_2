from django.shortcuts import render
from django.http import JsonResponse
import json
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import random
from django.db import connections # Import connections
from datetime import datetime # Import datetime

# Dictionary mapping keywords to video paths
video_dict = {
    "hello": "/static/sign_videos/hello.mp4",
    "good morning": "/static/sign_videos/good_morning.mp4",
    "how are you": "/static/sign_videos/how_are_you.mp4",
    "had your food": "/static/sign_videos/had_your_food.mp4",
    "i am a software engineer": "/static/sign_videos/i_am_a_software_engineer.mp4",
    "i love my mother": "/static/sign_videos/i_love_my_mother.mp4",
    "she is sleeping": "/static/sign_videos/she_is_sleeping.mp4",
    
    "welcome": "/static/sign_videos/welcome.mp4",
    "what are you doing": "/static/sign_videos/what_are_you_doing.mp4",
}

def home(request):
    return render(request, 'learninsilence_app/home.html')

def quiz(request):
    return render(request, 'learninsilence_app/quiz.html')

@csrf_exempt
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

def quiz_questions(request):
    """
    API endpoint to serve quiz questions as JSON.
    Each question: {image_url, correct_answer, options: [str, str, str, str]}
    """
    images_dir = os.path.join(settings.BASE_DIR, 'learninsilence_app', 'static', 'quiz images')
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    questions = []
    all_answers = [os.path.splitext(f)[0].replace('_', ' ').capitalize() for f in image_files]
    for img_file in image_files:
        correct_answer = os.path.splitext(img_file)[0].replace('_', ' ').capitalize()
        distractors = random.sample([a for a in all_answers if a != correct_answer], k=min(3, len(all_answers)-1))
        options = distractors + [correct_answer]
        random.shuffle(options)
        image_url = f"/static/quiz images/{img_file}"
        questions.append({
            'image_url': image_url,
            'correct_answer': correct_answer,
            'options': options
        })
    random.shuffle(questions)
    return JsonResponse({'questions': questions})

@csrf_exempt
def save_quiz_result(request):
    """
    API endpoint to receive and save quiz results to MongoDB.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = data.get('score')

            if score is not None:
                # --- MongoDB Saving Logic ----
                try:
                    # Access the MongoDB client via Django connections
                    client = connections['default'].client
                    db_name = settings.DATABASES['default']['NAME']
                    db = client[db_name]
                    
                    # Get or create the collection for quiz results
                    quiz_results_collection = db.quiz_results
                    
                    # Prepare the document to save
                    result_document = {
                        'score': score,
                        'timestamp': datetime.now() # Add a timestamp
                        # Add other relevant data here if needed (e.g., user ID if authenticated)
                    }
                    
                    # Insert the document into the collection
                    inserted_result = quiz_results_collection.insert_one(result_document)
                    print(f"Saved quiz result with ID: {inserted_result.inserted_id}")
                    
                    return JsonResponse({'status': 'success', 'message': 'Score saved'})
                except Exception as mongo_e:
                    print(f"[ERROR] MongoDB saving error: {mongo_e}")
                    return JsonResponse({'status': 'error', 'message': f'Failed to save score to database: {mongo_e}'}, status=500)
                # ------------------------------------------

            else:
                return JsonResponse({'status': 'error', 'message': 'Score not provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"[ERROR] General error in save_quiz_result: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)

