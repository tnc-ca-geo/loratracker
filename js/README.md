# Lora Tracker
Simple web-based application for viewing spatial LoRa data

https://lora-tracker.codefornature.org

## Getting started
 - Clone repo from https://github.com/tnc-ca-geo/LoraTesting.git
 - Navigate to LoraTesting/js/ directory 
 - Run `npm install` to install dev dependencies
 - From the LoraTesting/js/src directory run `python -m SimpleHTTPServer` to serve the site locally on http://localhost:8000

## Deploying to S3 Bucket
 - Run `npm run build` followed by `npm run s3_deploy_prod` to deploy the current build to the production envorinment ([https://lora-tracker.codefornature.org](https://lora-tracker.codefornature.org))
