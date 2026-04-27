🧭 Last updated Tue June 3, 2025
---
# 🐳 Docker System Map
## 🔁 Global Settings
- **Docker Compose Root:** `/Users/tonymacbook2025/Documents/Docker/docker_config`
- **Master** `**.env**` **File:** `/Users/tonymacbook2025/Documents/Docker/docker_config/.env`
## 🔒 Port Security
- **Strategy:** All ports bound to `127.0.0.1`
- **Firewall Status:** macOS firewall ON; Terminal & Warp incoming blocked
- **Exposure Risk:** Localhost-only; services not exposed to LAN or internet
- **Confirmed Secure:** ✅ True
## 📦 Containers
### **n8n**
- **Compose Path:** `/Users/tonymacbook2025/Documents/Docker/docker_config/docker-compose.yml`
- **Env File:** `.env`
- **Image:** `docker.n8n.io/n8nio/n8n:1.94.1`
- **SQLite DB:** `n8n_data/database.sqlite`
- **Cloudflare Tunnel Cred:** `n8n/4210bd78-efb0-4308-851c-20481b44f4ff.json`
- **Config Files:** `config`, `config.yml`
- **Encryption Key:** Stored in `config` and `.env`
- **Auth:** Basic auth - `fulcrumsf@gmail.com`
- **Network:** `unomas`
- **Port:** `5678`
- **URL:** [https://n8n.robottogato.com](https://n8n.robottogato.com/)
volumes:  
- /Users/tonymacbook2025/Documents/Docker/n8n-data:/home/node/.n8n  
- /Users/tonymacbook2025/Documents/Docker/outputs/n8n_outputs:/data/n8n  
- /Users/tonymacbook2025/Documents/Docker/scripts:/data/scripts  
- /Users/tonymacbook2025/Documents/Docker/outputs/mmaudio_outputs:/data/mmaudio  
- /Users/tonymacbook2025/Documents/Docker/outputs/comfyui_outputs:/data/comfyui  
- /var/run/docker.sock:/var/run/docker.sock
### **cloudflared**
- **Image:** `cloudflare/cloudflared:latest`
- **Container Name:** `cloudflared`
- **Command:** `tunnel --no-autoupdate run 4210bd78-efb0-4308-851c-20481b44f4ff`
- **Volumes:**
    
    - `./4210bd78-efb0-4308-851c-20481b44f4ff.json:/etc/cloudflared/creds.json`
    
    - `./config.yml:/etc/cloudflared/config.yml`
    
- **Env File:** `.env`
- **Network:** `unomas`
### **flowise**
- **Image:** `flowiseai/flowise`
- **Python**: 3.12.10
- **Python Path**: /usr/bin/python3
- **Port:** `${FLOWISE_PORT}` (e.g. 3001)
- **Volume:** `/Users/tonymacbook2025/Documents/Docker/flowise-data:/root/.flowise`
- **Networks:** `unomas`
- **Environment:** Uses `.env` values for credentials
### **open-webui**
- **Image:** `ghcr.io/open-webui/open-webui:main`
- **Python**: 3.11.12
- **Python Path**: /usr/local/bin/python3
- **Port:** `3000` (bound to container port 8080)
- **Volume:** `/Users/tonymacbook2025/Documents/Docker/openwebui-data:/app/backend/data`
- **Networks:** `unomas`
### **qdrant**
- **Image:** `qdrant/qdrant`
- **Port:** `6333`
- **Volume:** `/Users/tonymacbook2025/Documents/Docker/qdrant_storage:/qdrant/storage`
- **Networks:** `unomas`
### **postgres**
- **Image:** `postgres:16-alpine`
- **Port:** `5432`
- **Volume:** `/Users/tonymacbook2025/Documents/Docker/postgres_storage:/var/lib/postgresql/data`
- **Env File:** `.env`
- **Networks:** `unomas`
### **mmaudio**
- **Build:** `./mmaudio`
- **Command:** `bash run.sh`
- **Python:** 3.10.17
- **Python Path**: /usr/local/bin/python3
- **Ports:**
    
    - Flask: `127.0.0.1:5001`
    
    - Gradio: `127.0.0.1:7860`
    
- **Volumes:**
    
    - `/Users/tonymacbook2025/Documents/Docker/docker_config/mmaudio/weights:/app/weights`
    
    - `/Users/tonymacbook2025/Documents/Docker/docker_config/mmaudio/ext_weights:/app/ext_weights`
    
    - `/Users/tonymacbook2025/Documents/Docker/outputs/mmaudio_outputs:/app/outputs`
    
    - `/Users/tonymacbook2025/Documents/Docker/docker_config/mmaudio/logs:/app/logs`
    
    - `/tmp/mmaudio_swap:/swap`
    
    - Source code and scripts bound individually (e.g., `app.py`, `run.sh`, etc.)
    
    - `extra_model_paths.yaml:/app/extra_model_paths.yaml`
    
- **Resources:** Limits 12G / Reserved 8G / `shm_size`: 2G / `mem_swappiness`: 60
- **Status:** Working
- **Notes:** Flask API + Gradio UI, HuggingFace model support, auto bootstrap for weights
### **nca-toolkit**
- **Image:** `stephengpope/no-code-architects-toolkit:arm64`
- **Python:** 3.9.22
- **Python Path**: /usr/local/bin/python3
- **Port:** `8080`
- **Environment Variables:**
    
    - `API_KEY`: From 1Password
    
    - `S3_ENDPOINT_URL`: `http://minio:9000`
    
    - `S3_ACCESS_KEY`, `S3_SECRET_KEY`: From 1Password
    
    - `S3_BUCKET_NAME`: `nca-toolkit`
    
    - `S3_REGION`: `us-east-1`
    
    - `POSTGRES_HOST`: `postgres`
    
    - `QDRANT_HOST`: `qdrant`
    
    - `QDRANT_PORT`: `6333`
    
- **Status:** Working
- **Notes:** Supports secure POST to `/v1/s3/upload` → uploads to MinIO
### **baserow**
- **Image:** `baserow/baserow:1.32.5`
- **Python**: 3.11.2
- **Python Path**: /usr/bin/python3
- **Port:** `443`
- **Networks:** `unomas`
- **Volumes:** `baserow_data`, `baserow_static`, `baserow_media` (named volumes)
### **kokoro-tts-cpu**
- **Image:** `ghcr.io/remsky/kokoro-fastapi-cpu:v0.2.2`
- **Python**: 3.10.16
- **Python Path**: /app/.venv/bin/python3
- **Port:** `8880`
- **Volume:** `/Users/tonymacbook2025/Documents/Docker/kokoro-data:/app/data`
- **Networks:** `unomas`
### **minio**
- **Image:** `quay.io/minio/minio`
- **Port:** `9000`, `9001` (console)
- **Volume:** `/Users/tonymacbook2025/Documents/Docker/minio-data:/data`
- **Networks:** `unomas`
### **comfyui**
- **Image:** `comfyui`
- **Python**: 3.10.17
- **Python Path**: /usr/local/bin/python
- **Port:** `8188`
- **Volumes:**
    
    - `/Users/tonymacbook2025/Documents/Docker/ComfyUI/models:/app/models`
    
    - `/Users/tonymacbook2025/Documents/Docker/ComfyUI/custom_nodes_extra:/app/custom_nodes_extra`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/checkpoints:/app/AI_Models/checkpoints`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/clip:/app/AI_Models/clip`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/controlnet:/app/AI_Models/controlnet`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/embeddings:/app/AI_Models/embeddings`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/inpaint:/app/AI_Models/inpaint`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/lora:/app/AI_Models/lora`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/output:/app/AI_Models/output`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/style_models:/app/AI_Models/style_models`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/temp:/app/AI_Models/temp`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/upscalers:/app/AI_Models/upscalers`
    
    - `/Users/tonymacbook2025/Documents/Docker/AI_Models/vae:/app/AI_Models/vae`
    
    - `./extra_model_paths.yaml:/app/extra_model_paths.yaml`
    
- **Status:** Working
- **Notes:** Supports image generation with shared custom model assets
### **puppeteer**
- **Build:** `./puppeteer`
- **Command:** `node index.js`
- **Volumes:**
    
    - `/Users/tonymacbook2025/Documents/Docker/outputs/puppeteer_outputs:/app/outputs`
    
- **Status:** Optional (used for automation)
- **Notes:** Headless puppeteer runs only as needed
  
### saliency-api
- **Build:** ./saliency-api
- **Container_name**: saliency-api
- **Python:3.10-slim**  
    restart: unless-stopped
- **Runs Flask API Servier**: [http://saliency-api:8001/crop](http://saliency-api:8001/crop)
- **Ports**: 8001:8001 # Localhost access
- **Volumes:** ./saliency-api:/app # Mount source code for live edits
### python-service
- **Build:** image: python:3.10-slim
- **Container_name**: python-service
- **Working_dir**: /scripts
- **Command**: tail -f /dev/null
- **Volumes**:  
    - ../scripts:/scripts  
    - ../outputs:/data
- **Ports**: [http://172.22.0.7:5001](http://172.22.0.7:5001/)
  
  
---
## 📝 System Notes
- **Compose Updates:** Always backup before edits; preserve DB engine config (SQLite vs Postgres)
- **n8n Credentials:** Always stored in SQLite
- **Cloudflare:** Secured tunnel, no public access
- **robots.txt:** Not applicable to n8n
- **Auth Reset - Flowise:** Set `FLOWISE_USERNAME`, `FLOWISE_PASSWORD` in `.env`
- **Auth Reset - OpenWebUI:** Edit `webui.db` manually using TablePlus or CLI
- **Upload Test - NCA Toolkit:** Tested `/v1/s3/upload` with URL → verified in `nca-toolkit` bucket
---