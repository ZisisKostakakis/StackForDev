# StackForDev — Project Idea

## The Problem

Setting up a new laptop or onboarding a new team member is time-consuming. Installing the right language version, dependency managers, frameworks, and tooling for each project can take hours and leads to "works on my machine" conflicts.

## The Solution

**One prerequisite: Docker.**

StackForDev generates tailored Docker images for any language/stack combination. The container becomes the dev environment — language runtimes, dependencies, and tooling all live inside it. The developer's project files are volume-mounted so changes are live.

The end goal is **transparent command proxying**:
```bash
# Instead of: python somescript.py  (requires Python installed locally)
stackfordev python somescript.py
# Runs: docker run -v $(pwd):/app stackfordev-python-django python somescript.py
```

No Python on the laptop. No pip. No virtualenv. Just Docker.

## How It Works

1. **User opens the web UI** (SvelteKit frontend) and selects:
   - Programming language (Python, JavaScript, Go, ...)
   - Dependency stack (e.g. "Django Stack", "Data Science Stack")
   - Optional extra dependencies (comma-separated)
   - Language version

2. **Frontend POSTs to the API** (AWS API Gateway → Lambda):
   ```json
   { "config": { "language": "Python", "dependency_stack": "Django Stack", "language_version": "3.11", "extra_dependencies": ["celery"] } }
   ```

3. **Backend generates a Dockerfile** from a template, deduplicates against S3, uploads it, and returns the S3 URL.

4. **User pulls the generated Dockerfile**, builds the image locally, and uses it as their dev container with volume mounts.

5. **(Future)** A CLI wrapper (`stackfordev <command>`) transparently routes commands through the running container.

## Architecture

```
[Browser UI]  →  SvelteKit (StackForDev-FrontEnd)
                      ↓ POST /generate-dockerfile
              [API Gateway + API Key]
                      ↓
              [AWS Lambda (Python)]
                      ↓
              [DockerfileGenerator]  →  [S3 Bucket]
                                           ↓
                                    Returns Dockerfile URL
```

**Repos:**
- `StackForDev` — Python Lambda backend + Terraform IaC
- `StackForDev-FrontEnd` — SvelteKit web UI

## Supported Stacks (Current)

| Language   | Stacks |
|------------|--------|
| Python     | Django, Flask, Data Science, Web Scraping, Machine Learning |
| JavaScript | Express, React, Vue.js, Node.js API, Full-Stack JS |
| Go         | Gin, Beego, Web Framework, Microservices, Data Processing |

## Competitive Landscape

| Tool | Requires | Limitation |
|------|----------|------------|
| DevContainers | VS Code | IDE-coupled |
| GitHub Codespaces | GitHub account + internet | Cloud-only |
| Distrobox | Linux | OS-locked |
| nix-shell | Nix knowledge | Steep learning curve |
| **StackForDev** | Docker | — |

**Edge:** IDE-agnostic, single prerequisite, no cloud account needed after image generation.

## Roadmap

- [ ] CLI tool (`stackfordev <cmd>`) for transparent command proxying
- [ ] More language templates (Ruby, Rust, Java, PHP)
- [ ] Version picker UI on frontend
- [ ] `docker run` one-liner output alongside the Dockerfile
- [ ] Persistent container mode (avoid cold-start per command)
- [ ] Local caching of generated images
