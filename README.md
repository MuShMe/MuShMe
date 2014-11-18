MusicShareMeta
==============

![Travis CI](https://magnum.travis-ci.com/rootAvish/MuShMe.svg?token=javYTs1KMZ6nAj1iVtzd&branch=master)

This repository houses the most awesome music sharing network on the future web. If you think the repository in its current state is any way a judge of the ambition and hard work we put in this project, feel free to stop reading and fuck off. This was created because we wanted to learn something, and any form of reward, is personally, of no value to me. Some thing need much improvement, and will get that in due course of time. All those sleepless nights and bunked classes resulted in us understanding web practices, good and bad. We also managed to achieve something cool.

REQUIREMENTS
------------

* [flask](https://flask.pocoo.org)
* MySQL relational database
* flask-wtf
* [PyMySQL](https://github.com/PyMySQL/PyMySQL)

CONTRIBUTION
------------

* Install python 2.X

* Fork the repo.

* Install the files from `requirements.txt` using easy_install or pip.

* To run the client, navigate to `src/client/mutagen/` and run:-
	```bash
	  $mutagen build
	  $mutagen install
	```

* then run:-
	```bash
	   $python runserver.py
	```
  in the root project directory to launch this shiz.

* See if there's anything you might like to learn, and achieve that by adding to the base of the project. Currently it's Flask with minimal amount of JavaScript.

* We shall improve things where we want them, and possibly never have time for others.

* Also, this goes live here-> [MuShMe](#) (link will go live whenver we feel like it.)


TODO
====
* ~~Get recommendations working.~~
* ~~Get everything sorted so our app doesn't break all the time.~~
* ~~Improve the search.~~
* ~~A possibly better looking interface.~~
* A lot of minor fixes.
* ~~Fix the damn profile pics.~~


OPTIONALLY
----------
* Ajaxify this shit.
* Anything that can enhance our skills.
* Anything fun.
* Make the "scrobbler" work on Windows too.
* Enchane API.
* Write unit tests, so that Travis is actually of use :smiley:


LICENSE
-------------
The MIT License (MIT)

Copyright (c) 2014 The DBMS Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
