# Vision-Language Model Example

This example demonstrates how to use secure-runpod-chat with a vision-language model.

## Starting the Chat

```bash
secure-runpod-chat --model meta-llama/Llama-3.2-11B-Vision-Instruct
```

## Example Session

### Analyzing an Image

```
You: /image ~/Pictures/sunset.jpg
Image uploaded. Include it in your next message.

You: Describe this image in detail
Assistant: This image shows a beautiful sunset over the ocean. The sky is painted
in vibrant shades of orange, pink, and purple, with wispy clouds catching the
last rays of the setting sun. The ocean appears calm, with gentle waves reflecting
the colorful sky. In the foreground, there's a silhouette of a palm tree...

You: What time of day was this photo likely taken?
Assistant: Based on the lighting and sky colors, this photo was most likely taken
during the "golden hour" - the period shortly before sunset, typically between
30-60 minutes before the sun fully sets below the horizon...
```

### Asking Follow-up Questions

```
You: What camera settings would be good for this type of photo?
Assistant: For sunset photography like this, I'd recommend:
- ISO: 100-400 (lower for less noise)
- Aperture: f/8 to f/11 (for good depth of field)
- Shutter Speed: 1/125 to 1/250 (depending on light)
- White Balance: Daylight or Cloudy mode...
```

### Uploading Multiple Images

```
You: /image ~/Pictures/cat.jpg
Image uploaded. Include it in your next message.

You: What animal is this?
Assistant: This is a domestic cat...

You: /image ~/Pictures/dog.jpg
Image uploaded. Include it in your next message.

You: Now what animal is this?
Assistant: This is a dog...

You: What are the key differences between cats and dogs?
Assistant: Cats and dogs have several fundamental differences...
```

## Tips for Vision Models

1. **Image Formats**: Supports common formats (JPG, PNG, WEBP)
2. **Image Size**: Large images are automatically resized
3. **One Image at a Time**: Upload a new image for each analysis
4. **Context**: The model remembers previous conversation
5. **Local Files**: Images must be on your local machine

## Advanced Usage

### Analyzing a PDF Page (as Image)

```bash
# First convert PDF to image
convert document.pdf[0] page1.jpg

# Then analyze
You: /image page1.jpg
You: Extract the text from this document
```

### Batch Analysis Script

```bash
#!/bin/bash

# Start chat and analyze multiple images
for img in ~/Pictures/*.jpg; do
    echo "/image $img"
    echo "Describe this image and suggest tags"
    echo ""
done
```

## Common Use Cases

- **Image Description**: Get detailed descriptions of photos
- **OCR**: Extract text from images
- **Object Detection**: Identify objects in images
- **Style Analysis**: Analyze artistic style and composition
- **Comparison**: Compare multiple images
- **Question Answering**: Ask specific questions about images
