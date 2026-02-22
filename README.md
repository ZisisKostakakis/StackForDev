# StackForDev

Generate tailored Dockerfiles for development environments — no local language installation required.

![Architecture Diagram](https://raw.githubusercontent.com/ZisisKostakakis/StackForDev/main/images/StackForDev.png)

## Installation

```bash
pip install stackfordev
```

## Usage

```bash
# Interactive mode (prompts for missing options)
stackfordev generate

# Non-interactive
stackfordev generate --language python --stack "Django Stack" --version 3.11

# With extra dependencies
stackfordev generate -l python -s "Data Science Stack" -v 3.11 -e "numpy,pandas,scikit-learn"

# Save to file
stackfordev generate -l go -s "Gin Stack" -v 1.23 --output ./Dockerfile

# Generate offline (no API call)
stackfordev generate -l javascript -s "Express Stack" -v 20 --local

# Raw JSON output
stackfordev generate -l python -s "Flask Stack" -v 3.12 --json
```

## Supported Languages & Stacks

| Language   | Versions         | Stacks |
|------------|------------------|--------|
| Python     | 3.9, 3.10, 3.11, 3.12 | Django Stack, Flask Stack, Data Science Stack, Web Scraping Stack, Machine Learning Stack |
| JavaScript | 18, 20, 22       | Express Stack, React Stack, Vue.js Stack, Node.js API Stack, Full-Stack JavaScript |
| Go         | 1.21, 1.22, 1.23 | Gin Stack, Beego Stack, Web Framework Stack, Microservices Stack, Data Processing Stack |

## Options

```
stackfordev generate [OPTIONS]

  -l, --language TEXT    Programming language (python, javascript, go)
  -s, --stack TEXT       Dependency stack
  -v, --version TEXT     Language version
  -e, --extras TEXT      Comma-separated extra dependencies
  -o, --output PATH      Save Dockerfile to path
  --local                Generate offline without API call
  --json                 Output raw JSON response
  --help                 Show this message and exit.
```

## How It Works

1. Select language, stack, and version (interactively or via flags)
2. The CLI calls the StackForDev API (or generates locally with `--local`)
3. A tailored Dockerfile is returned and displayed (or saved with `--output`)
4. Use the Dockerfile to build a container that acts as a transparent runtime proxy — run `python script.py` inside the container against your volume-mounted files with no local language installation

## Architecture

The backend is an AWS Lambda function (container runtime) behind API Gateway, with S3 storage for generated Dockerfiles. The CLI can also generate Dockerfiles locally without any API call.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT — see [LICENSE](LICENSE) for details.
