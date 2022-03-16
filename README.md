# Lora Tracking using AWS

The goal of this project is to create a geographical enabled dashboard prototype for sensors and assets in ArcGIS online before we hand it off to contractor. 

**iot-aws-app**

This application implements a webhook in AWS that sends coordinates from LoRaWAN-based trackers to ArcGIS online. It replaces in part a workflow implemented in https://github.com/tnc-ca-geo/LoraTesting and is superior because of

a) the use of the webhook API (instead of MQTT)

b) the use of Lambda functions so that we don't rely on a dedicated server

## Payload decoders

This application relays currently on payload decoders. Even though that is not the ideal choice it allows us to use a wide range of tracking devices within the same application. Currently, we are using Oyster trackers (https://www.digitalmatter.com/devices/oyster-lorawan/) as reference. A payload decoder needs to implement the fields: ```time``` (for GPS derrived time), ```longitudeDeg```, and ```latitudeDeg```. Other GPS values like spead and heading need to be implemented in the future.

## Using SAM

The application is build on the simple AWS SAM starter template. NOTE: AWS SAM does not play well together with aws-vault, AWS credentials have to be set in the environment. Look at ```set_local_vars.sh.template``` for an idea how to create with aws-vault. Source a copy of that file if you are Falk and have access to his cred store. Adapt or export credentials as environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION) manually if you are not Falk.

```source set_local_vars.sh```

The application can be deployed with sufficient rights on AWS using the following two commands:

```sam build```

```sam deploy --guided```

In the interactive process of deployment a valid ArcGIS online secret needs to be provided (at the first time, it can be stored in the deployment files).

## Required Assets

Beside an AWS account, a ArcGIS online account is needed. Within this account, a feature service or view with the name lora_tracker_1 is needed.

There is a script to generate a Shapefile that can be used to create this service (see here https://github.com/tnc-ca-geo/LoraTesting/tree/master/clients/helpers). I will add a script to generate this and migrate existing data.

## Web App

There is a basic web app that can be accessed using https://lora-tracker.codefornature.org/. In order to use the web application login into ArcgisOnline using your account. 
