# GeoLocationEcho

This app queries the MaxMind GeoIP2 Cities database for information about submitted IP addresses and returns that 
information as JSON

## Architecture & Deployment

The app may be deployed onto a kubernetes cluster by executing

`helm upgrade --install echo ./GeoLocationEcho`

The helm chart deploys the following from the project root:

1. The Flask web app which handles the API calls and database queries, deployed as a k8s deployment. Packaged alongside
this is an initialization container which pulls the GeoIP database into an `emptyDir` volume for use by the Flask app
2. A k8s Service to front the deployment, which defaults to type `NodePort`
3. A k8s CronJob which weekly causes a rolling redeploy of the Flask deployment. This ensures the GeoIP database is 
regularly updated without downtime

## Testing

The tests may be run in the usual way via `python -m unittest` from the project root

### Note

The tests assume `GeoLite2-City.mmdb` is present in the `tests` directory