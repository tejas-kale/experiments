# File Management Examples

This guide shows how to upload and download files during your chat session.

## Uploading Files

### Upload a Text File

```
You: /upload ~/Documents/data.csv
File uploaded to /root/uploads/data.csv

You: Can you analyze the CSV file at /root/uploads/data.csv?
Assistant: I'll analyze the CSV file for you...
```

### Upload a Python Script

```
You: /upload ~/Projects/script.py
File uploaded to /root/uploads/script.py

You: Review the code in /root/uploads/script.py and suggest improvements
Assistant: Looking at your Python script, here are some suggestions...
```

### Upload Multiple Files

```
You: /upload ~/data/train.csv
File uploaded to /root/uploads/train.csv

You: /upload ~/data/test.csv
File uploaded to /root/uploads/test.csv

You: Compare these two datasets
```

## Downloading Files

### Download Generated Files

```
You: Can you create a Python script to process this data?
Assistant: Here's a script... I'll save it to /root/outputs/process.py

You: /download /root/outputs/process.py ./process.py
File downloaded to ./process.py
```

### Download to Specific Location

```
You: /download /root/outputs/results.json ~/Downloads/results.json
File downloaded to ~/Downloads/results.json
```

### Download Without Specifying Local Path

```
You: /download /root/model_output.txt
File downloaded to ./model_output.txt
```

## Working with Uploaded Files

### Data Analysis Workflow

```
You: /upload ~/data/sales_data.csv
File uploaded to /root/uploads/sales_data.csv

You: Load the CSV file at /root/uploads/sales_data.csv and analyze trends
Assistant: I'll analyze the sales data...

You: Create a summary report and save it to /root/outputs/report.txt
Assistant: I've created a summary report at /root/outputs/report.txt

You: /download /root/outputs/report.txt ./sales_report.txt
File downloaded to ./sales_report.txt
```

### Code Review Workflow

```
You: /upload ~/Projects/app.py
You: /upload ~/Projects/tests.py
You: /upload ~/Projects/config.py

You: Review these files for security vulnerabilities
Assistant: After reviewing your files, I found several areas of concern...

You: Can you create an improved version with fixes?
Assistant: I've created improved versions in /root/outputs/...

You: /download /root/outputs/app_fixed.py ./app.py
```

## File Organization Tips

### Remote Directory Structure

Files are organized on the instance as:

```
/root/
├── uploads/         # Your uploaded files
├── images/          # Uploaded images (for vision models)
├── outputs/         # Generated outputs
└── model_server.py  # Model server (managed automatically)
```

### Best Practices

1. **Use Clear Names**: Name files descriptively
2. **Organize Locally**: Keep local files organized
3. **Download Important Results**: Always download before exiting
4. **Clean Up**: Remove sensitive files before exiting (automatic)

## Security Notes

### Automatic Cleanup

When you exit, the tool automatically removes:

- All uploaded files in `/root/uploads/`
- All images in `/root/images/`
- All temporary files in `/tmp/`
- Model cache files

### Manual Cleanup

If you want to remove a file during the session:

```
You: Can you delete /root/uploads/sensitive_data.csv?
Assistant: [Executes command to delete file]
```

## Advanced Examples

### Processing Multiple Files

```python
# Create a script to upload and process multiple files

#!/bin/bash

files=(
    "data1.csv"
    "data2.csv"
    "data3.csv"
)

for file in "${files[@]}"; do
    # Upload file
    echo "/upload ~/data/$file"
    sleep 1
done

# Process all files
echo "Analyze all CSV files in /root/uploads/ and create a combined report"
echo "Save the report to /root/outputs/combined_report.pdf"

# Download result
echo "/download /root/outputs/combined_report.pdf ./report.pdf"
```

### Batch Image Processing

```
You: /upload ~/images/batch1.zip
File uploaded to /root/uploads/batch1.zip

You: Unzip the file and process all images
Assistant: I'll unzip and process the images...

You: /download /root/outputs/processed_images.zip ./processed.zip
```
