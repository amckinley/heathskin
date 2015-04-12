heathskin
=========

heathskin is used for providing useful game-tracking information in real-time,
and statistically over many games.


get heathskin
-------------
clone from github. inside the repo:

  pip install -r requirements.txt
  pip install -e .

starting heathskin
------------------
Start the webserver and the HAProxy server in front of it:
  circusd config/circus.ini

Then go to your browser to create an account:
  localhost:3000/register

Then start the uploader:
  heathskin-uploader --username foo@bar.com --password fizzbuzz

installing from github
----------------------

To install the latest development version:

  pip install cython git+git://github.com/surfly/gevent.git#egg=gevent