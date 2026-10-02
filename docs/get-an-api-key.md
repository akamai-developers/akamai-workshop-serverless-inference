# Get an API key

[Workshop home](../README.md) · [Setup](00_prework.md) · [Endpoint reference](inference.md)

Nothing else in this workshop works until you have an account and a key. Do this
first, and do it before the session if you are attending one. Account verification
can take a while and it is the most common reason someone is stuck at the start.

## 1. Create an Akamai Cloud account

> ### $300 in free credit for Akamai Cloud
> Sign up here: **[http://login.linode.com/signup?promo=akm-dev-git-300-72326-P153](http://login.linode.com/signup?promo=akm-dev-git-300-72326-P153)**

Confirm the credit amount, eligibility, and expiration in Cloud Manager before you
rely on it. Credit does not remove the need to watch what you spend.

Sign in to [Cloud Manager](https://cloud.linode.com) and finish any verification the
account asks for. If activation is pending, follow the instructions in the email.
See [account troubleshooting](https://techdocs.akamai.com/cloud-computing/docs/troubleshooting-cloud-manager-errors)
if it stays pending.

## 2. Create an inference key

<!-- TODO before publishing: replace this section with either the Cloud Manager
     click path and screenshots, or the CLI commands below, whichever the team
     prefers. Do not ship the placeholder. -->

**Option A: Cloud Manager**

Follow the official instructions in
[the Akamai Cloud Inference documentation](https://techdocs.akamai.com/cloud-computing/docs/ai-inference).

**Option B: the CLI**

```bash
# TODO: confirm the exact command before publishing.
```

Either way you end with a string that starts with `sk_aka_`. Copy it once. Treat it
like a password.

## 3. Put the key in your `.env`

From the workshop directory:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder:

```ini
AKAMAI_BASE_URL=https://api.akamai-inference.com/v1
AKAMAI_API_KEY=sk_aka_your_key_here
```

Keep the `/v1` suffix on the base URL. Leaving it off produces a `404` on every
request, which looks like a wrong model name and is not.

## 4. Check that it works

```bash
curl -s $AKAMAI_BASE_URL/models \
  -H "Authorization: Bearer $AKAMAI_API_KEY" | head -c 400
```

A list of models means the key and the endpoint are both right. A `401` means the key
is wrong or has extra whitespace. Anything else is in
[troubleshooting](troubleshooting.md).

If you would rather check from Python, [setup](00_prework.md) ends with a script that
does the same thing and prints a clearer message.

## Keeping the key safe

- `.env` is gitignored. Files you create yourself are not.
- Do not paste the key into a notebook cell. The notebooks read it from `.env`.
- Clear notebook outputs before sharing. An error traceback can contain a key.
- If you leak one, delete it in Cloud Manager and create another.

Next: [set up your laptop](00_prework.md).
