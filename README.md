# Chaos

Chaos is the web service which implements the real-time aspect of Navitia

## Installation

Installation instructions can be followed from [http://confluence.canaltp.fr/display/SPEED/Installation+et+utilisation+de+Chaos+en+local](http://confluence.canaltp.fr/display/SPEED/Installation+et+utilisation+de+Chaos+en+local)

### Python & Protobuf

Install [`pip`](https://pip.pypa.io/en/latest/installing/) and [`virtualenv`](http://virtualenv.readthedocs.org/en/latest/installation.html)

Install Python dependencies

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

You need to compile `protobuf` files before using chaos:

```
# Add `protobuf` files to the `proto` directory
# before executing the following command
./setup.py build_pbf
```

## Provisioning

Provisioning instructions can be followed from [provisioning/PROVISIONING.md](provisioning/PROVISIONING.md)

## Update database
source venv/bin/activate
honcho run ./manage.py db upgrade

## Change schema database
source venv/bin/activate
honcho run ./manage.py db migrate