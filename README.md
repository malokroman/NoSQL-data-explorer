# nested-data-helper
Help you find the data nested deep in your data.

## Introduction

I am a data engineer who works with data a lot. Whilst flat data might be straight forward to navigate, it is often not the case for nested data. Especially data from APIs, JSONs, or NoSQL Databases, the schema is not enforced by design and it requires discipline from the developer, which is not always guaranteed. Even if we are lucky to have access to the documentations, these documents might still be outdated or too big to understand. 

To efficiently understand and navigate nested data, I have been using the functions in this modules and decided to polish them and publish them for anyone to use. I have used them to understand the schema discipline, find the path to desired data, understand if there are missing data and etc. They may not be helpful in production but they surely are useful being used in REPL or Jupyter notebook. Use cases can be scraping, feature engineering, data mining, data cleansing, edge case finding and on and on. By using these function, you can speed up your data inspection iterations.

This library consist of two parts:
- navigation: syntactic sugar to help you navigate to the subpath of the complex data with the path syntax
- pathfinder: help you find the relevant paths you are looking for from paths or from the values

They share the same path structure so you can easily copy the path and see the data for yourself.

This library might not be useful in production as [key] chains work just fine and explore part has limited use in production, but this can speed up your data exploration a lot.


### Why nested-data-helper

This library is lightweight and get the job done! We use core python so installation is a breeze and we can be sure that this will work for years to come even when it seems abandoned.

### Navigation

You can get the values of the data without the clumsy chain of square brackets now.
``` python
>>> from nested_data_helper.navigation import navigate

>>> data = {
...   "results": [
...      {"name": "happy", "synonyms": [{"text": "happy"}, {"text": "glad"}]},
...      {"name": "sad", "synonyms": [{"text": "sad"}, {"text": "upset"}]},
...   ]
... }
# Instead of this
>>> data["results"][0]["name"]
"happy"

# write this
>>> navigate(data, "results.[0].name")
"happy"
# You can even use a list like this
>>> navigate(data, "results.[].name")  # returns all name under the results list
["happy", "sad"]

# And of course list in lists
navigate(data, "results.[].synonyms.[].text")  # These will be in a flat structure
["happy", "glad", "sad", "upset"]

# And combination of both
navigate(data, "results.[0].synonyms.[].text")
["happy", "glad"]
```

This is even more powerful combined with the paths returned from explore and will allow quick exploration of your data.


### Pathfinder

This helps you understand the data structure you are looking for by filtering out the noise. Combined with Counter, you can find the most common paths in the data, or simply understand if there are missing data. You can also find out the type discipline of the data through the explore functions.

These functions are:
- find_paths
- find_paths_unique
- find_paths_unique_per_doc

The above are useful for understanding the schema of the nested data and data discipline. When combined with Counter, you can quickly understand what paths are the most important in the data set. Other use cases include finding the most common fields that we are not sure the exact path is for like "name", "id". More examples are in the docstring for each function.

- find_values

This is useful when you know of a value or an aspect of value but are not sure what the paths are. For example, if you are trying to join two data sets with a known key, you could use the key to find the path to the data you need. Or if you want to make sure you have the best path for something, you can use this function to list all the paths that share these values and then evaluate them. More examples are in the docstring for the function.


## Development
This library works fine and has past the test (I use doctest for now). This library should have no dependencies other than core python so it is up to you if you want to use a virtual environment. 

To run the tests: 
``` python
python -m unittest tests/**.py
```

Feel free to send pull requests, issues, or fork this repos to amend as you need.


## Known issues
- The path definition does not distinguish between two levels of keys versus a key with a dot in it. There is no plan to handle edge cases as the limited use cases does not warrant the added complexity, but here are some tricks to deal with it:

When you use navigate, it will return a KeyError if a key with dot exists.

``` python
>>> data = {"top_level": {"second.level": "value"}}

>>> navigate(data, "top_level.second.level")
Traceback (most recent call last):
KeyError: 'second'
```

With that, you know that the second.level key is with a dot. You can use this to find the actual key:

``` python
>>> navigate(data, "top_level").keys()
dict_keys(['second.level'])

>>> navigate(data, "top_level")["second.level"]
'value'
```

- The path definition does not distinguish keys that is in square brackets and list indices

Similar workaround can be used.
