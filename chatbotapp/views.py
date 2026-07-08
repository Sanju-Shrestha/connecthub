from django.shortcuts import redirect, render
from django.contrib import messages
from connecthub.settings import GENERATIVE_AI_KEY
from chatbotapp.models import ChatMessage
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

def send_message(request):
    if request.method == 'POST':
        genai.configure(api_key=GENERATIVE_AI_KEY)
        model = genai.GenerativeModel("gemini-3.5-flash")

        user_message = request.POST.get('user_message')

        try:
            bot_response = model.generate_content(user_message)
            ChatMessage.objects.create(user_message=user_message, bot_response=bot_response.text)
        except ResourceExhausted:
            messages.error(request, "The AI server is currently exhausted. Please wait a moment and try again.")
        except Exception as e:
            messages.error(request, f"An unexpected error occured: {str(e)}")

    return redirect('list_messages')


def list_messages(request):
    message_list = ChatMessage.objects.all()
    return render(request, 'chatbot/list_messages.html', {'messages': message_list})