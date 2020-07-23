# bookmark-service

A **bookmark server** or URI shortener that maintains a mapping (dictionary)
between short names and long URIs, checking that each new URI added to the
mapping actually works (i.e. returns a 200 OK).

## This server is intended to serve three kinds of requests:

* A GET request to the / (root) path.
  The server returns a form allowing the user to submit a new name/URI pairing.  The form also includes a listing of all the known pairings.
* A POST request containing "long_uri" and "shortname" fields.
  The server checks that the URI is valid (by requesting it), and if so, stores the mapping from shortname to long_uri in its dictionary.  The server then redirects back to the root path.
* A GET request whose path contains a short name.
  The server looks up that short name in its dictionary and redirects to the corresponding long URI.

## Usage

Example usage via command line:
```
curl \
  -X POST https://bookmark-service.herokuapp.com/ \
  --data-urlencode "long_uri=https://github.com/volcain-io/fswd-bookmark-service" \
  --data-urlencode "short_name=github-link"
```

Refresh website [https://bookmark-service.herokuapp.com](https://bookmark-service.herokuapp.com) to see results.

Example output on website:
```
github-link: https://github.com/volcain-io/fswd-bookmark-service

```

Example usage via command line:
```
curl -i GET https://bookmark-service.herokuapp.com/github-link
```

Example useage via web browser:
```
https://bookmark-service.herokuapp.com/github-link
```

Will redirect you to **long_uri**

