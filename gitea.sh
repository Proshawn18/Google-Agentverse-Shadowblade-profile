#!/bin/bash

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# --- Gitea Instance Settings ---
GITEA_CONTAINER_NAME="my-gitea-container"
HOST_GITEA_WEB_PORT=3005
HOST_GITEA_SSH_PORT=2222
GITEA_DATA_PATH="${PWD}/gitea-data"

# --- Gitea MCP Instance Settings ---
MCP_CONTAINER_NAME="my-gitea-mcp-container"
HOST_MCP_WEB_PORT=8085
MCP_IMAGE="gitea/gitea-mcp-server:0.3.0"

# --- Shared Settings ---
DOCKER_NETWORK_NAME="gitea-network"

# --- Admin User (used for token generation) ---
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
ADMIN_EMAIL="admin@example.com"

# --- Regular User ---
NEW_USER="dev"
NEW_USER_PASSWORD="dev"
NEW_USER_EMAIL="dev@example.com"

# ==============================================================================
# SCRIPT LOGIC
# ==============================================================================

echo " Gitea & Gitea-MCP (Hybrid Config) Smart Setup Script"
echo "--------------------------------------------------------"
echo

# --- Preliminary Check: Ensure Docker Daemon is Running ---
echo "STEP 0: Checking if Docker daemon is running..."
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker daemon is not running. Please start Docker and run the script again."
    exit 1
fi
echo "--> Docker daemon is available."
echo

# --- Step 1: Network & Gitea Container Setup ---
echo "STEP 1: Checking Gitea container status..."

# Check if Gitea container is currently running
if [ "$(docker ps -q -f name=^/${GITEA_CONTAINER_NAME}$)" ]; then
    echo "--> Gitea container '${GITEA_CONTAINER_NAME}' is already running. Skipping its setup."
else
    echo "--> Gitea container not running. Starting setup..."

    # Clean up only if a stopped container with the same name exists
    if [ "$(docker ps -a -q -f name=^/${GITEA_CONTAINER_NAME}$)" ]; then
        echo "--> Removing stopped container '${GITEA_CONTAINER_NAME}'."
        docker rm "${GITEA_CONTAINER_NAME}" > /dev/null
    fi

    # Create network, silencing error if it already exists
    docker network create "${DOCKER_NETWORK_NAME}" > /dev/null 2>&1 || true

    # Unzip data if applicable
    if [ -f "gitea-data.zip" ] && [ ! -d "${GITEA_DATA_PATH}" ]; then
        echo "--> Found gitea-data.zip. Unzipping..."
        unzip gitea-data.zip
    fi
    mkdir -p "${GITEA_DATA_PATH}"

    # Deploy Gitea Container
    echo "--> Starting the main Gitea container..."
    docker run \
        -d \
        --name "${GITEA_CONTAINER_NAME}" \
        --network "${DOCKER_NETWORK_NAME}" \
        -p "${HOST_GITEA_WEB_PORT}:3000" \
        -p "${HOST_GITEA_SSH_PORT}:22" \
        -v "${GITEA_DATA_PATH}:/data" \
        --restart=always \
        gitea/gitea:latest

    echo "--> Container starting. Waiting for it to create initial files..."
    sleep 15

    # Get public URL for configuration
    if ! command -v cloudshell &> /dev/null; then
        GITEA_ROOT_URL_SETUP="http://localhost:${HOST_GITEA_WEB_PORT}/"
    else
        GITEA_ROOT_URL_SETUP=$(cloudshell get-web-preview-url -p "${HOST_GITEA_WEB_PORT}")
    fi

    # Configure app.ini
    echo "--> Modifying the configuration file inside the container..."
    CONFIG_FILE_PATH="/data/gitea/conf/app.ini"
    docker exec "${GITEA_CONTAINER_NAME}" sed -i "s|^ROOT_URL\s*=\s*.*|ROOT_URL = ${GITEA_ROOT_URL_SETUP}|" "${CONFIG_FILE_PATH}"
    if ! docker exec "${GITEA_CONTAINER_NAME}" grep -q "\[security\]" "${CONFIG_FILE_PATH}"; then
        docker exec "${GITEA_CONTAINER_NAME}" sh -c "echo -e '\n[security]' >> ${CONFIG_FILE_PATH}"
    fi
    docker exec "${GITEA_CONTAINER_NAME}" sed -i "/\[security\]/a INSTALL_LOCK = true" "${CONFIG_FILE_PATH}"

    # Restart Gitea and Wait for Health Check
    echo "--> Restarting Gitea and waiting for it to be ready..."
    docker restart "${GITEA_CONTAINER_NAME}"
    ATTEMPTS=0
    MAX_ATTEMPTS=30
    until [ "$(docker exec "${GITEA_CONTAINER_NAME}" curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/v1/version)" = "200" ]; do
        if [ ${ATTEMPTS} -eq ${MAX_ATTEMPTS} ]; then
            echo "Error: Gitea did not become healthy in time. Check logs with 'docker logs ${GITEA_CONTAINER_NAME}'"
            exit 1
        fi
        ATTEMPTS=$((ATTEMPTS+1))
        printf "."
        sleep 2
    done
    echo " Gitea API is online!"

    # Create Users
    echo "--> Creating Gitea users..."
    docker exec -u git "${GITEA_CONTAINER_NAME}" gitea admin user create --username "${ADMIN_USER}" --password "${ADMIN_PASSWORD}" --email "${ADMIN_EMAIL}" --admin --must-change-password=false || echo "--> Admin user '${ADMIN_USER}' likely already exists."
    docker exec -u git "${GITEA_CONTAINER_NAME}" gitea admin user create --username "${NEW_USER}" --password "${NEW_USER_PASSWORD}" --email "${NEW_USER_EMAIL}" --must-change-password=false || echo "--> Regular user '${NEW_USER}' likely already exists."
fi
echo

# --- Step 2: Gitea-MCP Container Setup ---
echo "STEP 2: Checking Gitea-MCP container status..."

# Check if Gitea-MCP container is currently running
if [ "$(docker ps -q -f name=^/${MCP_CONTAINER_NAME}$)" ]; then
    echo "--> Gitea-MCP container '${MCP_CONTAINER_NAME}' is already running. Skipping its setup."
else
    echo "--> Gitea-MCP container not running. Starting setup..."

    # Clean up only if a stopped container with the same name exists
    if [ "$(docker ps -a -q -f name=^/${MCP_CONTAINER_NAME}$)" ]; then
        echo "--> Removing stopped container '${MCP_CONTAINER_NAME}'."
        docker rm "${MCP_CONTAINER_NAME}" > /dev/null
    fi

    # Generate Access Token for MCP (requires running Gitea)
    echo "--> Generating a unique access token for user '${NEW_USER}'..."
    MCP_TOKEN_NAME="gitea-mcp-token-$(date +%s)"
    GITEA_MCP_TOKEN=$(docker exec -u git "${GITEA_CONTAINER_NAME}" gitea admin user generate-access-token --username "${NEW_USER}" --token-name "${MCP_TOKEN_NAME}" --scopes "all" | awk '{print $NF}' | tr -d '\r')

    if [ -z "$GITEA_MCP_TOKEN" ]; then
        echo "Error: Failed to generate Gitea access token. Please check Gitea logs."
        exit 1
    fi
    echo "--> Successfully generated token."

    # Start Gitea-MCP Container
    echo "--> Starting the Gitea-MCP container..."
    GITEA_INTERNAL_URL="http://${GITEA_CONTAINER_NAME}:3000"
    docker run \
        -d \
        --name "${MCP_CONTAINER_NAME}" \
        --network "${DOCKER_NETWORK_NAME}" \
        -p "${HOST_MCP_WEB_PORT}:8080" \
        --restart=always \
        -e GITEA_ACCESS_TOKEN="${GITEA_MCP_TOKEN}" \
        --entrypoint "/app/gitea-mcp" \
        "${MCP_IMAGE}" \
        -host "${GITEA_INTERNAL_URL}" \
        -transport "sse" \
        -insecure
fi

# --- Final Output ---
# This part runs every time to provide current access information.
echo
echo "--------------------------------------------------------"
echo " SCRIPT COMPLETE! ALL SERVICES SHOULD BE READY."
echo

if ! command -v cloudshell &> /dev/null; then
    GITEA_ROOT_URL="http://localhost:${HOST_GITEA_WEB_PORT}/"
    MCP_ROOT_URL="http://localhost:${HOST_MCP_WEB_PORT}/"
else
    GITEA_ROOT_URL=$(cloudshell get-web-preview-url -p "${HOST_GITEA_WEB_PORT}")
    MCP_ROOT_URL=$(cloudshell get-web-preview-url -p "${HOST_MCP_WEB_PORT}")
fi

echo " >> Main Gitea Web UI: ${GITEA_ROOT_URL}"
echo " >> Gitea-MCP Web UI:  ${MCP_ROOT_URL}"
echo
echo " >> Admin User:        '${ADMIN_USER}' / '${ADMIN_PASSWORD}'"
echo " >> Regular User:      '${NEW_USER}' / '${NEW_USER_PASSWORD}'"
echo
echo " >> Data is stored in: ${GITEA_DATA_PATH}"
echo