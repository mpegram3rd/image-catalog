# Instructions
Create a concise description of the attached image. IMPORTANT! DO NOT START WITH THE WORDS "THE IMAGE". The description should include what is in the image and any action
happening in the photo such that a blind person could form a mental image of what the photo represents. After providing
a description, output a list of tags that would describe the contents of what is in the image with the associated
confidence level.  Finally output a list of colors that indicate the most common colors found in the image.

# Response Formatting:
```json
{
  "description": "The image contains a cat with a bow around her neck.",
  "tags": [
      { "tag": "cat", "confidence": 0.98 },
      { "tag": "bow", "confidence": 0.82 }
   ],
  "colors" : ["brown", "white", "black"]
}
```
