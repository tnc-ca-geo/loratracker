export AWS_DEFAULT_REGION=us-west-1
export AWS_SAM_STACK_NAME=loratracker
export AWS_ACCESS_KEY_ID=$(aws-vault exec falk -- credstash get AWS_IOT_DEVUSER_ACCESS_KEY_ID)
export AWS_SECRET_ACCESS_KEY=$(aws-vault exec falk -- credstash get AWS_IOT_DEVUSER_SECRET_ACCESS_KEY)
export AGO_CLIENT_ID=$(aws-vault exec falk -- credstash get ARCGISONLINE_LORA_CLIENT_ID)
export AGO_CLIENT_SECRET=$(aws-vault exec falk -- credstash get ARCGISONLINE_LORA_CLIENT_SECRET)
