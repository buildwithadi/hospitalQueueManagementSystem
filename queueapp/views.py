from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientForm
from .models import Patient

def frontpage_view(request):
    return render(request, 'queueapp/frontpage.html')
# queueapp/views.py

def know_more_view(request):
    return render(request, 'queueapp/knowmore.html')
    

def specialities_view(request):
    return render(request, 'queueapp/specialities.html') 

def academics_view(request):
    return render(request, 'queueapp/academics.html')

def doctors_view(request):
    return render(request, 'queueapp/doctors.html')
# Receptionist Page - Add New Patient
def receptionist_view(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('receptionist')
    else:
        initial_data = {}
        status = request.GET.get('status')
        issue = request.GET.get('issue')
        if status:
            initial_data['status'] = status 
        if issue:
            initial_data['issue'] = issue # prefill status field

        form = PatientForm(initial=initial_data)
    return render(request, 'queueapp/receptionist.html', {'form': form})


# Doctor Panel - See details and mark patient as treated
from .models import Patient
 # assuming your priority logic is here

def doctor_panel_view(request):
    patients = Patient.objects.all().order_by('created_at')  # ensure earliest first

    # Annotate priority
    for patient in patients:
        patient.priority_score = get_patient_priority(patient)

    # Sort by priority first, then arrival time
    patients = sorted(patients, key=lambda p: (p.priority_score, p.created_at))

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

# queueapp/utils.py
def get_patient_priority(patient):
    score = 0

    # 1. Emergency first
    if patient.status == 'Emergency':
        score += 0
    else:
        score += 10

    # 2. Age
    if patient.age <= 1:
        score += 2
    elif 1 < patient.age <= 5:
        score += 4
    elif 6 <= patient.age <= 12:
        score += 6
    elif 13 <= patient.age <= 18:
        score += 8
    elif 19 <= patient.age <= 35:
        score += 12
    elif 36 <= patient.age <= 50:
        score += 10
    elif 51 <= patient.age <= 65:
        score += 6
    else:
        score += 3

    # 3. Issue
    issue_severity = {
        'Fever': 8,
        'Headache': 10,
        'Migraine': 7,
        'Typhoid': 3,
        'Diarrhea': 6,
        'Jaundice': 4,
        'Other': 9
    }
    score += issue_severity.get(patient.issue, 10)

    # 4. Gender and condition modifiers
    if patient.gender == 'Female' and patient.issue in ['Migraine', 'Fever']:
        score -= 1
    if patient.gender == 'Male' and patient.issue == 'Jaundice':
        score -= 1

    # 5. Blood group rarity
    if patient.blood_group in ['AB-', 'B-', 'O-']:
        score -= 1

    # 6. Compound risk
    if patient.status == 'Emergency' and patient.age < 5 and patient.issue in ['Typhoid', 'Diarrhea']:
        score -= 2
    if patient.status == 'Emergency' and patient.age > 60 and patient.issue in ['Jaundice', 'Fever']:
        score -= 2

    if patient.issue in ['Headache', 'Migraine'] and patient.age > 60:
        score -= 1

    # 7. Clamp to 1–50
    return max(1, min(score, 50))



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

