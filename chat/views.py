from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import StreamingHttpResponse

import my_settings
import openai
import json
import os


@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def post(self, request):
        openai.api_key = my_settings.API_KEY
        os.environ["OPENAI_API_KEY"] = my_settings.API_KEY

        # Parse the request body and extract the prompt
        prompt = json.loads(request.body)['content']

        # Define a generator function to stream the response
        def generate_response():
            for chunk in openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    stream=True,
            ):

                content = chunk["choices"][0].get("delta", {}).get("content")
                if content is not None:
                    yield content

        # Return a streaming response to the client
        return StreamingHttpResponse(generate_response(), content_type="application/octet-stream")

        # Return a JSON error if the request method is not POST
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

