from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientForm
from .models import Patient

# Receptionist Page - Add New Patient
def receptionist_view(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('receptionist')
    else:
        form = PatientForm()
    return render(request, 'queueapp/receptionist.html', {'form': form})


# Doctor Panel - See details and mark patient as treated
def doctor_panel_view(request):
    patients = Patient.objects.filter(treated=False).order_by('-status', 'created_at')
    return render(request, 'queueapp/doctor_panel.html', {'patients': patients})

from django.shortcuts import get_object_or_404, redirect
from .models import Patient

def mark_patient_treated(request, patient_id):
    # Get the patient by ID or return 404 if not found
    patient = get_object_or_404(Patient, id=patient_id)

    # Mark the patient as treated
    patient.treated = True
    patient.save()

    # Redirect to the patient panel after marking treated
    return redirect('doctor_panel')  # Assuming 'patient_panel' is the name of your patient panel URL


from django.shortcuts import render
from .models import Patient

def patient_panel(request):
    # Fetch only patients who are NOT treated
    patients = Patient.objects.filter(treated=False)

    # Assign priority to each patient
    for patient in patients:
        patient.priority_score = get_patient_priority(patient)
    
    # Sort patients by priority and created_at (First Come First Serve)
    patients = sorted(
        patients, 
        key=lambda p: (p.priority_score, p.created_at)  # Sorting by priority, then by FCFS
    )

    return render(request, 'queueapp/patient_panel.html', {'patients': patients})

def get_patient_priority(patient):
    # Calculate the priority score
    if patient.status == 'Emergency':
        return 1
    elif patient.age > 55 or patient.age < 18:
        return 2
    return 3


import json
import requests
from django.http import JsonResponse

def chatbot_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        # Retrieve chat history from session, or start empty
        chat_history = request.session.get('chat_history', [])

        # Add the new user message to history
        chat_history.append({'role': 'user', 'content': user_message})

        # Keep only the last 5 messages
        chat_history = chat_history[-5:]

        # Create DeepSeek API payload
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "Reply in less than 20 words. Be very concise and clear."}
            ] + chat_history
        }

        # Call DeepSeek API
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': 'Bearer sk-9458b6f75df44a42920f3435d03e7423',
                'Content-Type': 'application/json',
            },
            json=payload
        )

        reply_data = response.json()
        bot_reply = reply_data['choices'][0]['message']['content']

        # Add the bot's reply to history
        chat_history.append({'role': 'assistant', 'content': bot_reply})
        chat_history = chat_history[-5:]  # Keep only last 5 again

        # Save updated history back to session
        request.session['chat_history'] = chat_history

        return JsonResponse({'reply': bot_reply})

