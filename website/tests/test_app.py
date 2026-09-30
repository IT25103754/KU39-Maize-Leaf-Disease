import unittest,io
from PIL import Image
import numpy as np
from app import create_app
class AppTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=create_app();cls.client=cls.app.test_client()
 def test_home_health(self):
  self.assertEqual(self.client.get('/').status_code,200);self.assertEqual(self.client.get('/api/health').json['status'],'ready')
 def test_invalid(self):
  self.assertEqual(self.client.post('/api/predict').status_code,400)
  self.assertEqual(self.client.post('/api/predict',data={'image':(io.BytesIO(b'bad'),'x.jpg')}).status_code,400)
 def test_oversized(self):
  self.assertEqual(self.client.post('/api/predict',data={'image':(io.BytesIO(b'x'*(8*1024*1024+1)),'x.jpg')}).status_code,413)
 def test_gif(self):
  b=io.BytesIO();Image.new('RGB',(30,30)).save(b,'GIF');b.seek(0)
  self.assertEqual(self.client.post('/api/predict',data={'image':(b,'x.gif')}).status_code,400)
 def test_real_inference(self):
  b=io.BytesIO();Image.new('RGBA',(317,193),(80,140,40,180)).save(b,'PNG');data=b.getvalue()
  r=self.client.post('/api/predict',data={'image':(io.BytesIO(data),'x.png')});self.assertEqual(r.status_code,200)
  # Synthetic image only checks API/preprocessing parity, not classification quality.
  with Image.open(io.BytesIO(data)) as im:x=np.asarray(im.convert('RGB').resize((224,224),Image.Resampling.BILINEAR),dtype=np.float32)[None]
  engine=self.app.extensions['classifier'];expected=engine.model(x,training=False).numpy()[0];actual={row['class']:row['score'] for row in r.json['scores']}
  np.testing.assert_allclose([actual[c] for c in engine.classes],expected,atol=1e-7,rtol=1e-6)
  self.assertEqual(len(actual),4);self.assertAlmostEqual(sum(actual.values()),1,places=5)
