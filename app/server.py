import warnings
warnings.filterwarnings('ignore')
import eventlet
import uvicorn
import socketio
import asyncio
import pandas as pd
from aiohttp import web
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
import io
import base64
import cv2
import numpy as np
import imutils
from PIL import Image as Image_pil
from pathlib import Path
from mindflow_model import Model


# Chargement des informations sur l'architecture du modèle
#learn = load_learner('models/aimotion-hns-34.pkl')


### Flux d'images entrant dans le réseau de neurones

# Chargement de l'algorithme de la cascade de HAAR,technique classique de computer vision,permettant de déjà préselectionner les visages sur le flux d'images entrant

#haar_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')

# Parametre définissant le rognage effectué sur les visages préselectionnés, permettant de meilleurs performances de detection
#crop_param = (20, 40)

# Paramètre de chemin d'accès utilisé pour afficher l'émoji correspondant à l'émotion prédite sur le visage : 
#emoji_path = 'static/assets/emoji'


path = Path(__file__).parent

print('Web_server_init')

st_app = Starlette()
st_app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
st_app.mount('/static', StaticFiles(directory='app/static'))

sio = socketio.AsyncServer(sync_mode='aiohttp',async_mode='asgi',max_http_buffer_size=1e10)

app = socketio.ASGIApp(sio, st_app)



@st_app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())





@sio.on('frame')
async def image(header, init_msg):
    emotions = ['neutral', 'happy', 'sad', 'surprise', 'fear', 'disgust', 'anger', 'contempt']
    df_emotions = pd.DataFrame(None,columns=emotions)



        
    print('OK')
    print(init_msg)

    b64_src = "data:image/jpeg;base64"

    raf_dan_model = Model()
    crop_param = (3*20, 3*20)
    haar_cascade = cv2.CascadeClassifier('app/models/haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
            r , frame = cap.read()
            frame = cv2.flip(frame, 1) # annule l'inversion de l'image par la webcam
            #r, frame = cv2.imencode('.jpeg', frame)


            # Par défaut, la frame est en RGB, on la converti en image "niveaux de gris" 
            # cela permet d'avoir une plus grande efficience computationnelle et de meilleurs résultats pour
            # l'algorithme de Viola Jones
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            #cv2.imshow('Grayscale', gray_frame)
                
            #Extraction des visages present sur la gray_frame grace à l'algorithme de HAAR précedement chargé, nous retourne un itérable de coordonnées spatiales dans la gray_frame correspondantes
            

            

            visages = haar_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5,
                            minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
                    # Grace à chaque coordonnées des visages detectés, on leur applique le rognage spécifié precedemment et les envoient dans le réseau de neurones pour detection
            for visage_coordinates in visages:

                # Extraction des coordonées du visage en cours de traitementn, h étant la hauteur et w la largeur du rectangle correspondant au visage
                X, Y, w, h = visage_coordinates

                # Rognage et extraction de l'image 'niveau de gris' traité du visage en cours de traitement
                x_d, y_d = crop_param
                x1, x2, y1, y2 = (X - x_d, X + w + x_d, Y - y_d, Y + h + y_d)
                       
                
                try:
                    cp_visage = frame[y1:y2, x1:x2] #extraction du visage sur la frame RGB originelle
                    #cp_visage = cv2.resize(cp_visage, dsize=(48*1, 48*1))
                    #cv2.imwrite('test.jpg', cp_visage)
                    emotion_idx, emotion_class, emotion_prob, probs = raf_dan_model.predict(cp_visage)

                    print(emotion_idx, emotion_class, emotion_prob)

                    df_emotions = df_emotions.append({
                        'neutral':probs[0],
                        'happy':probs[1],
                        'sad':probs[2],
                        'surprise':probs[3],
                        'fear':probs[4],
                        'disgust':probs[5],
                        'anger':probs[6],
                        'contempt':probs[7]
                        },ignore_index=True)

                    df_emotions['positive'] = df_emotions['happy'] + df_emotions['surprise'] + df_emotions['contempt']
                    df_emotions['negative'] = df_emotions['sad'] + df_emotions['fear'] + df_emotions['disgust'] + df_emotions['anger']
                    
                except:
                    pass

            try:
                cv2.rectangle(img=frame,pt1=(x1 +10, y1+10),pt2=(x2-10, y2-10),color=(255, 25, 50),thickness=3)
                cv2.putText(frame,emotion_class,(50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 25, 50), 2, cv2.LINE_AA)
                #cv2.putText(frame,str(emotion_prob)[:3],(50,50), cv2.FONT_HERSHEY_SIMPLEX, 2, (127, 127, 127), 0.5, cv2.LINE_AA)
                r, frame = cv2.imencode('.jpeg', frame)
                stringData = base64.b64encode(frame).decode('utf-8')
                stringData = b64_src +','+stringData
                print('Frame Treated Succesfully')
                #emit the frame back
                probs_avg = list(df_emotions[emotions].mean() *100)
                emotion_spectrum = list(df_emotions[['positive','neutral','negative']].mean()*100)
                emotion_spectrum = [x/sum(emotion_spectrum) for x in emotion_spectrum]
                data = {'image':stringData,'emotion':emotion_class,'emotion_prob':emotion_prob, 'probs':probs,
                'probs_avg':probs_avg,'emotion_spectrum':emotion_spectrum};

                
                await sio.emit('response_back', data)

                print('Processed Frame Emited Succesfully')
    
            except:

                r, frame = cv2.imencode('.jpeg', frame)
                stringData = base64.b64encode(frame).decode('utf-8')
                stringData = b64_src +','+stringData

                data = {'image':stringData,'emotion':None,'emotion_prob':None,'probs':None,'probs_avg':None,
                'emotion_spectrum':None}

                await sio.emit('response_back', data)
                print('Vanilla Frame Emited Succesfully')


            


   

    

    
if __name__ == '__main__':
    
    
    uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
