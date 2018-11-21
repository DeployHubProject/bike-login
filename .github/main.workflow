workflow "Build and Deploy" {
  on = "push"
  resolves = [
    "Build Docker image",
  ] 
}

# Build

action "Build Docker image" {
  uses = "actions/docker/cli@master"
  args = ["build", "-t", "{repo}", "."]
}


