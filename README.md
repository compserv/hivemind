# Hivemind

**Hivemind** displays usage stats for the Berkeley EECS instructional
computers. It was originally developed by [Allen Guo][allen-guo] but is now
maintained by [HKN's Compserv committee][hkn-compserv].

[allen-guo]: https://github.com/guoguo12
[hkn-compserv]: https://hkn.eecs.berkeley.edu/about/officers


## How does it work?

Every five minutes, `backend/census.py` is executed. It connects to each server
listed in `backend/server.txt` via SSH and collects information. The results
from all of the servers are combined into a single JSON file
(`data/latest.json`).

You can view the most recently generated JSON file here:
[https://www.ocf.berkeley.edu/~hkn/hivemind/data/latest.json][latest].

[latest]: https://www.ocf.berkeley.edu/~hkn/hivemind/data/latest.json


### Overall load formula

The "overall load" heuristic is implemented in `toRating()` in
[`main.js`][main-js].

[main-js]: https://github.com/compserv/hivemind/blob/gh-pages/js/main.js


## How to contribute

Want to host the website locally? Clone this repo, and start a web server in
the project root directory.

The backend (i.e. the script that grabs data from the servers) is a little
harder to set up:

0. Install [paramiko](https://pypi.python.org/pypi/paramiko) via `pip install
   paramiko`.
1. Clone this repo and navigate to `backend/`.
2. Make a directory called `private/`.
3. Create an RSA key pair (`id_rsa` and `id_rsa.pub`) inside `private/` with no
   passphrase.
4. Add the public key to your class account's `~/.ssh/authorized_keys` file.
5. Change the value of `LOGIN_USERNAME` in `census.py` to your login.

You should then be able to execute `census.py` to grab data from each server in
`servers.txt`. The results are printed to stdout, which `run_census` puts into
a file for the frontend to fetch.


## Credits

Hivemind was made using jQuery, Vue.js, Moment.js, Skeleton, clipboard.js, and Hint.css.

Hivemind was originally developed by [Allen Guo][allen-guo] but is now
maintained by [HKN's Compserv committee][hkn-compserv].
