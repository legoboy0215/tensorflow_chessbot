import numpy as np

# Imports for visualization
import PIL.Image
from io import StringIO
from urllib.request import urlopen, Request
import urllib.parse

# Imports for pulling metadata from imgur url
import requests
from bs4 import BeautifulSoup

# All images are returned as PIL images, not numpy arrays
def loadImageGrayscale(img_file):
  """Load image from file, convert to grayscale float32 numpy array"""
  img = PIL.Image.open(img_file)

  # Convert to grayscale and return
  return img.convert("L")

def loadImageFromURL(url):
  """Load image from url.
  Or metadata url link from imgur"""
  
  # If imgur try to load from metadata
  url = tryUpdateImgurURL(url)

  # Try loading image from url directly
  try:
    req = Request(url, headers={'User-Agent' : "TensorFlow Chessbot"})
    con = urlopen(req)
    # Return PIL image and url used
    return PIL.Image.open(StringIO(con.read())), url
  except IOError:
    # Return None on failure to load image from url
    return None, url

def tryUpdateImgurURL(url):
  """Try to get actual image url from imgur metadata"""
  if 'imgur' not in url: # Only attempt on urls that have imgur in it
    return url

  soup = BeautifulSoup(requests.get(url).content, "lxml")
  
  # Get metadata tags
  meta = soup.find_all('meta')
  # Get the specific tag, ex.
  # <meta content="https://i.imgur.com/bStt0Fuh.jpg" name="twitter:image"/>
  tags = list(filter(lambda tag: 'name' in tag.attrs and tag.attrs['name'] == "twitter:image", meta))
  
  if tags:
    # Replace url with metadata url
    url = tags[0]['content']
  
  return url

def loadImageFromPath(img_path):
  """Load PIL image from image filepath, keep as color"""
  return PIL.Image.open(open(img_path,'rb'))


def resizeAsNeeded(img, max_size=(2000,2000)):
  if not PIL.Image.isImageType(img):
    img = PIL.Image.fromarray(img) # Convert to PIL Image if not already

  """Resize if image larger than max size"""
  if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
    print("Image too big (%d x %d)" % (img.size[0], img.size[1]))
    new_size = np.min(max_size) # px
    if img.size[0] > img.size[1]:
      # resize by width to new limit
      ratio = np.float(new_size) / img.size[0]
    else:
      # resize by height
      ratio = np.float(new_size) / img.size[1]
    print("Reducing by factor of %.2g" % (1./ratio))
    new_size = (np.array(img.size) * ratio).astype(int)
    print("New size: (%d x %d)" % (new_size[0], new_size[1]))
    img = img.resize(new_size, PIL.Image.BILINEAR)
  return img

def getVisualizeLink(corners, url):
  """Return online link to visualize found corners for url"""
  encoded_url = urllib.parse.quote(url, safe='')
  
  return ("http://tetration.xyz/tensorflow_chessbot/overlay_chessboard.html?%d,%d,%d,%d,%s" % 
    (corners[0], corners[1], corners[2], corners[3], encoded_url))
