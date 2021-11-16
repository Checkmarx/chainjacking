![readme cover image](https://user-images.githubusercontent.com/1287098/142020269-af916c4d-7c66-4893-a030-daa4113e00f4.png)

ChainJacking is a tool to find which of your Go lang direct GitHub dependencies is susceptible to ChainJacking attack. Read more about it [here](https://checkmarx.com/blog/a-new-type-of-supply-chain-attack-could-put-popular-admin-tools-at-risk/)

#### Requirements
- Python 3.6+ and pip
- Go and it's binaries >= 1.13
- GitHub token, to run queries on GitHub API 

#### Installation
```
pip install chainjacking
```

## Using in CI Workflows
ChainJacking can be easily integrated into modern CI workflows to test new code contributions.  


### GitHub Actions

https://user-images.githubusercontent.com/1287098/142009618-5eb5d87c-a001-4536-abf3-c5d06216e1b6.mp4

Example configuration:
```yaml
name: Pull Request

on:
  pull_request

jobs:

  build:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: ChainJacking tool test
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m pip install -q chainjacking
          python -m chainjacking -gt $GITHUB_TOKEN
```


## CLI
ChainJacking module can be run as a CLI tool simply as 
```
python -m chainjacking
```

### CLI Arguments
- `-gt <token>` - GitHub access token, to run queries on GitHub API (required)
- `-p <path>` - Path to scan. (default=current directory)
- `-v` - Verbose output mode
- `-url <url>` - Scan one or more GitHub URLs
- `-f <path>` - Scan one or more GitHub URLs from a file separated by new-line


#### Example: Scan a Go project
navigate your shell into a Go project's directory, and run:
```
python -m chainjacking -gt $GH_TOKEN
```

https://user-images.githubusercontent.com/1287098/142020377-c873716d-c080-418b-8597-f9e08dba3e82.mp4


