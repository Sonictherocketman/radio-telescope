# Astronomer

*This sub-project contains all of the code for running a data capture and transmission system for Radio Telescope devices. For the operation and physical manipulation of the telescope device itself, see the Lackey sub-project.*


## How it Works

Astronomer contains three separate processes which must run together on a Raspberry Pi (or other linux-based device) connected to a Software Defined Radio (SDR) which in-turn is connected to a radio telescope.

This software handles the tasks of observing celestial bodies, recording data, and uploading it to a remote service for data processing.


## Installation

Once you've procured a fresh Raspberry Pi and the rest of the components, log in to the RPi and perform the following steps.

Note, this installation assumes a fresh raspberry pi running either full or lite Raspbian.

You may need to install the following tools before beginning the installation:

```
$ sudo apt-get install -y \
    git \
    python3
    python3-pip
```

Then you will need to follow the [instructions here](https://osmocom.org/projects/rtl-sdr/wiki/Rtl-sdr) to install the rtl_sdr capture drivers. More information can be found on [this site](https://inst.eecs.berkeley.edu/~ee123/fa12/rtl_sdr.html)

Then, clone the repo to the correct location:
```
$ cd /opt
$ git clone https://github.com/Sonictherocketman/radio-telescope.git
```

Then install the python requirements.

```
$ pip install -r requirements.txt
```

Next, add the following section to your supervisord configuration located in `/etc/supervisord`.

```
[include]
files = /opt/radio-telescope/astronomer/supervisord.conf
```

Finally, gather the required information for the telescope from the web app. You will need two values which we will add to the user's `.bashrc`:

```
export HOME_AUTHORIZATION_TOKEN="some-token"
export TELESCOPE_ID="some-number"
```

Then start the services using supervisord!

```
$ sudo supervisorctl start astronomer
```
