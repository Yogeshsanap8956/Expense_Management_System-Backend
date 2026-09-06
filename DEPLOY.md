# Oracle Always Free + Cloudflare Tunnel

You run this **on the Oracle VM**. This repo cannot create the Oracle account for you.

## 1. Oracle Cloud (Always Free ARM)

1. Sign up: https://cloud.oracle.com (home region **Mumbai** if offered).
2. Compute → Create instance:
   - Shape: **VM.Standard.A1.Flex** (Ampere), 1 OCPU / 6 GB is enough.
   - Image: Ubuntu 22.04 or 24.04.
   - Networking: assign a public IP; you do **not** need to open 80/443 if you use the tunnel (keep SSH 22 for yourself only).
3. SSH in with the key you downloaded.

## 2. On the VM

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
# log out and back in
git clone https://github.com/Yogeshsanap8956/Expense_Management_System-Backend.git
cd Expense_Management_System-Backend
cp .env.example .env
# edit SECRET_KEY, CORS_ORIGINS (your Cloudflare Pages URL), ADMIN_PASSWORD
mkdir -p data/uploads
docker compose up -d --build api
curl -s http://127.0.0.1:8000/health
```

SQLite and bill photos live in `./data` (survives container rebuilds). Copy `data/` off the VM occasionally.

## 3. Public HTTPS (Cloudflare Zero Trust Tunnel) — recommended

Oracle security lists + Let's Encrypt are extra work. A tunnel gives HTTPS without opening inbound ports.

1. Cloudflare Zero Trust → Networks → Tunnels → Create.
2. Copy the install token into `.env` as `CLOUDFLARE_TUNNEL_TOKEN=...`
3. In the tunnel, Public Hostname:
   - Hostname: `api.yourdomain.com` (or a `*.cfargotunnel.com` hostname)
   - Service: `http://api:8000`
4. On the VM: `docker compose --profile tunnel up -d --build`
5. Set frontend Pages env `VITE_API_BASE=https://api.yourdomain.com` and rebuild Pages.
6. Put that same origin in backend `CORS_ORIGINS`.

## 4. Check

- `https://api.../health` → `{"status":"ok",...}`
- Login from the Pages PWA with demo admin `9999999999` / your `ADMIN_PASSWORD`.
