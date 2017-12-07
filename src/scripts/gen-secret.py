
import uuid
import base64

def gen_secret():
  data = b''.join(uuid.uuid4().bytes for _ in range(3))
  return base64.b64encode(data).decode('ascii')

if require.main == module:
  print(gen_secret())
