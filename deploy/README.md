# Deploy the agent

[Workshop home](../README.md) · [Module 04](../04_Agents/) · [Endpoint reference](../docs/inference.md)

**Optional. 30 minutes.** Not part of the workshop. The four numbered modules create
nothing and cost nothing beyond inference. This folder does both.

It takes the agent from [module 04](../04_Agents/2_build_the_agent.ipynb), wraps it
in an HTTP endpoint, and runs it on a single Linode with the key on the server
instead of in a notebook.

## What this creates, and what it costs

| Resource | What | Cost |
|---|---|---|
| One Linode | A 1 GB shared CPU instance running Docker | Charged hourly while it exists. Check current pricing in [Cloud Manager](https://cloud.linode.com) before you create it |

Nothing else. No database, no load balancer, no object storage. The agent embeds its
corpus into memory at startup, which takes a few seconds, so there is nothing to
persist.

**You are billed until you delete it.** [Teardown](#teardown) is one command. Do it
when you are done.

## Before you start

- An Akamai Cloud account and an inference key, from [get an API key](../docs/get-an-api-key.md)
- The [Linode CLI](https://techdocs.akamai.com/cloud-computing/docs/install-and-configure-the-cli), configured
- An SSH key at `~/.ssh/id_ed25519.pub`, or run `ssh-keygen -t ed25519`

You do not need Docker on your laptop. The Linode installs it.

## Run it locally first

Worth doing before you spend anything. If you have Docker:

```bash
# from the repo root, not from deploy/
docker build -t workshop-agent -f deploy/Dockerfile .
docker run --rm -p 8000:8000 --env-file .env workshop-agent
```

Then in another terminal:

```bash
curl -s localhost:8000/health

curl -s localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "What is the context limit of qwen3-8-27b?"}'
```

You should get back the answer, `answer_found: true`, and the source files.

## Deploy to a Linode

Fill in the placeholders in `cloud-init.yaml` and hand it to the CLI as user data.

```bash
# 1. Build the user data with your key substituted in.
sed -e "s|__AKAMAI_BASE_URL__|$(grep AKAMAI_BASE_URL .env | cut -d= -f2-)|" \
    -e "s|__AKAMAI_API_KEY__|$(grep AKAMAI_API_KEY .env | cut -d= -f2-)|" \
    -e "s|__REPO_URL__|https://github.com/akamai-developers/akamai-workshop-serverless-inference.git|" \
    deploy/cloud-init.yaml > /tmp/agent-user-data.yaml

# 2. Create the instance.
linode-cli linodes create \
  --label workshop-agent \
  --region us-sea \
  --type g6-nanode-1 \
  --image linode/ubuntu24.04 \
  --authorized_keys "$(cat ~/.ssh/id_ed25519.pub)" \
  --metadata.user_data "$(base64 -i /tmp/agent-user-data.yaml)" \
  --root_pass "$(openssl rand -base64 32)"

# 3. Remove the file holding your key.
rm /tmp/agent-user-data.yaml
```

`/tmp/agent-user-data.yaml` contains your API key in plain text. Delete it as soon as
the instance is created, which is what step 3 does.

Find the address, then wait. First boot installs Docker and builds the image, which
takes a few minutes.

```bash
linode-cli linodes list --label workshop-agent --format id,ipv4,status

IP=$(linode-cli linodes list --label workshop-agent --json | python3 -c 'import json,sys; print(json.load(sys.stdin)[0]["ipv4"][0])')

# Poll until it answers.
until curl -sf "http://$IP:8000/health"; do sleep 20; echo "waiting"; done
```

## Use it

```bash
curl -s "http://$IP:8000/ask" \
  -H 'Content-Type: application/json' \
  -d '{"question": "Which model should I use for tool calling?"}'
```

```json
{
  "answer": "Use qwen3-8-27b for tool calling. Avoid gemma-4-26b-a4b-it.",
  "answer_found": true,
  "sources": ["tool-calling.md", "models.md"]
}
```

## Teardown

```bash
linode-cli linodes delete $(linode-cli linodes list --label workshop-agent --text --no-headers --format id)
```

Confirm it is gone, because this is the step that stops the billing:

```bash
linode-cli linodes list --format id,label,status
```

## What this is and is not

It is a working example of the shape: inference key on the server, agent behind an
HTTP endpoint, no state to manage.

It is not production. There is no TLS, so traffic is plain HTTP. There is no
authentication, so anyone who finds the address can spend your inference budget, and
the firewall leaves port 8000 open to the world. There is no rate limiting and the
corpus is baked into the image at build time.

Before anything real: put it behind TLS, require an API key of your own on `/ask`,
restrict the firewall to the addresses that need it, and move the inference key into
a secrets manager rather than a file on disk.

## Files

| File | What |
|---|---|
| `app/agent.py` | The module 04 agent, as a module. Same two phase design |
| `app/main.py` | HTTP wrapper. Standard library only |
| `app/corpus/` | The documents, embedded at startup |
| `Dockerfile` | Runtime dependencies only, non-root user |
| `cloud-init.yaml` | Installs Docker, builds the image, runs it under systemd |

`app/corpus/` is a copy of `02_Embeddings_and_RAG/assets/sample-docs/`. Replace it
with your own documents and rebuild.
