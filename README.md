# Stanwood Python Utils

## Description

This project contains Python code snippets for Google App Engine projects.

Supported services:
* firebase
    * cloud messaging
    * firestore
    * authorization
* google
* slack
* github
* contentful
* toggl


## Installation

1. Add this package as git submodule:

`git submodule add git@github.com:stanwood/Stanwood_Python_Utils.git lib/stanwood_python_utils`

2. Add package to `appengine_config.py` file:

```
import os
from google.appengine.ext import vendor

vendor.add(os.path.join(os.path.dirname(__file__), 'stanwood'))
```
