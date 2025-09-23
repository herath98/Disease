from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import date

from django.contrib import messages
from django.contrib.auth.models import User , auth
from .models import patient , doctor , diseaseinfo , consultation ,rating_review,DiseaseForSuggestions
from chats.models import Chat,Feedback
import json
from django.shortcuts import render
import os

# Create your views here.


# loading trained_model safely: resolve path relative to project root and handle missing file
import joblib as jb
_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'trained_model')
model = None
try:
    if os.path.exists(_MODEL_PATH):
        model = jb.load(_MODEL_PATH)
    else:
        # fallback: try load by exact filename in case it's in working dir
        if os.path.exists('trained_model'):
            model = jb.load('trained_model')
        else:
            print(f"Warning: trained_model not found at {_MODEL_PATH} or './trained_model'. Model loading skipped.")
except Exception as e:
    # don't crash at import time; prediction code will handle model==None
    print(f"Error loading trained_model from {_MODEL_PATH}: {e}")




def home(request):

  if request.method == 'GET':
        
      if request.user.is_authenticated:
        return render(request,'homepage/index.html')

      else :
        return render(request,'homepage/index.html')

def admin_ui(request):

    if request.method == 'GET':

      if request.user.is_authenticated:

        auser = request.user
        Feedbackobj = Feedback.objects.all()

        return render(request,'admin/admin_ui/admin_ui.html' , {"auser":auser,"Feedback":Feedbackobj})

      else :
        return redirect('home')



    if request.method == 'POST':

       return render(request,'patient/patient_ui/profile.html')





def patient_ui(request):

    if request.method == 'GET':

      if request.user.is_authenticated:

        patientusername = request.session['patientusername']
        puser = User.objects.get(username=patientusername)

        return render(request,'patient/patient_ui/profile.html' , {"puser":puser})

      else :
        return redirect('home')



    if request.method == 'POST':

       return render(request,'patient/patient_ui/profile.html')

       


def pviewprofile(request, patientusername):

    if request.method == 'GET':

          puser = User.objects.get(username=patientusername)

          return render(request,'patient/view_profile/view_profile.html', {"puser":puser})




class DiseasePredictionSystem:
    def __init__(self,json_file_path = os.path.join(os.path.dirname(__file__), 'data', 'disease_suggestions.json')):
        self.diseaselist = [
            'Fungal infection', 'Allergy', 'GERD', 'Chronic cholestasis', 'Drug Reaction',
            'Peptic ulcer diseae', 'AIDS', 'Diabetes', 'Gastroenteritis', 'Bronchial Asthma',
            'Hypertension', 'Migraine', 'Cervical spondylosis', 'Paralysis (brain hemorrhage)',
            'Jaundice', 'Malaria', 'Chicken pox', 'Dengue', 'Typhoid', 'hepatitis A',
            'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Hepatitis E', 'Alcoholic hepatitis',
            'Tuberculosis', 'Common Cold', 'Pneumonia', 'Dimorphic hemmorhoids(piles)',
            'Heart attack', 'Varicose veins', 'Hypothyroidism', 'Hyperthyroidism',
            'Hypoglycemia', 'Osteoarthristis', 'Arthritis',
            '(vertigo) Paroymsal Positional Vertigo', 'Acne', 'Urinary tract infection',
            'Psoriasis', 'Impetigo'
        ]

        self.symptomslist = [
            'itching', 'skin_rash', 'nodal_skin_eruptions', 'continuous_sneezing', 'shivering',
            'chills', 'joint_pain', 'stomach_pain', 'acidity', 'ulcers_on_tongue',
            'muscle_wasting', 'vomiting', 'burning_micturition', 'spotting_urination',
            'fatigue', 'weight_gain', 'anxiety', 'cold_hands_and_feets', 'mood_swings',
            'weight_loss', 'restlessness', 'lethargy', 'patches_in_throat',
            'irregular_sugar_level', 'cough', 'high_fever', 'sunken_eyes', 'breathlessness',
            'sweating', 'dehydration', 'indigestion', 'headache', 'yellowish_skin',
            'dark_urine', 'nausea', 'loss_of_appetite', 'pain_behind_the_eyes', 'back_pain',
            'constipation', 'abdominal_pain', 'diarrhoea', 'mild_fever', 'yellow_urine',
            'yellowing_of_eyes', 'acute_liver_failure', 'fluid_overload',
            'swelling_of_stomach', 'swelled_lymph_nodes', 'malaise',
            'blurred_and_distorted_vision', 'phlegm', 'throat_irritation', 'redness_of_eyes',
            'sinus_pressure', 'runny_nose', 'congestion', 'chest_pain', 'weakness_in_limbs',
            'fast_heart_rate', 'pain_during_bowel_movements', 'pain_in_anal_region',
            'bloody_stool', 'irritation_in_anus', 'neck_pain', 'dizziness', 'cramps',
            'bruising', 'obesity', 'swollen_legs', 'swollen_blood_vessels',
            'puffy_face_and_eyes', 'enlarged_thyroid', 'brittle_nails', 'swollen_extremeties',
            'excessive_hunger', 'extra_marital_contacts', 'drying_and_tingling_lips',
            'slurred_speech', 'knee_pain', 'hip_joint_pain', 'muscle_weakness', 'stiff_neck',
            'swelling_joints', 'movement_stiffness', 'spinning_movements', 'loss_of_balance',
            'unsteadiness', 'weakness_of_one_body_side', 'loss_of_smell', 'bladder_discomfort',
            'foul_smell_of_urine', 'continuous_feel_of_urine', 'passage_of_gases',
            'internal_itching', 'toxic_look_(typhos)', 'depression', 'irritability',
            'muscle_pain', 'altered_sensorium', 'red_spots_over_body', 'belly_pain',
            'abnormal_menstruation', 'dischromic_patches', 'watering_from_eyes',
            'increased_appetite', 'polyuria', 'family_history', 'mucoid_sputum',
            'rusty_sputum', 'lack_of_concentration', 'visual_disturbances',
            'receiving_blood_transfusion', 'receiving_unsterile_injections', 'coma',
            'stomach_bleeding', 'distention_of_abdomen', 'history_of_alcohol_consumption',
            'fluid_overload', 'blood_in_sputum', 'prominent_veins_on_calf', 'palpitations',
            'painful_walking', 'pus_filled_pimples', 'blackheads', 'scurring', 'skin_peeling',
            'silver_like_dusting', 'small_dents_in_nails', 'inflammatory_nails', 'blister',
            'red_sore_around_nose', 'yellow_crust_ooze'
        ]

        self.disease_suggestions = self.load_disease_suggestions(json_file_path)
       
        self.doctor_specializations = {
            'Rheumatologist': ['Osteoarthristis', 'Arthritis'],
            'Cardiologist': ['Heart attack', 'Bronchial Asthma', 'Hypertension'],
            'ENT specialist': ['(vertigo) Paroymsal Positional Vertigo', 'Hypothyroidism'],
            'Neurologist': [
                'Varicose veins', 'Paralysis (brain hemorrhage)', 'Migraine',
                'Cervical spondylosis'
            ],
            'Allergist/Immunologist': [
                'Allergy', 'Pneumonia', 'AIDS', 'Common Cold', 'Tuberculosis',
                'Malaria', 'Dengue', 'Typhoid'
            ],
            'Urologist': ['Urinary tract infection', 'Dimorphic hemmorhoids(piles)'],
            'Dermatologist': [
                'Acne', 'Chicken pox', 'Fungal infection', 'Psoriasis', 'Impetigo'
            ],
            'Gastroenterologist': [
                'Peptic ulcer diseae', 'GERD', 'Chronic cholestasis', 'Drug Reaction',
                'Gastroenteritis', 'Hepatitis E', 'Alcoholic hepatitis', 'Jaundice',
                'hepatitis A', 'Hepatitis B', 'Hepatitis C', 'Hepatitis D', 'Diabetes',
                'Hypoglycemia'
            ]
        }
    def load_disease_suggestions(self, json_file_path):
        """
        Load disease suggestions from a JSON file.
        
        Args:
            json_file_path (str): Path to the JSON file containing disease suggestions
            
        Returns:
            dict: Dictionary containing disease suggestions, or empty dict if file not found
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Warning: Disease suggestions file not found at {json_file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {json_file_path}")
            return {}
        except Exception as e:
            print(f"Error loading disease suggestions: {str(e)}")
            return {}
    

    def get_symptoms_vector(self, selected_symptoms):
        """Convert selected symptoms to binary vector."""
        return [1 if symptom in selected_symptoms else 0 for symptom in self.symptomslist]

    def predict_disease(self, symptoms_vector):
        """Predict disease based on symptoms vector."""
        try:
            prediction = model.predict([symptoms_vector])[0]
            probabilities = model.predict_proba([symptoms_vector])
            confidence = format(probabilities.max() * 100, '.0f')
            return prediction, confidence
        except Exception as e:
            print(f"Error in disease prediction: {str(e)}")
            return None, 0

    def get_doctor_specialization(self, disease):
        """Get the appropriate doctor specialization for the disease."""
        for specialization, diseases in self.doctor_specializations.items():
            if disease in diseases:
                return specialization
        return "General Physician"

    def get_disease_suggestions(self, disease):
        """Get suggestions for the predicted disease."""
        return self.disease_suggestions.get(disease, {
            'good_habits': ['Consult a healthcare provider for specific recommendations'],
            'good_foods': ['Consult a nutritionist for personalized diet advice'],
            'notgoodfoods': ['Avoid any foods that cause discomfort']
        })

def checkdisease(request):
    """Main view function for disease prediction."""
    dps = DiseasePredictionSystem()
    
    if request.method == 'GET':
        return render(request, 'patient/checkdisease/checkdisease.html', {
            "list2": sorted(dps.symptomslist)
        })
    
    elif request.method == 'POST':
        try:
            # Get number of symptoms
            inputno = int(request.POST.get("noofsym", 0))
            
            if inputno == 0:
                return JsonResponse({
                    'predicteddisease': "none",
                    'confidencescore': 0,
                    'suggestions': None,
                    'consultdoctor': None
                })

            # Get selected symptoms
            selected_symptoms = request.POST.getlist("symptoms[]")
            
            # Generate symptoms vector and predict disease
            symptoms_vector = dps.get_symptoms_vector(selected_symptoms)
            predicted_disease, confidence_score = dps.predict_disease(symptoms_vector)
            print(predicted_disease)
            
            if predicted_disease is None:
                return JsonResponse({
                    'error': 'Prediction failed',
                    'predicteddisease': "none",
                    'confidencescore': 0
                })

            # Get doctor specialization and suggestions
            consultant_doctor = dps.get_doctor_specialization(predicted_disease)
            suggestions = dps.get_disease_suggestions(predicted_disease)
            
            
          
            # Save to database
            save_disease_info(
                request=request,
                predicted_disease=predicted_disease,
                input_symptoms_count=inputno,
                symptoms=selected_symptoms,
                confidence_score=confidence_score,
                consultant_doctor=consultant_doctor
            )

            return JsonResponse({
                'predicteddisease': predicted_disease,
                'confidencescore': confidence_score,
                'consultdoctor': consultant_doctor,
                'suggestions': suggestions
            })

        except Exception as e:
            print(f"Error in disease prediction view: {str(e)}")
            return JsonResponse({
                'error': 'An error occurred',
                'predicteddisease': "none",
                'confidencescore': 0
            })

def save_disease_info(request, predicted_disease, input_symptoms_count, symptoms, 
                     confidence_score, consultant_doctor):
    """Save the disease diagnosis information to the database."""
    try:
        patient = User.objects.get(username=request.session['patientusername']).patient
        
        disease_info = diseaseinfo.objects.create(
            patient=patient,
            diseasename=predicted_disease,
            no_of_symp=input_symptoms_count,
            symptomsname=symptoms,
            confidence=confidence_score,
            consultdoctor=consultant_doctor
        )
        
        request.session['diseaseinfo_id'] = disease_info.id
        request.session['doctortype'] = consultant_doctor
        
        return True
    except Exception as e:
        print(f"Error saving disease info: {str(e)}")
        return False

# def populate_disease_suggestions():
#     """Populate the database with disease suggestions."""
#     dps = DiseasePredictionSystem()
    
#     for disease, suggestions in dps.disease_suggestions.items():
#         try:
#             DiseaseForSuggestions.objects.get_or_create(
#                 disease=disease,
#                 defaults={
#                     'good_habits': suggestions['good_habits'],
#                     'good_foods': suggestions['good_foods'],
#                     'notgoodfoods': suggestions['notgoodfoods']
#                 }
#             )
#         except Exception as e:
#             print(f"Error populating suggestions for {disease}: {str(e)}")


   





def pconsultation_history(request):

    if request.method == 'GET':

      patientusername = request.session['patientusername']
      puser = User.objects.get(username=patientusername)
      patient_obj = puser.patient
        
      consultationnew = consultation.objects.filter(patient = patient_obj)
      
    
      return render(request,'patient/consultation_history/consultation_history.html',{"consultation":consultationnew})


def dconsultation_history(request):

    if request.method == 'GET':

      doctorusername = request.session['doctorusername']
      duser = User.objects.get(username=doctorusername)
      doctor_obj = duser.doctor
        
      consultationnew = consultation.objects.filter(doctor = doctor_obj)
      
    
      return render(request,'doctor/consultation_history/consultation_history.html',{"consultation":consultationnew})



def doctor_ui(request):

    if request.method == 'GET':

      doctorid = request.session['doctorusername']
      duser = User.objects.get(username=doctorid)

    
      return render(request,'doctor/doctor_ui/profile.html',{"duser":duser})



      


def dviewprofile(request, doctorusername):

    if request.method == 'GET':

         
         duser = User.objects.get(username=doctorusername)
         r = rating_review.objects.filter(doctor=duser.doctor)
       
         return render(request,'doctor/view_profile/view_profile.html', {"duser":duser, "rate":r} )








       
def  consult_a_doctor(request):


    if request.method == 'GET':

        
        doctortype = request.session['doctortype']
        print(doctortype)
        dobj = doctor.objects.all()
        #dobj = doctor.objects.filter(specialization=doctortype)


        return render(request,'patient/consult_a_doctor/consult_a_doctor.html',{"dobj":dobj})

   


def  make_consultation(request, doctorusername):

    if request.method == 'POST':
       

        patientusername = request.session['patientusername']
        puser = User.objects.get(username=patientusername)
        patient_obj = puser.patient
        
        
        #doctorusername = request.session['doctorusername']
        duser = User.objects.get(username=doctorusername)
        doctor_obj = duser.doctor
        request.session['doctorusername'] = doctorusername


        diseaseinfo_id = request.session['diseaseinfo_id']
        diseaseinfo_obj = diseaseinfo.objects.get(id=diseaseinfo_id)

        consultation_date = date.today()
        status = "active"
        
        consultation_new = consultation( patient=patient_obj, doctor=doctor_obj, diseaseinfo=diseaseinfo_obj, consultation_date=consultation_date,status=status)
        consultation_new.save()

        request.session['consultation_id'] = consultation_new.id

        print("consultation record is saved sucessfully.............................")

         
        return redirect('consultationview',consultation_new.id)



def  consultationview(request,consultation_id):
   
    if request.method == 'GET':

   
      request.session['consultation_id'] = consultation_id
      consultation_obj = consultation.objects.get(id=consultation_id)

      return render(request,'consultation/consultation.html', {"consultation":consultation_obj })

   #  if request.method == 'POST':
   #    return render(request,'consultation/consultation.html' )





def rate_review(request,consultation_id):
   if request.method == "POST":
         
         consultation_obj = consultation.objects.get(id=consultation_id)
         patient = consultation_obj.patient
         doctor1 = consultation_obj.doctor
         rating = request.POST.get('rating')
         review = request.POST.get('review')

         rating_obj = rating_review(patient=patient,doctor=doctor1,rating=rating,review=review)
         rating_obj.save()

         rate = int(rating_obj.rating_is)
         doctor.objects.filter(pk=doctor1).update(rating=rate)
         

         return redirect('consultationview',consultation_id)





def close_consultation(request,consultation_id):
   if request.method == "POST":
         
         consultation.objects.filter(pk=consultation_id).update(status="closed")
         
         return redirect('home')






#-----------------------------chatting system ---------------------------------------------------


def post(request):
    if request.method == "POST":
        msg = request.POST.get('msgbox', None)

        consultation_id = request.session['consultation_id'] 
        consultation_obj = consultation.objects.get(id=consultation_id)

        c = Chat(consultation_id=consultation_obj,sender=request.user, message=msg)

        #msg = c.user.username+": "+msg

        if msg != '':            
            c.save()
            print("msg saved"+ msg )
            return JsonResponse({ 'msg': msg })
    else:
        return HttpResponse('Request must be POST.')

def chat_messages(request):
   if request.method == "GET":

         consultation_id = request.session['consultation_id'] 

         c = Chat.objects.filter(consultation_id=consultation_id)
         return render(request, 'consultation/chat_body.html', {'chat': c},context)


#-----------------------------chatting system ---------------------------------------------------


