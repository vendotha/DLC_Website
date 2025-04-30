from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.core.cache import cache
from .forms import FeedbackForm
import google.generativeai as genai


def home(request):
    return render(request, 'digital_literacy/home.html')


def tutorials(request):
    return render(request, 'digital_literacy/tutorials.html')


def ai_chat(request):
    response = None
    error = None

    # Rate limiting
    if request.method == 'POST':
        user_ip = request.META.get('REMOTE_ADDR', 'unknown')
        cache_key = f"ai_chat_{user_ip}"
        request_count = cache.get(cache_key, 0)

        if request_count >= 5:  # Limit to 5 requests per minute
            error = "Please wait a minute before making more requests to DigiBuddy."
        else:
            cache.set(cache_key, request_count + 1, 60)  # 60 second timeout

            user_input = request.POST.get('user_input', '').strip()
            if user_input:
                try:
                    genai.configure(api_key='AIzaSyBbdJwZoupajYeM6q0I6V3B3acEOpZWdeA')
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    prompt = f"""
                    You are DigiBuddy, a friendly AI assistant helping elderly users with digital tools.
                    Respond in simple language with short sentences and clear steps.
                    If explaining an app feature, provide numbered instructions.
                    Always be patient and encouraging.

                    User question: {user_input}
                    """

                    response = model.generate_content(
                        prompt,
                        safety_settings={
                            'HARM_CATEGORY_HARASSMENT': 'BLOCK_ONLY_HIGH',
                            'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_ONLY_HIGH',
                            'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_ONLY_HIGH',
                            'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_ONLY_HIGH',
                        },
                        generation_config={
                            'max_output_tokens': 1000,
                            'temperature': 0.3,
                        }
                    )
                except Exception as e:
                    error = f"Sorry, DigiBuddy is having trouble right now. Please try again later. ({str(e)})"
            else:
                error = "Please enter a question for DigiBuddy."

    return render(request, 'digital_literacy/ai_chat.html', {
        'response': response.text if response else None,
        'error': error,
        'last_question': request.POST.get('user_input', '') if request.method == 'POST' else ''
    })


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'digital_literacy/feedback.html', {'submitted': True})
    else:
        form = FeedbackForm()
    return render(request, 'digital_literacy/feedback.html', {'form': form})