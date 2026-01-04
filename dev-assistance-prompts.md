# Purpose
This project was written as an exercise in working with offline AI using local models.  While I'm competent at Python and React 
they are not my strong suits. I am also working with a component framework known as [Mantine](https://mantine.dev/). This provided an opportunity 
to see how effective the local models can be at getting answers.  

This file will capture SOME of the prompts I used to help me figure out various aspects of the project as examples you can 
try yourself to see how the results look.  I'll try to capture the `prompt` which `local model` I was using and some thoughts on the
results

# Prompts
**Intent:** I wanted to generate thumbnails and store them as base64 lower quality jpeg images in the vector DB's metadata. 

**Model:** `google/gemma-3-12b`

**Prompt:**
```text
Create an example of how to take a Pillow `Image`, generate a thumbnail constrained to a fixed width and height but maintaining the proper aspect ratio and converting that thumbnail in its JPEG representation with 80% compression as base64 in Python
```

**Discussion:** Provided a good example of the code necessary for doing this.  Also provided detailed explanation.  I was able to work with the example and adapt it to my purposes.

---
**Intent:** Template

**Model:** `google/gemma-3-12b`

**Prompt:**
```text
template
```
**Discussion:** Template

---



