# Instructions
Create a concise description of the attached image. IMPORTANT! DO NOT START WITH THE WORDS "THE IMAGE". 
The description should include what is in the image and any action happening in the photo such that a blind person could 
form a mental image of what the photo represents. If there is significant text in the image, extract that text as part of 
the description. IMPORTANT! IF THERE IS NO TEXT IN THE IMAGE DO NOT SAY THAT. After providing a description, output a 
list of tags in all lower case that would describe the contents of what is in the image with the associated confidence 
level. Finally, output a list of colors that indicate the most common colors found in the image with a value indicating 
the relative percentage of the image that uses that color. Only provide the top 4 colors max.

# Response Formatting:
```json
{
 "description": "The head and shoulders of a cat with a mix of white brown and black fur looking directly at the camera. It is wearing a bow around its neck.",
 "tags": [
     { "tag": "cat", "confidence": 0.98 },
     { "tag": "bow", "confidence": 0.82 }
  ],
 "colors" : [
   { "color": "brown", "frequency": 0.2 },
   { "color": "white", "frequency": 0.7 },
 ]
}
```
