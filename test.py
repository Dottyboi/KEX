from math import floor, ceil
b = "abcdefghijklmnopqrstuvwxyzåäö"

print(len(b))

if len(b) > 25:
  if (offset := len(b) - 25) % 2 == 0:
    start = int(offset/2)
    stop = int(offset/2)
  else:
    start = int(floor(offset/2))
    stop = int(ceil(offset/2))

  b = b[start:-stop]
            
elif len(b) < 25:
  while len(b) < 25:
    b += b[-1]
            

print(len(b))

print(b)