# Cross-Platform Color Definitions
ifeq ($(OS),Windows_NT)
    # Git Bash Support Only
    ifeq ($(shell echo $$BASH_VERSION 2>/dev/null),)
        $(error This Makefile Only Supports Git Bash On Windows)
    endif
    GREEN=\033[0;32m
    BLUE=\033[0;34m
    YELLOW=\033[1;33m
    RED=\033[0;31m
    NC=\033[0m
else
    # Unix Systems Have Full ANSI Color Support
    GREEN=\033[0;32m
    BLUE=\033[0;34m
    YELLOW=\033[1;33m
    RED=\033[0;31m
    NC=\033[0m
endif

# Default Goal
.DEFAULT_GOAL := help

# Utility Echo And Color Variable Aliases
ECHO_CMD=echo
GREEN_START=${GREEN}
BLUE_START=${BLUE}
YELLOW_START=${YELLOW}
RED_START=${RED}
COLOR_END=${NC}

# Compose Helpers And Sonar Config
COMPOSE_FILE ?= docker-compose.yml
DOCKER_COMPOSE ?= docker compose
PODMAN_COMPOSE ?= podman compose
SONAR_HOST_URL ?= http://localhost:9000
SONAR_PROJECT_KEY ?= InitStack

# Help Target: Show Available Makefile Commands
help:
	@echo ""
	@printf "${BLUE}InitStack Makefile Commands${NC}\n"
	@echo ""
	@printf "${GREEN}General:${NC}\n"
	@echo "  help            - Show This Help Message"
	@echo ""
	@printf "${GREEN}Code Analysis:${NC}\n"
	@echo "  sonar-scan      - Run SonarQube Analysis (Requires SONAR_TOKEN Env Var)"
	@echo "  ruff-check      - Run Ruff Linter In Check Mode"
	@echo "  ruff-lint       - Run Ruff Linter With Auto-Fix"
	@echo ""
	@printf "${GREEN}Podman:${NC}\n"
	@echo "  podman-build    - Build All Services"
	@echo "  podman-up       - Build And Start All Services"
	@echo "  podman-down     - Stop And Remove Services"
	@echo "  podman-restart  - Restart All Services"
	@echo "  podman-clean    - Clean Unused Podman Resources"
	@echo ""
	@printf "${GREEN}Docker:${NC}\n"
	@echo "  docker-build    - Build All Services"
	@echo "  docker-up       - Build And Start All Services"
	@echo "  docker-down     - Stop And Remove Services"
	@echo "  docker-restart  - Restart All Services"
	@echo "  docker-clean    - Clean Unused Docker Resources"
	@echo ""
	@printf "${GREEN}Cleaning:${NC}\n"
	@echo "  clean-all       - Remove Python And Tooling Artifacts"
	@echo ""

# Sonar-Scan Target: Run SonarQube Analysis
sonar-scan:
	@echo ""
	@printf "${YELLOW}Starting Sonarscanner...${NC}\n"
	@[ -n "$$SONAR_TOKEN" ] || (printf "${RED}SONAR_TOKEN Is Not Set. Export SONAR_TOKEN And Re-Run.${NC}\n"; exit 1)
	sonar-scanner \
		-D sonar.host.url=$(SONAR_HOST_URL) \
		-D sonar.projectKey=$(SONAR_PROJECT_KEY) \
		-D sonar.login=$$SONAR_TOKEN
	@printf "${GREEN}SonarQube Scan Completed!${NC}\n"
	@echo ""

# Podman-Build Target: Build All Services
podman-build:
	@echo ""
	@printf "${YELLOW}Building All Services...${NC}\n"
	$(PODMAN_COMPOSE) -f $(COMPOSE_FILE) build --detach
	@printf "${GREEN}Services Built Successfully!${NC}\n"
	@echo ""

# Podman-Up Target: Build And Start All Services
podman-up:
	@echo ""
	@printf "${YELLOW}Building And Starting Services...${NC}\n"
	$(PODMAN_COMPOSE) -f $(COMPOSE_FILE) up -d --build
	@printf "${GREEN}Services Built And Started Successfully!${NC}\n"
	@echo ""

# Podman-Down Target: Stop And Remove Services
podman-down:
	@echo ""
	@printf "${YELLOW}Stopping And Removing Services...${NC}\n"
	$(PODMAN_COMPOSE) -f $(COMPOSE_FILE) down --remove-orphans
	@printf "${GREEN}Services Stopped And Removed Successfully!${NC}\n"
	@echo ""

# Podman-Restart Target: Restart All Services
podman-restart:
	@echo ""
	@printf "${YELLOW}Restarting Services...${NC}\n"
	$(PODMAN_COMPOSE) -f $(COMPOSE_FILE) restart
	@printf "${GREEN}Services Restarted Successfully!${NC}\n"
	@echo ""

# Podman-Clean Target: Prune Unused Podman Resources
podman-clean:
	@echo ""
	@printf "${YELLOW}Cleaning Unused Podman Resources...${NC}\n"
	podman system prune -f --filter "until=24h"
	podman builder prune -f
	@printf "${GREEN}Podman Resources Cleaned Successfully!${NC}\n"
	@echo ""

# Docker-Build Target: Build All Services With Docker
docker-build:
	@echo ""
	@printf "${YELLOW}Building All Services With Docker...${NC}\n"
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) build
	@printf "${GREEN}Services Built Successfully With Docker!${NC}\n"
	@echo ""

# Docker-Up Target: Build And Start All Services With Docker
docker-up:
	@echo ""
	@printf "${YELLOW}Building And Starting Services With Docker...${NC}\n"
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up -d --build
	@printf "${GREEN}Services Built And Started Successfully With Docker!${NC}\n"
	@echo ""

# Docker-Down Target: Stop And Remove Services With Docker
docker-down:
	@echo ""
	@printf "${YELLOW}Stopping And Removing Services With Docker...${NC}\n"
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) down --remove-orphans
	@printf "${GREEN}Services Stopped And Removed Successfully With Docker!${NC}\n"
	@echo ""

# Docker-Restart Target: Restart Services With Docker
docker-restart:
	@echo ""
	@printf "${YELLOW}Restarting Services With Docker...${NC}\n"
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) restart
	@printf "${GREEN}Services Restarted Successfully With Docker!${NC}\n"
	@echo ""

# Docker-Clean Target: Prune Unused Docker Resources
docker-clean:
	@echo ""
	@printf "${YELLOW}Cleaning Unused Docker Resources...${NC}\n"
	docker system prune -f --filter "until=24h"
	docker builder prune -f
	@printf "${GREEN}Docker Resources Cleaned Successfully!${NC}\n"
	@echo ""

# Clean-All Target: Remove Python, Tooling, Celery, And Coverage Artifacts
clean-all:
	@echo ""
	@printf "${YELLOW}Cleaning All Python And Tooling Artifacts...${NC}\n"
	find . -type d -name 'build' -prune -exec rm -rf {} +
	find . -type d -name 'dist' -prune -exec rm -rf {} +
	find . -type d -name 'sdist' -prune -exec rm -rf {} +
	find . -type d -name 'wheels' -prune -exec rm -rf {} +
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} +
	find . -type d -name 'pip-wheel-metadata' -prune -exec rm -rf {} +
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	find . -type d -name '.ruff_cache' -prune -exec rm -rf {} +
	find . -type d -name '.tox' -prune -exec rm -rf {} +
	find . -type d -name '.nox' -prune -exec rm -rf {} +
	find . -type d -name '.cache' -prune -exec rm -rf {} +
	find . -type d -name 'htmlcov' -prune -exec rm -rf {} +
	find . -type d -name '.scannerwork' -prune -exec rm -rf {} +
	find . -type f -name '.coverage' -exec rm -f {} \;
	find . -type f -name '.coverage.*' -delete
	find . -type f -name 'coverage.xml' -delete
	find . -type d -name 'coverage' -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name 'celery.pid' -delete
	find . -type f -name 'celerybeat.pid' -delete
	find . -type f -name 'celerybeat-schedule' -delete
	find . -type f -name 'celerybeat-schedule.db' -delete
	find . -type f -name 'celerybeat-schedule.*' -delete
	find . -type d -name 'celerybeat-schedule' -prune -exec rm -rf {} +
	find . -type f -name 'flower.pid' -delete
	@printf "${GREEN}Cleanup Completed Successfully!${NC}\n"
	@echo ""

# Ruff-Check Target: Run Ruff Linter In Check Mode
ruff-check:
	@echo ""
	@printf "${YELLOW}Running Ruff Linter In Check Mode...${NC}\n"
	ruff check .
	@printf "${GREEN}Ruff Check Completed!${NC}\n"
	@echo ""

# Ruff-Lint Target: Run Ruff Linter With Auto-Fix
ruff-lint:
	@echo ""
	@printf "${YELLOW}Running Ruff Linter With Auto-Fix...${NC}\n"
	ruff check --fix .
	@printf "${GREEN}Ruff Lint Completed!${NC}\n"
	@echo ""

# Phony Targets Declaration
.PHONY: help sonar-scan ruff-check ruff-lint clean-all \
	podman-build podman-up podman-restart podman-clean \
	podman-down \
	docker-build docker-up docker-restart docker-clean docker-down
