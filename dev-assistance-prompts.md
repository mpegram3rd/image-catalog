# Purpose
This project was written as an exercise in working with offline AI using local models.  While I'm competent at Python and React 
they are not my strong suits. I am also working with a component framework known as [Mantine](https://mantine.dev/). This provided an opportunity 
to see how effective the local models can be at getting answers.  

This file will capture SOME of the prompts I used to help me figure out various aspects of the project as examples you can 
try yourself to see how the results look.  I'll try to capture the `prompt` which `local model` I was using and some thoughts on the
results

# Prompts
**Intent:** I wanted to generate `thumbnails` and store them as `base64` lower quality `jpeg` images in the vector DB's metadata. 

**Model:** `google/gemma-3-12b`

**Prompt:**
```text
Create an example of how to take a Pillow `Image`, generate a thumbnail constrained to a fixed width and height but maintaining the proper aspect ratio and converting that thumbnail in its JPEG representation with 80% compression as base64 in Python
```

**Discussion:** Provided a good example of the code necessary for doing this.  Also provided detailed explanation.  I was able to work with the example and adapt it to my purposes.

---
**Intent:** I realized it was going to be better for me to work with the already `Base64` encoded image file I had in memory so I wanted to take that data and directly create a `PIL Image` file from it.

**Model:** `google/gemma-3-12b`

**Prompt:**
```text
How can I take a base64 encoded jpeg image and convert it into a PILLOW image?
```
**Discussion:** Once again the solution was satsifactory, in fact a bit more complete than I needed to so I extracted the useful bits and applied them to my situation.

---
**Intent:** After creating a grid of thumbnails I wanted to be able to open a `Mantine Modal` when I clicked on the `Mantine Image`  I also wanted to be able to pass in the URL of the image to be displayed in the modal.  I knew this needed to use props but wanted to see how the model responded.

**Model:** `google/gemma-3-12b`

**Prompt:**
```text
Create an example using Mantine of an Image that is clickable.  When clicked it will open a modal that will show the image that is defined in another component.  The modal component will be passed a URL so it will know which image to display.
```
**Discussion:** The model provided an appropriate solution.  It also provided a good explanation of the solution and followed up with `Key Improvements and Considerations`

---
**Intent:** Template

**Model:** `google/gemma-3-12b`

**Prompt:**
```text
template
```
**Discussion:** Template

---



