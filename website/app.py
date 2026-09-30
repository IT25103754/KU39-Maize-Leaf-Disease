"""KU39 inference-only local website. Uses the original locked model."""
import os
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL','2')
os.environ.setdefault('CUDA_VISIBLE_DEVICES','-1')
from pathlib import Path
import hashlib,io,json,threading,time,warnings,webbrowser
import numpy as np
from PIL import Image,ImageOps,UnidentifiedImageError
from flask import Flask,request,jsonify,render_template
BASE=Path(__file__).resolve().parent
LIMIT=8*1024*1024
Image.MAX_IMAGE_PIXELS=25_000_000
class Classifier:
 def __init__(self):
  import tensorflow as tf
  self.info=json.loads((BASE/'model/model_info.json').read_text())
  path=BASE/'model/model.keras'
  if hashlib.sha256(path.read_bytes()).hexdigest()!=self.info['sha256']:raise RuntimeError('Model changed. Extract a fresh ZIP.')
  self.classes=self.info['classes'];self.model=tf.keras.models.load_model(path,compile=False);self.lock=threading.Lock()
  if self.model.input_shape!=(None,224,224,3) or self.model.output_shape[-1]!=4:raise RuntimeError('Unexpected model shape')
  self.model(np.zeros((1,224,224,3),np.float32),training=False)
 def predict(self,data):
  try:
   with warnings.catch_warnings():
    warnings.simplefilter('error',Image.DecompressionBombWarning)
    with Image.open(io.BytesIO(data)) as im:
     if im.format not in {'JPEG','PNG'}:raise ValueError('Choose a JPG or PNG image.')
     if getattr(im,'n_frames',1)!=1:raise ValueError('Choose a single-frame image.')
     im.load();rgb=ImageOps.exif_transpose(im).convert('RGB')
     x=np.asarray(rgb.resize((224,224),Image.Resampling.BILINEAR),dtype=np.float32)[None]
  except (OSError,UnidentifiedImageError,Image.DecompressionBombWarning,Image.DecompressionBombError) as e:
   raise ValueError('Cannot read this image. Choose a valid JPG/PNG under 25 megapixels.') from e
  start=time.perf_counter()
  with self.lock:s=self.model(x,training=False).numpy()[0]
  if not np.isfinite(s).all() or (s<0).any() or not np.isclose(s.sum(),1,atol=1e-5):raise RuntimeError('Invalid model output')
  rows=[{'class':self.classes[int(i)],'label':self.classes[int(i)].replace('_',' '),'score':float(s[i])} for i in np.argsort(-s,kind='stable')]
  return {'prediction':rows[0]['label'],'score':rows[0]['score'],'scores':rows,'model':self.info['model'],'inference_ms':round((time.perf_counter()-start)*1000),'notice':'Model scores do not guarantee correctness. Non-maize rejection and field validation are not implemented.'}
def create_app():
 app=Flask(__name__);app.config['MAX_CONTENT_LENGTH']=LIMIT+256*1024
 engine=Classifier();app.extensions['classifier']=engine
 @app.get('/')
 def index():return render_template('index.html',info=engine.info)
 @app.get('/api/health')
 def health():return jsonify(status='ready',model=engine.info['model'])
 @app.post('/api/predict')
 def predict():
  file=request.files.get('image')
  if not file or not file.filename:return jsonify(error='Choose a maize leaf image first.'),400
  data=file.read(LIMIT+1)
  if not data:return jsonify(error='The selected file is empty.'),400
  if len(data)>LIMIT:return jsonify(error='Choose an image under 8 MB.'),413
  try:return jsonify(engine.predict(data))
  except ValueError as e:return jsonify(error=str(e)),400
  except Exception:
   app.logger.exception('Prediction failed');return jsonify(error='Prediction failed. Check the app window and try another image.'),500
 @app.errorhandler(413)
 def oversized(e):return jsonify(error='Choose an image under 8 MB.'),413
 @app.after_request
 def headers(response):
  response.headers['Cache-Control']='no-store';response.headers['X-Content-Type-Options']='nosniff';return response
 return app
if __name__=='__main__':
 from waitress import serve
 print('Loading saved maize model. Keep this window open...',flush=True)
 app=create_app();port=int(os.environ.get('MAIZE_PORT','5000'));url=f'http://127.0.0.1:{port}'
 print(f'READY: {url}\nPress Ctrl+C to stop.',flush=True)
 if os.environ.get('MAIZE_NO_BROWSER')!='1':threading.Timer(1.5,lambda:webbrowser.open(url)).start()
 host=os.environ.get('MAIZE_HOST','127.0.0.1')
 if host=='0.0.0.0':
  print('Wi-Fi: use this computer Wi-Fi IPv4 address with port '+str(port)+'.',flush=True)
 serve(app,host=host,port=port,threads=4)
