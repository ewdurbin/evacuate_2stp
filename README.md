# evacuate_2stp

Unfortuantely [the maintainer of 2STP](https://github.com/thomasrzhao) [announced end of support for 2STP](http://thomasrzhao.com/2stp-support/end-of-support/) in September 2016.

With the release of iOS 11.2.1, the UI for 2STP has begun to degrade. Sending me and many others on a search for a new app for 2FA.

This tool allows for decrypting the encrypted backups created by 2STP.

## Usage

Requires:

  - [Python 3.6](https://www.python.org/downloads/)
  - :cake: [`pipenv`](https://docs.pipenv.org) :cake:

```
git clone https://github.com/ewdurbin/evacuate_2stp.git
cd evacuate_2stp
pipenv install
pipenv run python decrypt_2STP.py --encrypted-2stp-export <path to your 2STP export>
```
