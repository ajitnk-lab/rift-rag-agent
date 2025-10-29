FROM public.ecr.aws/lambda/python:3.11

# Copy application files
COPY lambda_handler.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD ["lambda_handler.lambda_handler"]
