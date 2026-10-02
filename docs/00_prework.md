# Setup

[Workshop home](../README.md) · [Get an API key](get-an-api-key.md) · [Troubleshooting](troubleshooting.md)

Fifteen minutes, and you only need it once. Do this before the session. Get your
[API key](get-an-api-key.md) first, because nothing here can be checked without it.

## 1. Check your tools

macOS, Linux, or Ubuntu under [WSL 2](https://learn.microsoft.com/windows/wsl/install).
You need Git and Python 3.11 or newer.

```bash
git --version
python3 --version
```

On Ubuntu, install the virtual environment package if it is missing:

```bash
sudo apt update
sudo apt install -y python3-venv
```

## 2. Clone and install

```bash
git clone https://github.com/akamai-developers/akamai-workshop-serverless-inference.git
cd akamai-workshop-serverless-inference
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Every command in this workshop runs from `akamai-workshop-serverless-inference` with
`.venv` active. Open a new terminal and you have to activate it again:

```bash
source .venv/bin/activate
```

## 3. Add your key

```bash
cp .env.example .env
```

Open `.env` and paste the key you created in [get an API key](get-an-api-key.md):

```ini
AKAMAI_BASE_URL=https://api.akamai-inference.com/v1
AKAMAI_API_KEY=sk_aka_your_key_here
```

Two variables, and they carry the whole workshop. There is no database to configure
and no cloud token to create.

## 4. Verify

```bash
python scripts/check_setup.py
```

It checks your Python version, that `.env` is filled in, that the endpoint answers,
and that one real completion comes back. It prints the model list so you can see what
is served today.

Expected output ends with:

```
All checks passed. Open the notebooks with: jupyter notebook
```

If a check fails it names the variable or the step to fix. See
[troubleshooting](troubleshooting.md) for the error you got.

## 5. Open the notebooks

```bash
jupyter notebook
```

Start with `01_Inference_APIs/01_inference_apis.ipynb`. Pick the kernel for this
project's `.venv`, not a system Python. If the first cell cannot find `openai`, the
kernel is wrong.

## Ready check

- `python --version` reports 3.11 or newer inside `.venv`
- `python scripts/check_setup.py` passes every line
- Jupyter opens and the kernel runs `import openai` without error
- Your key is in `.env` and nowhere else

## Optional, for the deploy folder only

Skip this unless you plan to run [deploy](../deploy/) at the end. It is not part of
the workshop and it creates billable resources.

You will need the [Linode CLI](https://techdocs.akamai.com/cloud-computing/docs/install-and-configure-the-cli)
and an SSH key:

```bash
ls ~/.ssh/id_ed25519.pub || ssh-keygen -t ed25519
```

Next: [call your first model](../01_Inference_APIs/).
