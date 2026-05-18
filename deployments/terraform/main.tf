terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

resource "docker_network" "titan_net" {
  name = "titan-net"
}

resource "docker_container" "redis" {
  name  = "titan-redis"
  image = "redis:7-alpine"
  networks_advanced {
    name = docker_network.titan_net.name
  }
}

resource "docker_container" "gateway" {
  name  = "titan-gateway"
  image = "titan-gateway:latest"
  ports {
    internal = 9000
    external = 9000
  }
  networks_advanced {
    name = docker_network.titan_net.name
  }
  depends_on = [docker_container.redis]
}