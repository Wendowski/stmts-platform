# DreamHost deployment

The new workflow deploys the **static, fictional, read-only web preview** to DreamHost shared hosting. It does not deploy Django, Angular SSR, PostgreSQL, Redis, RabbitMQ, workers, authentication or publication. Native apps are built/distributed separately. The current backend is still a development fixture service, not a production application.

DreamHost shared plans prohibit persistent processes and do not support PostgreSQL. Python being installed does not make the planned Django service/worker architecture available. DreamCompute (or an appropriately provisioned VPS/dedicated server) is the full-stack direction. Managed VPS can run persistent processes/Node, but PostgreSQL and other services still require a supported external service or suitable self-managed host. Full-stack deployment remains a separate infrastructure increment once a target and production runtime configuration exist.

Official references, checked 9 November 2026:
- https://help.dreamhost.com/hc/en-us/articles/214869648-Persistent-processes
- https://help.dreamhost.com/hc/en-us/articles/217141627-Supported-and-unsupported-technologies
- https://help.dreamhost.com/hc/en-us/articles/216661778-Rsync

## Set up the shared preview

1. Push the Git repository to GitHub. No remote is currently configured by this project.
2. Create a dedicated preview subdomain in DreamHost, enable HTTPS, and enable Shell access for its user. Use a dedicated web directory, not an existing production site's directory.
3. In that directory create an empty marker named `.stmts-preview-root`, for example `touch /home/youruser/preview.example.com/.stmts-preview-root`. The workflow refuses to deploy without it. The directory must already exist.
4. Generate a dedicated SSH deploy key. Install its public key for the DreamHost shell user. Verify the server host-key fingerprint through a trusted independent channel before supplying a known_hosts entry; the workflow never disables host verification or trusts ssh-keyscan output automatically.
5. Create a GitHub environment named `dreamhost-preview`, restrict deployments to `main`, and configure any desired reviewers. Configure the values below. After setup, set the repository enable variable to `true`.
6. Run **Deploy DreamHost static preview** from Actions, or push to `main`. Build artifacts are produced even when deployment is disabled. The deployment job verifies the published commit at `deployment.json` after upload.

| Location | Name | Value |
|---|---|---|
| Repository variable | DREAMHOST_DEPLOY_ENABLED | `true` to enable the deploy job; unset builds only |
| Environment variable | DREAMHOST_DEPLOY_PATH | Absolute dedicated directory, e.g. `/home/youruser/preview.example.com` (no trailing slash) |
| Environment variable | DREAMHOST_PREVIEW_URL | HTTPS root URL, e.g. `https://preview.example.com` (no trailing slash) |
| Environment secret | DREAMHOST_SSH_HOST | DreamHost SSH hostname |
| Environment secret | DREAMHOST_SSH_USER | Shell username |
| Environment secret | DREAMHOST_SSH_KEY | Dedicated private deploy key |
| Environment secret | DREAMHOST_KNOWN_HOSTS | Independently verified OpenSSH known_hosts line(s) |

The static preview defaults to the fictional post automatically and keeps the existing development banner. `production` remains the SSR build and excludes development JSON; only the explicitly named `shared-preview` configuration enables this demonstration. The preview has no live API and `/v1` returns unavailable rather than an SPA shell. Deploy at the subdomain root; subdirectory deployment needs explicit base-URL changes.

## Transfers and recovery

Only the compiled browser directory is uploaded; repository files, backend code, .env and server bundles are excluded by construction. SSH verifies host keys. Deploy paths are validated and require the marker. Transfers are serialized, use no `--delete`, upload hashed assets first, then index.html, then deployment.json. This reduces missing-asset windows but is not an atomic release transaction. Old assets remain available for existing tabs; no automatic garbage collection is performed.

To roll back, download a previous successful `dreamhost-preview` artifact from Actions and deploy its complete contents with the same script and credentials, or revert the relevant Git commit and rerun the workflow. The artifact includes .htaccess; preserve hidden files when extracting. A failed post-upload health check does not automatically roll back the site. Keep HTTPS enabled and avoid caching deployment.json/index.html at an additional CDN.

Local verification: `npm --prefix web run build:shared-preview`; `python tests/test_dreamhost_deploy.py`; `bash -n infra/dreamhost/deploy-preview.sh`. Live SSH upload and DreamHost Apache behavior require the actual account configuration and have not been run here.
