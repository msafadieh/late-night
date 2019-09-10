# late-night
a webpage with Vassar's Gordon Commons late night menu items

## Requirements
1. Python 3
2. [Some python modules](requirements.txt)

## Usage

### Set up
```
> git clone https://github.com/msafadieh/late-night.git
> cd late-night
> python3 -m venv .env
> source bin/activate
> pip3 install -r requirements.txt
```
### Deploy using gunicorn
```
> gunicorn latenight:app -b localhost:4000
```
Make sure to replace `localhost:4000` with the correct host and port. I recommend setting up a reverse proxy using [nginx](https://nginx.org/).

## License
This project was released under [GPL 3.0](LICENSE).
