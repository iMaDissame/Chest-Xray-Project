# Update the permission classes and authentication methods
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth import authenticate, login,logout
from django.conf import settings
import numpy as np
import datetime
from docx import Document
import os
import random
import openai
from .serializers import UserSerializer, DoctorInfoSerializer, DocumentModelSerializer
from .models import DocumentModel, DoctorsInfo
from .apps import RadiologyConfig
from keras.src.utils import image_utils
from django.core.files.storage import FileSystemStorage

# Remove token-based authentication
@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    if request.method == 'POST':
        uname = request.data.get('username')
        email = request.data.get('email')
        pass1 = request.data.get('password')
        pass2 = request.data.get('password2')
        
        if not all([uname, email, pass1, pass2]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        if pass1 != pass2:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Check if username exists
        if User.objects.filter(username=uname).exists():
            return Response({'error': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(uname, email, pass1)
            return Response({
                'success': True,
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])  # Simplified - removed csrf_exempt
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)  # Create a session
        
        # Return credentials that can be stored and used by the app
        return Response({
            'success': True,
            'user_id': user.pk,
            'username': user.username,
            'auth_username': username,
            'auth_password': password
        }, status=status.HTTP_200_OK)
    return Response({
        'error': 'Invalid username or password'
    }, status=status.HTTP_401_UNAUTHORIZED)

# X-ray classification API
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def api_predict_pneumonia(request):
    if request.method == 'POST' and request.FILES.get('image_file'):
        img_file = request.FILES['image_file']
        fs = FileSystemStorage()
        
        filename = fs.save('reports/' + img_file.name, img_file)
        temp_img_path = fs.path(filename)
        
        try:
            model = RadiologyConfig.model
            img = image_utils.load_img(temp_img_path, target_size=(150, 150))
            img_array = image_utils.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0
            prediction = model.predict(img_array)
            result = "Pneumonia" if prediction[0][0] > 0.5 else "Normal"
            confidence = float(prediction[0][0]) if prediction[0][0] > 0.5 else float(1 - prediction[0][0])
            
            return Response({
                'result': result,
                'confidence': confidence * 100,  # Convert to percentage
                'image_path': filename
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'No image file provided'
    }, status=status.HTTP_400_BAD_REQUEST)

# Heartbeat classification API - Similar to your view function
# Remplacez la fonction api_heartbeat_classification existante par celle-ci:
@api_view(['POST'])
@permission_classes([AllowAny])
def api_heartbeat_classification(request):
    age = request.data.get('age')
    gender = request.data.get('gender')
    heart_rate = request.data.get('heartRate')  # Récupérer la fréquence cardiaque saisie
    
    if not age or not gender:
        return Response({
            'error': 'Age and gender are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Utilisez la valeur fournie ou une valeur aléatoire si non fournie
        if not heart_rate:
            possible_heart_rates = [60, 65, 72, 78, 85, 90, 67, 55, 57, 80]
            heart_rate = random.choice(possible_heart_rates)
        else:
            # Convertir en entier
            heart_rate = int(heart_rate)
            
        # OpenAI API call - même que précédemment
        openai.api_key = "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"
        prompt = f"A {gender} patient aged {age} years with a heart rate of {heart_rate} BPM. What could be the medical interpretation of this heart rate?"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        if response and 'choices' in response and response['choices']:
            prediction = response['choices'][0]['message']['content']
            return Response({
                'heart_rate': heart_rate,
                'prediction': prediction
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'heart_rate': heart_rate,
                'error': "No valid response received from OpenAI."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        return Response({
            'error': f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Document management APIs - simplified without authentication
@api_view(['GET'])
@permission_classes([AllowAny])
def api_list_documents(request):
    firstname = request.query_params.get('firstname', '')
    lastname = request.query_params.get('lastname', '')
    
    # Without authentication, return all documents (or limit some way)
    documents = DocumentModel.objects.all()
    
    if firstname and lastname:
        documents = documents.filter(name__icontains=firstname, lastname__icontains=lastname)
    elif firstname:
        documents = documents.filter(name__icontains=firstname)
    elif lastname:
        documents = documents.filter(lastname__icontains=lastname)
    
    serializer = DocumentModelSerializer(documents, many=True)
    return Response(serializer.data)

# Doctor search API - already using AllowAny
# In your api.py file
# Add this function at the top of your file, after the imports
def types_and_cities(specialiterVilleListe):
    """Extract unique specialties and cities from a list of tuples"""
    Specialiter = [elm[1] for elm in specialiterVilleListe]
    cities = [elm[0] for elm in specialiterVilleListe]
    return list(set(Specialiter)), list(set(cities))

@api_view(['GET'])
@permission_classes([AllowAny])
def api_get_doctor_filters(request):
    # Use the exact same function as your web view
    DoctorsListe = DoctorsInfo.objects.values_list('City', 'Specialiter').distinct()
    SpecialiterList, citiesList = types_and_cities(DoctorsListe)
    
    # Return with the EXACT same field names as your web app
    return Response({
        'filtered_Specialiter': SpecialiterList,
        'filtered_cities': citiesList
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_search_doctors(request):
    # Match exactly your web parameter names
    specialty = request.query_params.get('Specialiter')
    city = request.query_params.get('ville')
    
    queryset = DoctorsInfo.objects.all()
    
    # Match your existing filtering logic
    if specialty and specialty != "All Specialties":
        queryset = queryset.filter(Specialiter=specialty)
    if city and city != "All Cities":
        queryset = queryset.filter(City=city)
    
    # Create response data in the same format as your template's expectations
    doctors = []
    for doctor in queryset:
        image_url = doctor.image if hasattr(doctor, 'image') else ""
        
        doctors.append({
            'id': doctor.id,
            'DoctorName': doctor.DoctorName,
            'Specialiter': doctor.Specialiter,
            'City': doctor.City,
            'Link': doctor.Link if hasattr(doctor, 'Link') else "",
            'Location': doctor.City,  # Added this based on your guest.html template
            'image': image_url  # Simple string, not a URL object
        })
    
    return Response(doctors)

# Add this new function
@api_view(['POST'])
@permission_classes([AllowAny])
def api_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({"success": True, "message": "Successfully logged out"})
    return Response({"success": False, "message": "No user to log out"})

# Replace your existing api_chatbot function with this:

@api_view(['POST'])  # Change from GET to POST
@permission_classes([AllowAny])
def api_chatbot(request):
    user_input = request.data.get('message', '')  # Changed from query_params to data
    if not user_input:
        return Response({'response': 'No input provided'})
    
    try:
        # Use the functions from your views that already work
        from .views import predict_class, get_response, intents
        
        prediction = predict_class(user_input)
        response = get_response(prediction, intents)
        return Response({'response': response})
    
    except Exception as e:
        return Response({'error': f"An error occurred: {str(e)}"}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Add this function 

# Assurez-vous que cette fonction est correctement implémentée:

@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def api_generate_report(request):
    if request.method == 'POST':
        # Extract form data
        firstname = request.data.get('firstname')
        lastname = request.data.get('lastname')
        case_description = request.data.get('case_description')
        doctor_name = request.data.get('doctor_name', 'Mobile App User')
        
        # Check for required fields
        if not all([firstname, lastname, case_description]):
            return Response({
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for required image file
        if 'image_file' not in request.FILES:
            return Response({
                'error': 'X-ray image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        img_file = request.FILES['image_file']
        fs = FileSystemStorage()
        
        # Save the uploaded image
        filename = fs.save('reports/' + img_file.name, img_file)
        temp_img_path = fs.path(filename)
        
        try:
            # Load template
            template_file = os.path.join(settings.MEDIA_ROOT, 'documents', 'Pneumonia_Medical_Report_Template.docx')
            doc = Document(template_file)
            
            # Fill template
            user_inputs = {
                'doctor_name': doctor_name,
                'patient_name': f'{firstname} {lastname}',
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'case_description': case_description,
                'xray_image': temp_img_path
            }
            
            # Use the existing replace_placeholders function (imported from views)
            from .views import replace_placeholders
            replace_placeholders(doc, user_inputs)
            
            # Save document
            output_filename = f'{firstname}_{lastname}_report.docx'
            output_path = os.path.join(settings.MEDIA_ROOT, 'documents', output_filename)
            doc.save(output_path)
            
            # Create document record (using a dummy user if not authenticated)
            try:
                user = request.user if request.user.is_authenticated else User.objects.first()
                new_document = DocumentModel(
                    user=user,
                    name=firstname,
                    lastname=lastname,
                    description=case_description,
                    image=filename,  # Relative path for DB storage
                    file=f'documents/{output_filename}'  # Relative path for DB storage
                )
                new_document.save()
                
                # Get the base URL for media files
                media_url = settings.MEDIA_URL
                
                return Response({
                    'success': True,
                    'message': 'Report generated successfully',
                    'document_id': new_document.id,
                    'report_url': f"{request.build_absolute_uri(media_url)}documents/{output_filename}",
                    'image_url': f"{request.build_absolute_uri(media_url)}{filename}"
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Failed to save document record: {str(e)}',
                    'report_path': output_path
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'error': f'Failed to generate report: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'error': 'Invalid request'
    }, status=status.HTTP_400_BAD_REQUEST)