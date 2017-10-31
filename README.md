### Prerequisites

Python 2.7
Scrapy
Scrapy-splash plugin
Docker

### Installing

To get the project running you need to install the prerequisites as follows:

Scrapy

```
pip install Scrapy
```

Scrapy-splash plugin

```
pip install scrapy-splash
```

Docker

```
Docker installation is dependant on the operating system in use. To install docker for your specific OS check https://docs.docker.com. Example docker installation for windows is found here https://docs.docker.com/docker-for-windows/install/#start-docker-for-windows
```

### Running the application

First get splash running by:

```
sudo docker run -p 8050:8050 scrapinghub/splash --max-timeout 300

```

Unzip the project. After that change directory to the project directory by running:

```
cd GPScrapper
```

From this directory you can then run the scrapper using the command:

```
scrapy crawl nj_administrative_code
```

After running this command, check the results.json file in the project directory to view scrapping results. Sample results from running the scrapper can be found in the 

```
results_sample.json
```

in the zip file


